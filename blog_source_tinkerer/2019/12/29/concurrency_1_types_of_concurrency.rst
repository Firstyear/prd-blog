Concurrency 1: Types of Concurrency
===================================

I want to explain different types of concurrent datastructures, so that we can explore their
properties and when or why they might be useful.

As our computer systems become increasingly parallel and asynchronous, it's important that our
applications are able to work in these environments effectively. Languages like Rust help us to
ensure our concurrent structures are safe.

CPU Memory Model Crash Course
-----------------------------

In no way is this a thorough, complete, or 100% accurate representation of CPU memory. My goal
is to give you a quick brief on how it works. I highly recommend you read `"what every programmer should know about memory" <https://people.freebsd.org/~lstewart/articles/cpumemory.pdf>`_
if you want to learn more.

In a CPU we have a view of a memory space. That could be in the order of KB to TB. But it's a single
coherent view of that space.

Of course, over time systems and people have demanded more and more performance. But we also have
languages like C, that won't change from their view of a system as a single memory space, or change
how they work. Of course, it turns out `C is not a low level language <https://queue.acm.org/detail.cfm?id=3212479>`_
but we like to convince ourselves it is.

To keep working with C and others, CPU's have acquired cache's that are transparent to the operation
of the memory. You have no control of what is - or is not - in the cache. It "just happens" asynchronously.
This is exactly why spectre and meltdown happened (and will continue to happen) because these
async behaviours will always have the observable effect of making your CPU faster. Who knew!

Anyway, for this to work, each CPU has multiple layers of cache. At L3 the cache is shared with
all the cores on the die. At L1 it is "per cpu".

Of course it's a single view into memory. So if address 0xff is in the CPU cache of core 1, and
also in cache of core 2, what happens? Well it's supported! Caches between cores are kept in sync
via a state machine called MESI. These states are:

* Exclusive - The cache is the only owner of this value, and it is unchanged.
* Modified - The cache is the only owner of this value, and it has been changed.
* Invalid - The cache holds this value but another cache has changed it.
* Shared - This cache and maybe others are viewing this valid value.

To gloss very heavily over this topic, we want to avoid invaild. Why? That means two cpus are
*contending* for the value, causing many attempts to keep each other in check. These contentions
cause CPU's to slow down.

We want values to either be in E/M or S. In shared, many cpu's are able to read the value at maximum
speed, all the time. In E/M, we know only this cpu is changing the value.

This cache coherency is also why mutexes and locks exist - they issue the needed CPU commands
to keep the caches in the correct states for the memory we are accessing.

Keep in mind Rust's variables are immutable, and able to share between threads, or mutable and
single thread only. Sound familar? Rust is helping with concurrency by keeping our variables
in the fastest possible cache states.

Data Structures
---------------

We use data structures in programming to help improve behaviours of certain tasks. Maybe we need
to find values quicker, sort contents, or search for things. Data Structures are a key element
of modern computer performance.

However most data structures are not thread safe. This means only a single CPU can access or change
them at a time. Why? Because if a second read them, due to cache-differences in content the second
CPU may see an invalid datastructure, leading to undefined behaviour.

Mutexes can be used, but this causes other CPU's to stall and wait for the mutex to be released -
not really what we want on our system. We want every CPU to be able to process data without stopping!

Thread Safe Datastructures
--------------------------

There exist many types of thread safe datastructures that can work on parallel systems. They often
avoid mutexes to try and keep CPU's moving as fast as possible, relying on special atomic cpu operations
to keep all the threads in sync.

Multiple classes of these structures exist, which have different properties.


Mutex
-----

I have mentioned these already, but it's worth specifying the properties of a mutex. A mutex
is a system where a single CPU exists in the mutex. It becomes one "reader/writer" and all
other CPU's must wait until the mutex is released by the current CPU holder.

Read Write Lock
---------------

Often called RWlock, these allow one writer OR multiple parallel readers. If a reader is reading
then a writer request is delayed until the readers complete. If a writer is changing data, all
new reads are blocked. All readers will always be reading the same data.

These are great for highly concurrent systems provided your data changes infrequently. If you have
a writer changing data a lot, this causes your readers to be continually blocking. The delay on
the writer is also high due to a potentially high amount of parallel readers that need to exit.

Lock Free
---------

Lock free is a common (and popular) datastructue type. These are structures that don't use a mutex
at all, and can have multiple readers *and* multiple writers at the same time.

The most common and popular structure for lock free is queues, where many CPUs can append items
and many can dequeue at the same time. There are also a number of lock free sets which can be updated
in the same way.

An interesting part of lock free is that all CPU's are working on the same set - if CPU 1 reads
a value, then CPU 2 writes the same value, the next read from CPU 1 will show the new value. This
is because these structures aren't transactional - lock free, but not transactional. There are some
times where this is really useful as a property when you need a single view of the world between
all threads, and your program can tolerate data changing between reads.

Wait Free
---------

This is a specialisation of lock free, where the reader/writer has guaranteed characteristics about
the time they will wait to read or write data. This is very detailed and subtle, only affecting
real time systems that have strict deadline and performance requirements.

Concurrently Readable
---------------------

In between all of these is a type of structure called concurrently readable. A concurrently readable
structure allows one writer *and* multiple parallel readers. An interesting property is that when
the reader "begins" to read, the view for that reader is guaranteed not to change until the reader
completes. This means that the structure is transactional.

An example being if CPU 1 reads a value, and CPU 2 writes to it, CPU 1 would NOT see the change from
CPU 2 - it's outside of the read transaction!

In this way there are a lot of read-only immutable data, and one writer mutating and changing
things ... sounds familar? It's very close to how our CPU's cache work!

These structures also naturally lend themself well to long processing or database systems where you
need transactional (ACID) properties. In fact some databases use concurrent readable structures
to achieve ACID semantics.


If it's not obvious - concurrent readability is where my interest lies, and in the next post
I'll discuss some specific concurrently readable structures that exist today, and ideas for
future structures.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
