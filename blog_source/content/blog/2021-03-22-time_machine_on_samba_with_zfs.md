+++
title = "Time Machine on Samba with ZFS"
date = 2021-03-22
slug = "2021-03-22-time_machine_on_samba_with_zfs"
# This is relative to the root!
aliases = [ "2021/03/22/time_machine_on_samba_with_zfs.html" ]
+++
# Time Machine on Samba with ZFS

Time Machine is Apple\'s in-built backup system for MacOS. It\'s
probably the best consumer backup option, which really achieves \"set
and forget\" backups.

It can backup to an external hard disk on a dock, an Apple Time Machine
(wireless access point), or a custom location based on SMB shares.

Since I have a fileserver at home, I use this as my Time Machine backup
target. To make this work really smoothly there are a few setup steps.

## MacOS Time Machine Performance

By default timemachine operates as a low priority process. You can set a
sysctl to improve the performance of this (especially helpful for a
first backup!)

    sysctl -w debug.lowpri_throttle_enabled=0

You will need a launchd script to make this setting survive a reboot.

## ZFS

I\'m using ZFS on my server, which is probably the best filesystem
available. To make Time Machine work well on ZFS there are a number of
tuning options that can help. As these backups write and read many small
files, you should have a large amount of RAM for ARC (best) or a ZIL on
nvme. RAID 10 will likely work better than RAIDZ here as you need better
seek latency than write throughput due to the need to access many small
files. Generally time machine is very \"IO demanding\".

For the ZFS properties on the filesystem I created it with the following
options to [zfs create]{.title-ref}. Each once is set with [-o
attribute=value]{.title-ref}

    atime: off
    dnodesize: auto
    xattr: sa
    logbias: throughput
    recordsize: 1M
    compression: zstd-10 | zle
    refquota: 3T
    # optional - greatly improves write performance
    sync: disabled
    # security
    setuid: off
    exec: off
    devices: off

The important ones here are the compression setting. If you choose zle,
you gain much faster write performance, but you dont get much in the way
of compression. zstd-10 gives me about 1.3x compression, but at the loss
of performance. Generally the decision is based on your pool and storage
capacity.

Also note the use of refquota instead of quota. This applies the quota
to this filesystem only excluding snapshots - if you use quota, the
space taken by snapshots it also applied to this filesystem, which may
cause you to run out of space.

You may optionally choose to disable sync. This is because Time Machine
issues a sync after every single file write to the server, which can
cause low performance with many small files. To mitigate the data loss
risk here, I snapshot the backups filesystem hourly.

If you want to encrypt at the ZFS level instead of through time machine
you need to enable this as you create the filesystem.

    # create a key file to unlock the zfs filesystem
    openssl rand -hex -out /root/key 32

    # Add the following settings during zfs create:
    -o encryption=aes-128-gcm -o keyformat=hex -o keylocation=file:///root/key

If you add any subvolumes, you need to repeat the same encryption steps
during the create of these subvolumes.

For example a create may look like:

    zfs create \
        -o encryption=aes-128-gcm -o keyformat=hex -o keylocation=file:///root/key \
        -o atime=off -o dnodesize=auto -o xattr=sa -o logbias=throughput \
        -o recordsize=1M -o compression=zle -o refquota=3T -o sync=disabled \
        -o setuid=off -o exec=off -o devices=off tank/backups

## smb.conf

In smb.conf you define the share that exposes the timemachine backup
location. You need to set additional metadata on this so that macos will
recognise it correctly.

    [global]
    min protocol = SMB2
    ea support = yes

    # This needs to be global else time machine ops can fail.
    vfs objects = fruit streams_xattr
    fruit:aapl = yes
    fruit:metadata = stream
    fruit:model = MacSamba
    fruit:posix_rename = yes
    fruit:veto_appledouble = no
    fruit:nfs_aces = no
    fruit:wipe_intentionally_left_blank_rfork = yes
    fruit:delete_empty_adfiles = yes
    spotlight = no

    [timemachine_a]
    comment = Time Machine
    fruit:time machine = yes
    fruit:time machine max size = 1050G
    path = /var/data/backup/timemachine_a
    browseable = yes
    write list = timemachine
    create mask = 0600
    directory mask = 0700
    # NOTE: Changing these will require a new initial backup cycle if you already have an existing
    # timemachine share.
    case sensitive = true
    default case = lower
    preserve case = no
    short preserve case = no

The fruit settings are required to help Time Machine understand that
this share is usable for it. I have also added a custom timemachine user
to smbpasswd, and created a matching posix account who should own these
files.

## MacOS

You can now add this to MacOS via system preferences. If your ZFS volume
is NOT encyrpted, you should add the timemachine volume via system
preferences, as it is the only way to enable encryption of the time
machine backup. For system preferences to \"see\" the samba share you
may need to mount it manually via finder as the time machine user.

If you are using ZFS encryption, you can add the time machine backup
from the command line instead.

    tmutil setdestination smb://timemachine:password@hostname/timemachine_a

If you intend to have multiple time machine targets, MacOS is capable of
mirroring between multilple stripes alternately. You can append the
second stripe with (note the -a). You could do this with other shares
(offsite for example) or with a HDD on your desk.

    tmutil setdestination -a smb://timemachine:password@hostname/timemachine_b

