+++
title = "LDAP Guide Part 1: Foundations"
date = 2016-06-20
slug = "2016-06-20-the_ldap_guide_part_1_foundations"
# This is relative to the root!
aliases = [ "2016/06/20/the_ldap_guide_part_1_foundations.html" ]
+++
# LDAP Guide Part 1: Foundations

To understand LDAP we must understand a number of concepts of
datastructures: Specifically graphs.

## Undirected

In computer science, a set of nodes, connected by some set of edges is
called a graph. Here we can see a basic example of a graph.

![image](/_static/graph-basic-1.svg)

Viewing this graph, we can see that it has a number of properties. It
has 4 nodes, and 4 edges. As this is undirected we can assume the link A
to B is as valid as B to A.

We also have a cycle: That is a loop between nodes. We can see this in
B, C, D. If any edge between the set of B, D or B, C, or C, D were
removed, this graph would no longer have cycles.

