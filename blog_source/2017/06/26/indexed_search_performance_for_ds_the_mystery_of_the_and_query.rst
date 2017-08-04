indexed search performance for ds - the mystery of the and query
===============================================================

Directory Server is heavily based on set mathematics - one of the few topics I enjoyed during university. Our filters
really boil down to set queries:

::

    &((attr=val1)(attr=val2))

This filter describes the intersection of sets of objects containing "attr=val1" and "attr=val2".

One of the properties of sets is that operations on them are commutative - the sets to a union or intersection
may be supplied in any order with the same results. As a result, these are equivalent:

::

    &(a)(b)(c)
    &(b)(a)(c)
    &(c)(b)(a)
    &(c)(a)(b)
    ...

In the past I noticed an odd behaviour: that the *order* of filter terms in an ldapsearch query would drastically change
the performance of the search. For example:

::

    &(a)(b)(c)
    &(c)(b)(a)

The later query may significantly outperform the former - but 10% or greater. I have never understood the reason why
though. I toyed with ideas of re-arranging queries in the optimise step to put the terms in a better order, but I didn't
know what factors affected this behaviour.

Over time I realised that if you put the "more specific" filters first over the general filters, you would see a 
performance increase.

What was going on?
------------------

Recently I was asked to investigate a full table scan issue with range queries. This led me into an exploration of our
search internals, and yielded the answer to the issue above.

Inside of directory server, our indexes are maintained as "pre-baked" searches. Rather than trying to search every
object to see if a filter matches, our indexes contain a list of entries that match a term. For example:

::

    uid=mark: 1, 2
    uid=william: 3
    uid=noriko: 4

From each indexed term we construct an IDList, which is the set of entries matching some term.

On a complex query we would need to intersect these. So the algorithm would iteratively apply this:

::

    t1 = (a, b)
    t2 = (c, t1)
    t3 = (d, t2)
    ...

In addition, the intersection would allocate a new IDList to insert the results into.

What would happen is that if your first terms were large, we would allocate large IDLists, and do many copies into it. This
would also affect later filters as we would need to check large ID spaces to perform the final intersection.

In the above example, consider a, b, c all have 10,000 candidates. This would mean t1, t2 is at least 10,000 IDs, and we
need to do at least 20,000 comparisons. If d were only 3 candidates, this means that we then throw away the majority of work
and allocations when we get to t3 = (d, t2).

What is the fix?
----------------

We now wrap each term in an idl_set processing api. When we get the IDList from each AVA, we insert it to the idl_set. This
tracks the "minimum" IDList, and begins our intersection from the smallest matching IDList. This means that we have the
quickest reduction in set size, and results in the smallest possible IDList allocation for the results. In my tests I have
seen up to 10% improvement on complex queries.

For the example above, this means we procees d first, to reduce t1 to the smallest possible candidate set we can.

::

    t1 = (d, a)
    t2 = (b, t1)
    t3 = (c, t2)
    ...

This means to create t2, t3, we will do an allocation that is bounded by the size of d (aka 3, rather than 10,000), we only need
to perform fewer queries to reach this point.

A benefit of this strategy is that it means if on the first operation we find t1 is empty set, we can return *immediately*
because no other intersection will have an impact on the operation.

What is next?
-------------

I still have not improved union performance - this is still somewhat affected by the ordering of terms in a filter. However,
I have a number of ideas related to either bitmask indexes or disjoin set structures that can be used to improve this performance.

Stay tuned ....


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
