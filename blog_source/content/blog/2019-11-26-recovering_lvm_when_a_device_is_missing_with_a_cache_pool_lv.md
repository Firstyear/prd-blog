+++
title = "Recovering LVM when a device is missing with a cache pool lv"
date = 2019-11-26
slug = "2019-11-26-recovering_lvm_when_a_device_is_missing_with_a_cache_pool_lv"
# This is relative to the root!
aliases = [ "2019/11/26/recovering_lvm_when_a_device_is_missing_with_a_cache_pool_lv.html" ]
+++
# Recovering LVM when a device is missing with a cache pool lv

I had a heartstopping moment today: my after running a command lvm
proudly annouced it had removed an 8TB volume containing all of my
virtual machine backing stores.

## Everyone, A short view back to the past \...

I have a home server, with the configured storage array of:

-   2x 8TB SMR (Shingled Magnetic Recording) archive disks (backup
    target)
-   2x 8TB disks (vm backing store)
-   2x 1TB nvme SSD (os + cache)

The vm backing store also had a lvm cache segment via the nvme ssds in a
raid 1 configuration. This means that the 2x8TB drives are in raid 1,
and a partition on each of the nvme devices are in raid 1, then they are
composed to allow the nvme to cache blocks from/to the 8TB array.

Two weeks ago I noticed one of the nvme drives was producing IO errors
indicating a fault of the device. Not wanting to risk corruption or
other issues from growing out of hand, I immediately shutdown the
machine and identified the nvme disk with the error.

At this stage I took the precaution of imaging (dd) both the good and
bad nvme devices to the archive array. Subsequently I completed a secure
erase of the faulty nvme drive before returning it to the vendor for
RMA.

I then left the server offline as I was away from my home for more than
a week and would not need, and was unable to monitor if the other drives
would produce further errors.

## Returning home \...

I decided to ignore William of the past (always a bad idea) and to
\"break\" the raid on the remaining nvme device so that my server could
operate allowing me some options for work related tasks.

This is an annoying process in lvm - you need to remove the missing
device from the volume group as well as indicating to the array that it
should no longer be in a raid state. This vgreduce is only for removing
missing PV\'s, it shouldn\'t be doing anything else.

I initiated the raid break process on the home, root and swap devices.
The steps are:

    vgreduce --removemissing <vgname>
    lvconvert -m0 <vgname>/<lvname>

This occured without fault due to being present on an isolated
\"system\" volume group, so the partial lvs were untouched and left on
the remaining pv in the vg.

When I then initiated this process on the \"data\" vg which contained
the libvirt backing store, vgreduce gave me the terrifying message:

    Removing logical volume "libvirt_t2".

Oh no \~

## Recovery Attempts

When a logical volume is removed, it can be recovered as lvm stores
backups of the LVM metadata state in /etc/lvm/archive.

My initial first reaction was that I was on a live disk, so I needed to
backup this content else it would be lost on reboot. I chose to put this
on the unaffected, and healthy SMR archive array.

    mount /dev/mapper/archive-backup /archive
    cp -a /etc/lvm /archive/lvm-backup

At this point I knew that randomly attempting commands would cause
*further damage* and likely *prevent any ability to recover*.

The first step was to activate ssh so that I could work from my laptop -
rather than the tty with keyboard and monitor on my floor. It also means
you can copy paste, which reduces errors. Remember, I\'m booted on a
live usb, which is why I reset the password.

    # Only needed in a live usb.
    passwd
    systemctl start sshd

I then formulated a plan and wrote it out. This helps to ensure that
I\'ve thought through the recovery process and the risks, it helps be to
be fully aware of the situation.

    vim recovery-plan.txt

Into this I laid out the commands I would follow. Here is the plan:

    bytes 808934440960
    data_00001-2096569583

    dd if=/dev/zero of=/mnt/lv_temp bs=4096 count=197493760
    losetup /dev/loop10 /mnt/lv_temp
    pvcreate --restorefile /etc/lvm/archive/data_00001-2096569583.vg --uuid iC4G41-PSFt-6vqp-GC0y-oN6T-NHnk-ivssmg /dev/loop10
    vgcfgrestore data --test --file /etc/lvm/archive/data_00001-2096569583.vg

