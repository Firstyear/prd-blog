Concurrency 2: Concurrently Readable Structures
===============================================

In this post, I'll discuss concurrently readable datastructures that exist, and ideas
for future structures. Please note, this post is an inprogress design, and may be altered
in the future.

Before you start, make sure you have `read part 1 <../concurrency_1_types_of_concurrency.html>`_

Concurrent Cell
---------------

The simplest form of concurrently readable structure is a concurrent cell. This is equivalent to
a read-write lock, but has concurrently readable properties instead. The key mechanism to enable
this is that when the writer begins, it clones the data before writing it. We trade more memory
usage for a gain in concurrency.

To see an implementation, see my `rust crate, concread <https://crates.io/crates/concread>`_

Concurrent Tree
---------------

The concurrent cell is good for small data, but a larger structure - like a tree - may take too
long to clone on each write. A good estimate is that if your data in the cell is larger than about
512 bytes, you likely want a concurrent tree instead.

In a concurrent tree, only the *branches* involved in the operation are cloned. Imagine the following
tree:

::

             --- root 1 ---
            /               \
        branch 1         branch 2
        /     \         /        \
    leaf 1   leaf 2  leaf 3    leaf 4

When we attempt to change a value in leaf 4 we copy it before we begin.

::

          ---------------------------
         /   --- root 1 ---          \-- root 2
         v  /               \                \
        branch 1         branch 2            branch 2(c)
        /     \         /        \           /    \
    leaf 1   leaf 2  leaf 3    leaf 4        |    leaf 4(c)
                        ^                    |
                        \-------------------/



In the process the pointers from the new root 2 to branch 1 are maintained. branch 2(c) also
maintains a pointer to leaf 3.

This means that in this example only 3/7 nodes are copied, saving a lot of cloning. As your tree
grows this saves a lot of work. Consider a tree with node-widths of 7 pointers and at height level
5. Assuming perfect layout, you only need to clone 5/~16000 nodes. A huge saving in memory copy!

The interesting part is a reader of root 1, also is unaffected by the changes to root 2  - the tree
from root 1 hasn't been changed, as all it's pointers and nodes are still valid.

When any reader of root 1 ends, we clean up all the nodes it pointed to that no longer are needed
by root 2 (this can be done with atomic reference counting, or garbage lists in transactions).

::

             --- root 2 ---
            /               \
        branch 1         branch 2(c)
        /     \         /        \
    leaf 1   leaf 2  leaf 3    leaf 4(c)


It is through this copy-on-write (also called multi view concurrency control) that we achieve
concurrent readability in the tree.

This is really excellent for databases where you have in memory structures that work in parallel
to the database transactions. In kanidm an example is the in-memory schema that is used at run time
but loaded from the database. They require transactional behaviours to match the database, and ACID
properties so that readers of a past transaction have the "matched" schema in memory.

Future Idea - Concurrent Cache
------------------------------

A design I have floated in my head is a concurrently readable cache - it should have the same
transactional properties as a concurrently readable structure - one writer, multiple readers
with consistent views of the data. As well it should support rollbacks if a writer fails.

This scheme should work with any cache type - LRU, LRU2Q, LFU. I plan to use ARC however.

ARC was popularised by ZFS - ARC is not specific to ZFS, it's a strategy for cache replacement.

ARC is a combination of an LRU and LFU with a set of ghost lists and a weighting factor. When an
entry is "missed" it's inserted to the LRU. When it's accessed from the LRU a second time, it moves
to the LFU.

When entries are evicted from the LRU or LFU they are added to the ghost list. When a cache miss
occurs, the ghost list is consulted. If the entry "would have been" in the LRU, but was not, the
LRU grows and the LFU shrinks. If the item "would have been" in the LFU but was not, the LFU is expanded.

This causes ARC to be self tuning to your workload, as well as balancing "high frequency" and "high
locality" operations.

A major problem though is ARC is not designed for concurrency - LFU/LRU rely on double linked lists
which is *very* much something that only a single thread can modify safely.

How to make ARC concurrent
--------------------------

To make this concurrent, I think it's important to specify the goals.

* Readers should be able to read and find entries in the cache
* If a reader locates a missing entry it must be able to load it from the database
* The reader should be able to send loaded entries to the cache so they can be used.
* Reader access metrics should be acknowledged by the cache.
* Multiple reader generations should exist
* A writer should be able to load entries to the cache
* A writer should be able to modify an entry of the cache without affecting readers
* Writers should be able to be rolled back with low penalty

