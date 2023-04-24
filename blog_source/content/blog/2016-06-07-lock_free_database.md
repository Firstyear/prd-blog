+++
title = "lock free database"
date = 2016-06-07
slug = "2016-06-07-lock_free_database"
# This is relative to the root!
aliases = [ "2016/06/07/lock_free_database.html", "blog/html/2016/06/07/lock_free_database.html" ]
+++
# lock free database

While discussing some ideas with the owner of
[liblfds](http://liblfds.org/) I was thinking about some of the issues
in the database of Directory Server, and other ldap products. What slows
us down?

## Why are locks slow?

It\'s a good idea to read [this
article](http://liblfds.org/mediawiki/index.php?title=Article:Memory_Barriers)
to understand Memory Barriers in a cpu.

When you think about the way a mutex has to work, it takes advantage of
these primitives to create a full barrier, and do the compare and
exchange to set the value of the lock, and to guarantee the other memory
is synced to our core. This is pretty full on for cpu time, and in
reverse, to unlock you have to basically do the same again. That\'s a
lot of operations! (NOTE: You do a load barrier on the way in to the
lock, and a store barrier on the unlock. The end result is the full
barrier over the set of operations as a whole.)

Lock contenion is really the killer though. If every thread is blocked
on a single lock, they cannot progress. Given the cost of our lock, if
we are stalling our threads behind a lock, we have cpus waiting to do
nothing during this process. The OS scheduler helps mask this by waking
and running another thread, but eventually contenion will win out.

If we bring NUMA into the picture, our mutex may be in a different NUMA
region than the thread requesting the lock. This adds an impact to
latency as well!

We need to try and avoid these operations if we can, to increase
performance.

## BDB

Currently, BDB basically serialises all operations over a set of locks
to access to the data.

This means that a set of readers and writers will execute *in order*,
with only one at a time.

Not so great for performance, but great for consistency. We are hit hard
by our locks, and we have issues with NUMA, especially accessing the
page caches, as we regularly have to cross NUMA regions to access the
required memory.

## LMDB

LMDB does somewhat better. This is based on a COW btree, with reference
counting to accessors. There are still locks scattered through out the
tree, which will have an impact however.

But, LMDB can establish a read only transaction, of which there can be
many, and a serialised, single write transaction. These still suffer
from synchronisation of the locks across cores, because LMDB basically
allows direct memory access to the tree.

As well, NUMA is an issue again: Across a NUMA region, if you access the
DB over one of the boundaries, you will suffer a large performance hit.
LMDB tries to offset this through it\'s use of the VFS for page cache.
However that\'s just passing the buck. You now rely on the kernel to
have the memory pages needed in the correct region, and that\'s not
guaranteed.

## What can we do?

We need to think about how CPU and RAM works. We need to avoid crossing
NUMA regions, and we need to avoid costly CPU instructions and
behaviour. We need to avoid contenion on single locks no matter where
they may be. We need our program to act less like a human reasons about
it, and more like how a CPU works: Asynchronously, and with
interprocessor communication. When our program behaviour matches the
hardware, we can achieve better performance, and correctness.

In the testing of lfds, the lfds author has found that Single Thread,
accessing memory within one NUMA region, and without locks, always wins
by operation count. This is compared to even lock free behaviours across
many cores.

This is because in a single thread we don\'t *need* to lock data. It has
exclusive access, and does not need to contend with other cores. No
mutexes needed, no barriers needed.

So we must minimise our interprocessor traversal if we can, but we want
to keep data into a single CPU region. Our data should ideally be in the
NUMA region we want to access it in, in the end.

## Async db

*Disclaimer*: This is just an idea, and still needs polish.

We run our database, (be it lmdb, bdb, or something new) in a single
thread, on one cpu. Now that we are within a single CPU, we can dispense
all locking mechanisms, and still have a guarantee that the view of the
data is correct.

Every thread of our application would then be \"pinned\" to a NUMA
region and core, to ensure that they don\'t move.

We would then use the [single producer, single consumer bounded
queue](http://liblfds.org/mediawiki/index.php?title=r7.1.0:Queue_%28bounded,_single_producer,_single_consumer%29)
from this article. Each NUMA region would establish one of these queues
to the database thread. The bounding size is the number of working
threads on the system. Each queue would be thread max for the bound,
even though there are multiple regions. This is because there may be an
unequal distribution of threads to regions, so we may have all threads
in one region.

Now, our database thread can essentially round robbin, and dequeue
requests as they enter. We can use the DB without locks, because we are
serialised within one thread. The results would then be placed back into
the queue, and the requestor of the operation would be able to examine
the results. Because we put the results into the memory space of the
requestor, we pay the NUMA price once as we retrieve the result, rather
than repeatedly like we do now where we access various caches and
allocations.

Why would this be better?

-   We have dispensed completely with ALL mutexes and locks. The queue
    in liblfds is fast. Amazingly fast. Seriously, look at [these
    benchmarks](http://liblfds.org/mediawiki/index.php?title=r7.1.0:Queue_%28unbounded,_many_producer,_many_consumer%29#Benchmark_Results_and_Analysis).
    And that\'s on the many many queue, which is theoretically slower
    than the single single bounded queue.
-   We keep consistency within the database. Because we only have one
    thread acting on the data, we have gained serialisation implicitly.
-   We keep data in the NUMA regions where it needs to be. Rather than
    having a large cache that spans potentially many NUMA regions, we
    get data as we need, and put it into the numa region of the DB
    thread.
-   Because the data is within a single thread, we take advantage of the
    cpu cache heavily, without the expense of the cpu caches to the
    other threads. Minimising page evictions and inclusions is a good
    thing.

There are many other potential ways to improve this:

-   We could potentially cache entries into the NUMA region. When a
    search is requested, provided the serial of the entry hasn\'t been
    advanced, the entry still within our NUMA region is valid. This
    prevents more moving between NUMA regions, again yielding a benefit.
    It would basically be:


```
    Thread A                              Thread DB
    Queue a read transaction with
    thread ID X               -->
                              <--  Open the transaction, and stash

    Queue a search for set of IDs -->
                                    Dequeue search request
                                    Build ID set
                                    With each ID, pair to the "db version" of the entry. IE USN style.
                              <--   Return ID set to queue
    Examine the local cache.
    if ID not in local cache || 
    not USN matches entry in cache
        Add Id to "retrieve set"
    Queue a retrieve request      -->
                                    Dequeue the retrieve request
                                    Copy the requested IDs / entries to Thread A
                              <--   Return

    Queue a transaction complete  -->
                              <--   Done
```


## Acknowledgement

Huge thank you to Winterflaw, the author of LibLFDS for discussing these
ideas, his future review of this idea, and for teaching me many of these
concepts.

