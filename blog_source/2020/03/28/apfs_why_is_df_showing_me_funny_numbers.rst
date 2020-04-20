APFS (why is df showing me funny numbers?!)
===========================================

Apple's APFS has been the default for MacOS since High Sierra, where SSD (flash) automatically
would convert from HFS+. This is a god send, especially with HFS+'s history of destroying any
folder that has a large number of inodes within it.

However, APFS behaves differently to previous filesystem technology. Let's see if we can
explain why df reports multiple 932Gi disks like this:

::

    > df -h
    Filesystem                             Size   Used  Avail Capacity    iused      ifree %iused  Mounted on
    /dev/disk1s5                          932Gi   10Gi  380Gi     3%     484322 9767493838    0%   /
    /dev/disk1s1                          932Gi  530Gi  380Gi    59%    2072480 9765905680    0%   /System/Volumes/Data

And if we can explain why when you delete large files, you don't get any space back from df
either.

How it looked with HFS+
-----------------------

With HFS+ it was pretty simple. You had a disk (a block device), which had partitions (slices of
the space in the block device) and those partitions were formatted with a filesystem that knew
how to store data in them. An example:

::

    > diskutil list
    ...
    /dev/disk2 (external, physical):
       #:                       TYPE NAME                    SIZE       IDENTIFIER
       0:      GUID_partition_scheme                         *1.0 TB     disk2
       1:                        EFI EFI                     209.7 MB   disk2s1
       2:                  Apple_HFS tmachine                999.9 GB   disk2s2

We can see that disk2 is 1.0TB in size, and it contains two partitions, the first is 209.7MB for
EFI (disk2s1) and the second has data and formatted as HFS+ (disk2s2).

Of course, this has some drawbacks - partitions don't like being moved, and filesystem resizing
is a costly process of time and IO cycles. It's quite inflexible. If you wanted another partition
here for read only data, well, you'd have to change a lot. Properties can only be applied to a
filesystem as a whole, and they can't share space. If you had a 1TB drive partitioned to 500GB
each, and were running low on space on one of them, well ... good luck! You have to move data
manually, or change where applications store data.

APFS
----

APFS doesn't quite follow this model though. APFS is what's called a volume based filesystem.
That means there is an intermediate layer in here. The layout looks like this in diskutil

::

    > diskutil list
    ...
    /dev/disk0 (internal, physical):
       #:                       TYPE NAME                    SIZE       IDENTIFIER
       0:      GUID_partition_scheme                        *1.0 TB     disk0
       1:                        EFI EFI                     314.6 MB   disk0s1
       2:                 Apple_APFS Container disk1         1.0 TB     disk0s2

So our disk0 looks like before - an EFI partition, and a very large APFS container. However
the container itself is NOT the filesystem. The contain is a pool of storage that APFS volumes
are created into. We can see the volumes too.

::

    > diskutil list
    ...
    /dev/disk1 (synthesized):
       #:                       TYPE NAME                    SIZE       IDENTIFIER
       0:      APFS Container Scheme -                      +1.0 TB     disk1
                                     Physical Store disk0s2
       1:                APFS Volume Macintosh HD — Data     569.4 GB   disk1s1
       2:                APFS Volume Preboot                 81.8 MB    disk1s2
       3:                APFS Volume Recovery                526.6 MB   disk1s3
       4:                APFS Volume VM                      10.8 GB    disk1s4
       5:                APFS Volume Macintosh HD            11.0 GB    disk1s5

Notice how /dev/disk1 is "synthesized"? It's not real - it's there to "trick" legacy tools into
thinking that the container is a "block" device and the volumes are "partitions".

Benefits of Volumes
-------------------

One of the immediate benefits is that unlike partitions, in a volume filesystem, *all* the space
of the underlying container (also known as: pool, volume group) is available to *all* volumes at anytime. Because 
the volumes are a flexible concept, they can have non-contiguous geometry on the disk (unlike a
partition). That's why in your df output you can see:

::

    > df -h
    Filesystem                             Size   Used  Avail Capacity    iused      ifree %iused  Mounted on
    /dev/disk1s5                          932Gi   10Gi  380Gi     3%     484322 9767493838    0%   /
    /dev/disk1s1                          932Gi  530Gi  380Gi    59%    2072480 9765905680    0%   /System/Volumes/Data

Both disk1s5 (Macintosh HD) and disk1s1 (Macintosh HD — Data) are APFS volumes. The container has 932Gi
total space, and 380Gi available in the container which either volume could allocate. But you can also
see the exact space reservation of each volume too: disk1s5 only has 10Gi in use, and disk1s1 has
530Gi in use.

It would be very possible for disk1s1 to grow to fill all the space, and then to contract, and then
have disk1s5 grow to take all the space and contract - this is because the space is flexibly
allocated from the container. Neat!

Each volume also can have different properties applied. For example, /dev/disk1s5 (Macintosh HD) in
MacOS catalina is read-only:

::

    /dev/disk1s5 on / (apfs, local, read-only, journaled)
    /dev/disk1s1 on /System/Volumes/Data (apfs, local, journaled, nobrowse)

