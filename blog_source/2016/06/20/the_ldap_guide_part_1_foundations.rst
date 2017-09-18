LDAP Guide Part 1: Foundations
==============================

To understand LDAP we must understand a number of concepts of datastructures: Specifically graphs.

Undirected
----------

In computer science, a set of nodes, connected by some set of edges is called a graph. Here we can see a basic example of a graph.

.. image:: /_static/graph-basic-1.svg

Viewing this graph, we can see that it has a number of properties. It has 4 nodes, and 4 edges. As this is undirected we can assume the link A to B is as valid as B to A.

We also have a cycle: That is a loop between nodes. We can see this in B, C, D. If any edge between the set of B, D or B, C, or C, D were removed, this graph would no longer have cycles.

.. more::

Directed
--------

A directed graph is where each edge not only defines a link between two nodes, but also the direction of the link. For example, we can see that A to B is a valid edge, but B to A is not. We would say that the node where the link is from is the outgoing node of the edge. Where the node recieves an egde, IE the arrow, is an incoming edge.

.. image:: /_static/graph-basic-2.svg

In this graph, for a cycle to occur, we must have a set of nodes where not only the edges exist, but the direction allows a loop. Here, the cycle is B, C, D. Were the link between C and D reversed, we no longer have a cycle in our directed graph.

.. image:: /_static/graph-basic-3.svg

Trees
-----

A tree is a special case of the directed graph. The properties of a tree are that:

* Each node has 1 and only 1 incoming edge.
* The graph may have no cycles.

An example of a tree is below. You can check and it maintains all the properties above. Note there is no limit to outbound edges, the only rule is maximum of one incoming.

.. image:: /_static/graph-basic-4.svg

A property that you regularly see is that nodes are unique in a tree, IE A will not appear twice. This allows for *searching* of the tree.

More on nodes
-------------

So far our nodes have been a bit bland. We can do more with them though. Instead of just storing a single datum in them, we can instead store the datum as a key to lookup the node, and then have more complex data in the value of the node. For example, we can expand our tree to look like this:


.. image:: /_static/graph-basic-5.svg

This is why having unique keys in our nodes is important. It allows us to search the tree for that node, and to retrieve the data stored within.

What does LDAP look like
------------------------

LDAP is a tree of objects. Each object has a name, or an RDN (Relative Distinguished Name). The object itself has many key: value pairs in it's data field. If we visualise this, it looks like this.

.. image:: /_static/graph-basic-6.svg
    :width: 850 px

We have the RDN (our tree node's key value), displayed by type=value, and then a set of attributes (the data of the node).

Naming things
-------------

With LDAP often we want to directly reference an node in the tree. To do so, we need a way to uniquely reference the nodes as they exist.

Unlike our example trees, where each key is likely to be unique. IE node with key A is cannot exist twice in the tree. In ldap it *is* valid to have a key exist twice, such as ou=People. This raises a challenge. Previously, we could just "look for A", and we would have what we wanted. But now, we must not only know the RDN, aka key, that we want to retrieve, but the path through the tree from the root to our target node with the RDN.

This is done by walking down the tree til we find what we want. Looking at the image above, consider:

::

    dc=com
    dc=example,dc=com
    ou=People,dc=example,dc=com
    uid=user,ou=People,dc=example,dc=com

We can make a Fully Qualified Distinguished Name (FQDN), or just Distinguished Name(DN), by joining the RDN components. For our example, uid=user,ou=People,dc=example,dc=com. This is a unique path through the tree to the node we wish to access.

This should explain why LDAP is called a "tree", why objects are named the way they are, and help you to visualise the layout of data in your own tree.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