Now to explain this: The situation we are in is:

-   We have a removed data/libvirt_t2 logical volume
-   The VG data is missing a single PV (nvme0). It still has three PVs
    (nvme1, sda1, sdb1).
-   We can not restore metadata unless all devices are present as per
    the vgcfgrestore man page.

This means, we need to make a replacement device to replace into the
array, and then to restore the metadata with that.

The \"bytes\" section you see, is the *size* of the missing nvme0
partition that was a member of this array - we need to create a loopback
device of the same or greater size to allow us to restore the metadata.
(dd, losetup)

Once the loopback is created, we can then recreate the pv on the
loopback device with the same UUID as the missing device.

Once this is present, we can now restore the metadata as documented
which should contain the logical volume.

I ran these steps and it was all great until vgcfgrestore. I can not
remember the exact error but it was along the lines of:

    Unable to restore metadata as PV was missing for VG when last modification was performed.

Yep, the vgreduce command has changed the VG state, triggering a
metadata backup, but because a device was missing at the time, we can
not restore this metadata.

## Options \...

At this point I had to consider alternate options. I conducted research
into this topic as well to see if others had encountered this case (no
one has ever not been able to restore their metadata apparently in this
case \...). The options that I arrived at:

-   1.  Restore the metadata from the nvme /root as it has older (but
        known) states - however I had recently expanded the libvirt_t2
        volume from a live disk, meaning it may not have the correct
        part sizes.

-   2.  Attempt to extract the xfs filesystem with DD from the disk to
        begin a data recovery.

-   3.  Cry in a corner

-   4.  Use lvcreate with the \"same paramaters\" and hope that it
        aligns the start at the same location as the former
        data/libvirt_t2 allowing the xfs filesystem to be accessed.

All of these weren\'t good - especially not 3.

I opted to attempt solution 1, and then if that failed, I would
disconnect one of the 8TB disks, attempt solution 4, then if that ALSO
failed, I would then attempt 2, finally all else lost I would begin
solution 3. The major risk of relying on 4 and 2 is that LVM has dynamic
geometry on disk, it does not always allocate contiguously. This means
that attempting 4 with lvcreate may not create with the same geometry,
and it may write to incorrect locations causing dataloss. The risk of 2
was again, due to the dynamic geometry what we recover may be
re-arranged and corrupt.

This mean option 1 was the best way to proceed.

I mounted the /root volume of the host and using the lvm archive I was
able to now restore the metadata.

    vgcfgrestore data --test --file /system/etc/lvm/archive/data_00004-xxxx.vg

Once completed I performed an lvscan to refresh what block devices were
available. I was then shown that every member of the VG data had
conflicting seqno, and that the metadata was corrupt and unable to
proceed.

Somehow we\'d made it worse :(

## Successful Procedure

At this point, faced with 3 options that were all terrible, I started to
do more research. I finally discovered a post describing that the lvm
metadata is stored on disk in the same format as the .vg files in the
archive, and it\'s a ring buffer. We may be able to restore from these.

To do so, you must *dd* out of the disk into a file, and then manipulate
the file to only contain a single metadata entry.

Remember how I made images of my disks before I sent them back? This was
their time to shine.

I did do a recovery plan with these commands too, but it was more
evolving due to the paramaters involved so it changed frequently with
the offsets. The plan was very similar to above - use a loop device as a
stand in for the missing block device, restore the metadata, and then go
from there.

We know that LVM metadata occurs in the first section of the disk, just
after the partition start. So to work out where this is we use gdisk to
show the partitions in the backup image.

    # gdisk /mnt/mion.nvme0n1.img
    GPT fdisk (gdisk) version 1.0.4
    ...

    Command (? for help): p
    Disk /mnt/mion.nvme0n1.img: 2000409264 sectors, 953.9 GiB
    Sector size (logical): 512 bytes
    ...

    Number  Start (sector)    End (sector)  Size       Code  Name
       1            2048         1026047   500.0 MiB   EF00
       2         1026048       420456447   200.0 GiB   8E00
       3       420456448      2000409230   753.4 GiB   8E00