This is to prevent system tampering, and strengthen integrity of the system. There are a number
of tricks to achieve this such as overlaying multiple volumes together. /Applications for example
is actually a folder consitituted from the content of /System/Applications and /System/Volumes/Data/Applications.
Anytime you "drag" and application to /Applications, you are actually putting it into /System/Volumes/Data/Applications.
A very similar property holds for /Users (/System/Volumes/Data/Users), and even /Volumes.

Copy-on-Write, Snapshots
------------------------

APFS is also a copy-on-write filesystem. This means whenever you write data, it's actually written
to newly allocated disk regions, and the pointers are atomicly flipped to it. The full write occurs
or it does not. This is part of the reason why APFS is so much better than HFS+ - in a crash
your data is either in a previous state, or the new state - never a half written or corrupted
state.

This is the reason why APFS is only used on SSD (flash) devices - COW is very random IO write
intensive, and on a rotational disk this would cause the head to "seek" randomly which would make
both writes and reads very slow. SSD of course isn't affected by this, so having a highly fragmented
file does not impose a penalty in the same way.

Copy-on-Write however opens up some interesting behaviours. If you COW a file, but never remove
the old version, you have a *snapshot*. This means you can have point-in-time views to how a
filesystem was. This is actually used now by time machine during backups to ensure the content
of a backup is stable before being written to the external backup media. It also allow time machine
to perform "backups" while you are out-and-about, by snapshotting as you work. Because snapshots
are just "not removing old data" they are low overhead to maintain and take snapshots.

You can see snapshots on your system with:

::

    > tmutil listlocalsnapshots /
    Snapshots for volume group containing disk /:
    com.apple.TimeMachine.2020-03-27-084939.local
    com.apple.TimeMachine.2020-03-27-100157.local
    com.apple.TimeMachine.2020-03-27-105937.local
    com.apple.TimeMachine.2020-03-27-121414.local
    ...

You can even take your own snapshots if you want!

::

    > time tmutil localsnapshot
    Created local snapshot with date: 2020-03-28-091943
    tmutil localsnapshot  0.01s user 0.01s system 4% cpu 0.439 total

See how fast that is! Remember also because this is based on copy-on-write, the snapshots only
take as much data as the *differences*, or what you are changing as you work.

Space Reclaim
-------------

This leads to the final point of confusion - when people delete files to clear space, but
df reports no change. For example:

::

    > df -h
    Filesystem                             Size   Used  Avail Capacity    iused      ifree %iused  Mounted on
    /dev/disk1s1                          932Gi  530Gi  380Gi    59%    2072480 9765905680    0%   /System/Volumes/Data
    > ls -alh Downloads/Windows_Server_2016_Datacenter_EVAL_en-us_14393_refresh.ISO
    -rwx------@ 1 william  staff   6.5G 10 Oct  2018 Downloads/Windows_Server_2016_Datacenter_EVAL_en-us_14393_refresh.ISO
    > rm Downloads/Windows_Server_2016_Datacenter_EVAL_en-us_14393_refresh.ISO
    > df -h
    Filesystem                             Size   Used  Avail Capacity    iused      ifree %iused  Mounted on
    /dev/disk1s1                          932Gi  530Gi  380Gi    59%    2072479 9765905681    0%   /System/Volumes/Data

Now I promise, I really did delete the file - check the "iused" and "ifree" columns. But also note
that the "Used" space didn't change? Surely we should expect to see this value drop to 523Gi since
I removed a 6.5G file.

Remember that APFS is a voluming filesystem, with copy-on-write. Due to snapshots, the space used
in a volume is the sum of active data *and* snapshotted data. This means that when you are removing
a file you are removing it from the volume at this point in time, but it may still exist in
snapshots that exist in the volume! That's why there is a reduction in the iused/ifree (an inode
pointer was removed) but no change in the space (the file still exists in a snapshot).

During normal operation, provided there is sufficent freespace, you won't actually notice this behaviour.
But when you say ... have not a lot of space left (maybe 10G), and you delete some files to import
something (say a 40G import), you try the copy again ... and it fails! Drat! But you wait a bit
and suddenly it works? What in heck happened?

In the background, MacOS has registered "okay, the user demands at least 30G more space to complete
this task. Let's clean snapshots until we have that much space available". The snapshots are pruned
so when you come back later, suddenly you have the space.

Again, you can actually do this yourself. tmutil has a command "thinlocalsnapshots" for this. An
example usage would be:

::

    > tmutil thinlocalsnapshots /System/Volumes/Data [bytes required]
    Thinned local snapshots:

In my case I have a lot of space available, so no snapshots are pruned. But you may find that
multiple snapshots are removed in this process!

Conclusion
----------

APFS is actually a really cool piece of filesystem technology, and I think has made MacOS one of
the most viable platforms for reliable daily use. It embraces many great ideas, and despite it's
youth, has done really well. But those new ideas conflict with legacy, and have some behaviours that
are not always clearly exposed on shown to you, the user. Understanding those behaviours means we
can see *why* our computers are behaving in certain - sometimes unexpected - ways.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
