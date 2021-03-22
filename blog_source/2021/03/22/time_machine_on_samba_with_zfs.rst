Time Machine on Samba with ZFS
==============================

Time Machine is Apple's in-built backup system for MacOS. It's probably the best consumer backup
option, which really achieves "set and forget" backups.

It can backup to an external hard disk on a dock, an Apple Time Machine (wireless access point), or
a custom location based on SMB shares.

Since I have a fileserver at home, I use this as my Time Machine backup target. To make this work
really smoothly there are a few setup steps.

ZFS
---

I'm using ZFS on my server, which is probably the best filesystem available. To make Time Machine
work well on ZFS there are a number of tuning options that can help. As these backups write and
read many small files, you should have a large amount of RAM for ARC (best) or a ZIL + L2ARC
on nvme. RAID 10 will likely work better than RAIDZ here as you need better seek latency than write
throughput due to the need to access many small files.

For the ZFS properties on the filesystem I have set:

::

    atime: off
    dnodesize: auto
    xattr: sa
    logbias: latency
    recordsize: 32K
    compression: zstd-10
    quota: 3T
    # optional
    sync: disabled

The important ones here are the compression setting, which in my case gives a 1.3x compression ratio
to save space, the quota to prevent the backups overusing space, the recordsize that helps to minimise
write fragmentation.

You may optionally choose to disable sync. This is because Time Machine issues a sync after every
single file write to the server, which can cause low performance with many small files. To mitigate
the data loss risk here, I both snapshot the backups directory hourly, but I also have two stripes
(an A/B backup target) so that if one of the stripes goes back, I can still access the other. This
is another reason that compression is useful, to help offset the cost of the duplicated data.

Quota
-----

Inside of the backups filessytem I have two folders:

::

    timemachine_a
    timemachine_b

In each of these you can add a PList that applies quota limits to the time machine stripes.

::

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>GlobalQuota</key>
        <integer>1000000000000</integer>
      </dict>
    </plist>


The quota is in bytes. You may not need this if you use the smb fruit:time machine max size setting.

smb.conf
--------

In smb.conf I offer two shares for the A and B stripe. These have identical configurations beside the paths.

::

    [timemachine_b]
    comment = Time Machine
    path = /var/data/backup/timemachine_b
    browseable = yes
    write list = timemachine
    create mask = 0600
    directory mask = 0700
    spotlight = no
    vfs objects = catia fruit streams_xattr
    fruit:aapl = yes
    fruit:time machine = yes
    fruit:time machine max size = 1050G
    durable handles = yes
    kernel oplocks = no
    kernel share modes = no
    posix locking = no

The fruit settings are required to help Time Machine understand that this share is usable for it.
Most of the durable settings are related to performance improvement to help minimise file locking
and to improve throughput. These are "safe" only because we know that this volume is ALSO not accessed
or manipulated by any other process or nfs at the same time.

I have also added a custom timemachine user to smbpasswd, and created a matching posix account who should
own these files.

MacOS
-----

You can now add this to MacOS via system preferences. Alternately you can use the command line.

::

    tmutil setdestination smb://timemachine:password@hostname/timemachine_a

If you intend to have stripes (A/B), MacOS is capable of mirroring between two strips alternately.
You can append the second stripe with (note the -a).

::

    tmutil setdestination -a smb://timemachine:password@hostname/timemachine_b



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