There are a lot of places to draw inspiration from, and I don't think I can list - or remember them
all.

My current "work in progress" is that we use a concurrently readable pair of trees to store the LRU
and LFU. These trees are able to be read by readers, and a writer can concurrently write changes.

The ghost lists of the LRU/LFU are maintained single thread by the writer. The linked lists for both
are also single threaded and use key-references from the main trees to maintain themselves. The writer
maintains the recv end of an mpsc queue. Finally a writer has an always-incrementing transaction
id associated.

A reader when initiated has access to the writer of the queue and the transaction id of the writer
that created this generation. The reader has a an empty hash map.

Modification to ARC
-------------------

A modification is that we need to retain the transaction id's related to items. This means the
LRU and LFU contain:

::

    type Txid: usize;

    struct ARC<K, Value<V>> {
        lru: LRU<K, Value<V>>,
        lfu: LFU<K, Value<V>>,
        ghost_lru: BTreeMap<K, Txid>
        ghost_lfu: BTreeMap<K, Txid>
    }

    struct Value<V> {
        txid: Txid,
        data: V,
    }

Reader Behaviour
----------------

The reader is the simpler part of the two, so we'll start with that.

When a reader seeks an item in the cache, it references the read-only LRU/LFU trees. If found, we queue
a cache-hit marker to the channel.

If we miss, we look in our local hashmap. If found we return that.

If it is not in the local hashmap, we now seek in the database - if found, we load the entry.
The entry is stored in our local hashmap.

As the reader transaction ends, we send the set of entries in our local hash map as values (see
Modification to ARC), so that the data and the transaction id of the generation when we loaded
is associated. This has to be kept together as the queue could be recieving items from many generations
at once.

The reader attempts a "try_include" at the end of the operation, and if unable, it proceeds.

::

    enum State<V> {
        Missed<V>
        Accessed
    }

    struct ChanValue<K, V> {
        txid: Txid,
        key: K,
        data: State<V>
    }

Writer Behaviour
----------------

There are two major aspects to writer behaviour. The writer is responsible for maintaining a local
cache of missed items, a local cache of writen (dirty) items, managing the global LRU/LFU, and responding
to the reader inclusion requests.

When the writer looks up a value, it looks in the LFU/LRU. If found (and the writer is reading) we
return the data to the caller, and add an "accessed" value to the local thread store.

If the writer is attempting to mutate, we clone the value and put it into the local thread store in
the "dirty" state.

::

    enum State {
        Dirty(V),
        Clean(V),
        Accessed
    }

    struct Value<V> {
        txid: usize,
        state: State<V>
    }

If it is not found, we seek the value in the database. It is added to the cache. If this is a write,
we flag the entry as dirty. Else it's flagged clean.

If we abort, we move to the include step before we complete the operation.

If we commit, we write our clean and dirty flagged data to the LFU/LRU as required. The LRU/LFU
self manages it's lists and sets, it's okay to the concurrent behaviours. We indicate which items
have been accessed.

We the perform an "include" operation. Readers attempt this at the end of their operations if the
lock can be taken, and skip if not.

We dequeue from the queue up to some limit of values. For each value that is requested, we look it
up in our LRU/LFU.

* If the value was not in the ARC, and in the ghost list, include it + it's txid if the txid is higher than the ghost key txid
* If the value was not in the ARC, and not in the ghost list, include it.
* If the value is in the ARC, but a lower txid, we update the access metrics.
* If the value is in the ARC and a higher txid, we update the access metrics and update the value
  to the newer version.

* If the value is an accessed marker, and the item is in the ghost list, continue
* If the value is an accessed marker, and the item is in the ARC, we update it's access metrics

Questions for Future William
----------------------------

ARC moves from LRU -> LFU if the LRU has a hit, but this seems overly aggresive. Perhaps this should
be if LRU is a hit on 2 occasions move to LFU?

A thread must wake and feed the cache if we are unable to drain the readers, as we don't want the
queue to grow without bound.

Limitations and Concerns
------------------------

Cache missing is very expensive - multiple threads may load the value, the readers must queue
the value, and the writer must then act on the queue. Sizing the cache to be large enough is
critically important as eviction/missing will have a higher penalty than normal. Optimally
the cache will be "as large or larger" than the working set.

Due to the inclusion cost, the cache may be "slow" during the warm up, so this style of cache
really matters for highly concurrent software that can not tolerate locking behaviour, and
for items where the normal code paths are extremely slow. IE large item deserialisation
and return.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
