Rust RwLock and Mutex Performance Oddities
==========================================

Recently I have been working on Rust datastructures once again. In the process I wanted to test
how my work performed compared to a standard library RwLock and Mutex. On my home laptop the
RwLock was 5 times faster, the Mutex 2 times faster than my work.

So checking out my code on my workplace workstation and running my bench marks I noticed the
Mutex was the same - 2 times faster. However, the RwLock was 4000 times slower.

What's a RwLock and Mutex anyway?
---------------------------------

In a multithreaded application, it's important that data that needs to be shared between threads
is consistent when accessed. This consistency is not just logical consistency of the data, but
affects hardware consistency of the memory in cache. As a simple example, let's examine an update
to a bank account done by two threads:

::

    acc = 10
    deposit = 3
    withdrawl = 5

    [ Thread A ]            [ Thread B ]
    acc = load_balance()    acc = load_balance()
    acc = acc + deposit     acc = acc - withdrawl
    store_balance(acc)      store_balance(acc)

What will the account balance be at the end? The answer is "it depends". Because threads are
working in parallel these operations could happen:

* At the same time
* Interleaved (various possibilities)
* Sequentially

This isn't very healthy for our bank account. We could lose our deposit, or have invalid data.
Valid outcomes at the end are that acc could be 13, 5, 8. Only one of these is correct.

A mutex protects our data in multiple ways. It provides hardware consistency operations so that
our cpus cache state is valid. It also allows only a single thread inside of the mutex at a time
so we can linearise operations. Mutex comes from the word "Mutual Exclusion" after all.

So our example with a mutex now becomes:

::

    acc = 10
    deposit = 3
    withdrawl = 5

    [ Thread A ]            [ Thread B ]
    mutex.lock()            mutex.lock()
    acc = load_balance()    acc = load_balance()
    acc = acc + deposit     acc = acc - withdrawl
    store_balance(acc)      store_balance(acc)
    mutex.unlock()          mutex.unlock()

Now only one thread will access our account at a time: The other thread will block until the mutex
is released.

A RwLock is a special extension to this pattern. Where a mutex guarantees single access to the
data in a read and write form, a RwLock (Read Write Lock) allows multiple read-only views OR
single read and writer access. Importantly when a writer wants to access the lock, all readers
must complete their work and "drain". Once the write is complete readers can begin again.
So you can imagine it as:

::

    Time ->

    T1: -- read --> x
    T3:     -- read --> x                x -- read -->
    T3:     -- read --> x                x -- read -->
    T4:                   | -- write -- |
    T5:                                  x -- read -->


Test Case for the RwLock
------------------------

My test case is simple. Given a set of 12 threads, we spawn:

* 8 readers. Take a read lock, read the value, release the read lock. If the value == target then stop the thread.
* 4 writers. Take a write lock, read the value. Add one and write. Continue until value == target then stop.

Other conditions:

* The test code is identical between Mutex/RwLock (beside the locking costruct)
* --release is used for compiler optimisations
* The test hardware is as close as possible (i7 quad core)
* The tests are run multiple time to construct averages of the performance

The idea being that X target number of writes must occur, while many readers contend as fast
as possible on the read. We are pressuring the system of choice between "many readers getting
to read fast" or "writers getting priority to drain/block readers".

On OSX given a target of 500 writes, this was able to complete in 0.01 second for the RwLock. (MBP 2011, 2.8GHz)

On Linux given a target of 500 writes, this completed in 42 seconds. This is a 4000 times difference. (i7-7700 CPU @ 3.60GHz)

All things considered the Linux machine should have an advantage - it's a desktop processor, of a newer generation, and much faster
clock speed. So why is the RwLock performance so much different on Linux?

To the source code!
-------------------

Examining the `Rust source code <https://github.com/rust-lang/rust/blob/master/src/libstd/sys/unix/rwlock.rs>`_ ,
many OS primitives come from libc. This is because they require OS support to function. RwLock is an example of this
as is mutex and many more.
The unix implementation for Rust consumes the pthread_rwlock primitive. This means we need to read man
pages to understand the details of each.

OSX uses FreeBSD userland components, so we can assume they follow the BSD man pages. In the
FreeBSD man page for pthread_rwlock_rdlock we see:

::

    IMPLEMENTATION NOTES

     To prevent writer starvation, writers are favored over readers.

Linux however, uses different constructs. Looking at the Linux man page:

::

    PTHREAD_RWLOCK_PREFER_READER_NP
      This is the default.  A thread may hold multiple read locks;
      that is, read locks are recursive.  According to The Single
      Unix Specification, the behavior is unspecified when a reader
      tries to place a lock, and there is no write lock but writers
      are waiting.  Giving preference to the reader, as is set by
      PTHREAD_RWLOCK_PREFER_READER_NP, implies that the reader will
      receive the requested lock, even if a writer is waiting.  As
      long as there are readers, the writer will be starved.


Reader vs Writer Preferences?
-----------------------------

Due to the policy of a RwLock having multiple readers OR a single writer, a preference
is given to one or the other. The preference basically boils down to the choice of:

* Do you respond to write requests and have new readers block?
* Do you favour readers but let writers block until reads are complete?

The difference is that on a *read* heavy workload, a write will continue to be delayed so that
readers can begin *and* complete (up until some threshold of time). However, on a writer
focused workload, you allow readers to stall so that writes can complete sooner.

On Linux, they choose a reader preference. On OSX/BSD they choose a writer preference.

Because our test is about how fast can a target of write operations complete, the writer
preference of BSD/OSX causes this test to be much faster. Our readers still "read" but are
giving way to writers, which completes our test sooner.

However, the linux "reader favour" policy means that our readers (designed for creating
conteniton) are allowed to skip the queue and block writers. This causes our writers to starve. Because the test
is only concerned with writer completion, the result is (correctly) showing our writers are
heavily delayed - even though many more readers are completing.

If we were to track the number of reads that completed, I am sure we would see a large factor
of difference where Linux has allow many more readers to complete than the OSX version.

Linux pthread_rwlock does allow you to change this policy (PTHREAD_RWLOCK_PREFER_WRITER_NP)
but this isn't exposed via Rust. This means today, you accept (and trust) the OS default. Rust
is just unaware at compile time and run time that such a different policy exists.

Conclusion
----------

Rust like any language consumes operating system primitives. Every OS implements these differently
and these differences in OS policy can cause real performance differences in applications between
development and production.

It's well worth understanding the constructions used in programming languages and how they
affect the performance of your application - and the decisions behind those tradeoffs.

This isn't meant to say "don't use RwLock in Rust on Linux". This is meant to say "choose it
when it makes sense - on read heavy loads, understanding writers will delay". For my project
(A copy on write cell) I will likely conditionally compile rwlock on osx, but mutex on linux
as I require a writer favoured behaviour. There are certainly applications that will benefit
from the reader priority in linux (especially if there is low writer volume and low penalty
to delayed writes).


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