It\'s important to note the sector size flag, as well as the fact the
output is in sectors.

The LVM header occupies 255 sectors after the start of the partition. So
this in mind we can now create a dd command to extract the needed
information.

    dd if=/mnt/mion.nvme0n1.img of=/tmp/lvmmeta bs=512 count=255 skip=420456448

bs sets the sector size to 512, count will read from the start up to 255
sectors of size \'bs\', and skip says to start reading after \'skip\' \*
\'sector\'.

At this point, we can now copy this and edit the file:

    cp /tmp/lvmmeta /archive/lvm.meta.edit

Within this file you can see the ring buffer of lvm metadata. You need
to find the highest seqno that is a *complete record*. For example, my
seqno = 20 was partial (is the lvm meta longer than 255, please contact
me if you know!), but seqno=19 was complete.

Here is the region:

    # ^ more data above.
    }
    # Generated by LVM2 version 2.02.180(2) (2018-07-19): Mon Nov 11 18:05:45 2019

    contents = "Text Format Volume Group"
    version = 1

    description = ""

    creation_host = "linux-p21s"    # Linux linux-p21s 4.12.14-lp151.28.25-default #1 SMP Wed Oct 30 08:39:59 UTC 2019 (54d7657) x86_64
    creation_time = 1573459545      # Mon Nov 11 18:05:45 2019

    ^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@^@data {
    id = "4t86tq-3DEW-VATS-1Q5x-nLLy-41pR-zEWwnr"
    seqno = 19
    format = "lvm2"

So from there you remove everything above \"contents = \...\", and clean
up the vgname header. It should look something like this.

    contents = "Text Format Volume Group"
    version = 1

    description = ""

    creation_host = "linux-p21s"    # Linux linux-p21s 4.12.14-lp151.28.25-default #1 SMP Wed Oct 30 08:39:59 UTC 2019 (54d7657) x86_64
    creation_time = 1573459545      # Mon Nov 11 18:05:45 2019

    data {
    id = "4t86tq-3DEW-VATS-1Q5x-nLLy-41pR-zEWwnr"
    seqno = 19
    format = "lvm2"

Similar, you need to then find the bottom of the segment (look for the
next highest seqno) and remove everything *below* the line: \"#
Generated by LVM2 \...\"

Now, you can import this metadata to the loop device for the missing
device. Note I had to wipe the former lvm meta segment due to the
previous corruption, which caused pvcreate to refuse to touch the
device.

    dd if=/dev/zero of=/dev/loop10 bs=512 count=255
    pvcreate --restorefile lvmmeta.orig.nvme1.edited --uuid iC4G41-PSFt-6vqp-GC0y-oN6T-NHnk-ivssmg /dev/loop10

Now you can do a dry run:

    vgcfgrestore --test -f lvmmeta.orig.nvme1.edited data

And the real thing:

    vgcfgrestore -f lvmmeta.orig.nvme1.edited data
    lvscan

Hooray! We have volumes! Let\'s check them, and ensure their filesystems
are sane:

    lvs
    lvchange -ay data/libvirt_t2
    xfs_repair -n /dev/mapper/data-libvirt_t2

If xfs_repair says no errors, then go ahead and mount!

At this point, lvm started to resync the raid, so I\'ll leave that to
complete before I take any further action to detach the loopback device.

## How to Handle This Next Time

The cause of this issue really comes from vgreduce \--removemissing
removing the device when a cache member can\'t be found. I plan to
report this as a bug.

However another key challenge was the inability to restore the lvm
metadata when the metadata archive reported a missing device. This is
what stopped me from being able to restore the array in the first place,
even though I had a \"fake\" replacement. This is also an issue I intend
to raise.

Next time I would:

-   Activate the array as a partial
-   Remove the cache device first
-   Then stop the raid
-   Then perform the vgreduction

I really hope this doesn\'t happen to you!

