What's the problem with NUMA anyway?
====================================

What is NUMA?
-------------

Non-Uniform Memory Architecture is a method of seperating ram and memory management units to be associated with CPU sockets. The reason for this is performance - if multiple sockets shared a MMU, they will cause each other to block, delaying your CPU. 

To improve this, each NUMA region has it's own MMU and RAM associated. If a CPU can access it's local MMU and RAM, this is very fast, and does *not* prevent another CPU from accessing it's own. For example:

::

      CPU 0   <-- QPI --> CPU 1
        |                   |
        v                   v
      MMU 0               MMU 1
        |                   |
        v                   v
      RAM 1               RAM 2

For example, on the following system, we can see 1 numa region:

::

    # numactl --hardware
    available: 1 nodes (0)
    node 0 cpus: 0 1 2 3
    node 0 size: 12188 MB
    node 0 free: 458 MB
    node distances:
    node   0 
      0:  10 

On this system, we can see two:

::

    # numactl --hardware
    available: 2 nodes (0-1)
    node 0 cpus: 0 1 2 3 4 5 6 7 8 9 10 11 24 25 26 27 28 29 30 31 32 33 34 35
    node 0 size: 32733 MB
    node 0 free: 245 MB
    node 1 cpus: 12 13 14 15 16 17 18 19 20 21 22 23 36 37 38 39 40 41 42 43 44 45 46 47
    node 1 size: 32767 MB
    node 1 free: 22793 MB
    node distances:
    node   0   1
      0:  10  20
      1:  20  10

This means that on the second system there is 32GB of ram per NUMA region which is accessible, but the system has total 64GB.

The problem
-----------

The problem arises when a process running on NUMA region 0 has to access memory from another NUMA region. Because there is no direct connection between CPU 0 and RAM 1, we must communicate with our neighbour CPU 1 to do this for us. IE:

::

    CPU 0 --> CPU 1 --> MMU 1 --> RAM 1

Not only do we pay a time delay price for the QPI communication between CPU 0 and CPU 1, but now CPU 1's processes are waiting on the MMU 1 because we are retrieving memory on behalf of CPU 0. This is very slow (and can be seen by the node distances in the numactl --hardware output).

Today's work around
-------------------

The work around today is to limit your Directory Server instance to a single NUMA region. So for our example above, we would limit the instance to NUMA region 0 or 1, and treat the instance as though it only has access to 32GB of local memory.

It's possible to run two instances of DS on a single server, pinning them to their own regions and using replication between them to provide synchronisation. You'll need a load balancer to fix up the TCP port changes, or you need multiple addresses on the system for listening.

The future
----------

In the future, we'll be adding support for better copy-on-write techniques that allow the cores to better cache content after a QPI negotiation - but we still have to pay the transit cost. We can minimise this as much as possible, but there is no way today to avoid this penalty. To use all your hardware on a single instance, there will always be a NUMA cost somewhere.

The best solution is as above: run an instance per NUMA region, and internally provide replication for them. Perhaps we'll support an automatic configuration of this in the future.




.. author:: default
.. categories:: none
.. tags:: none
.. comments::
