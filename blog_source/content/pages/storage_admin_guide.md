+++
title = "Storage Administration Guide"
date = 2023-09-08
slug = "storage_admin_guide"
# This is relative to the root!
# aliases = [ "2016/06/20/the_ldap_guide_part_1_foundations.html", "blog/html/pages/ldap_guide_part_1_foundations.html" ]
+++

# Storage Administration Guide

This guide will help you understand, configure and maintain storage on Linux servers. The content
of this guide is optimised for reliability and accesibility. This is based not only on my own
experiences but observing the experiences of enterprise customers for many years.

## ⚠️  Warnings ⚠️

Making changes to storage entails risks. Linux and it's storage tools have no safety barriers.
Mistakes can result in *COMPLETE LOSS OF ALL YOUR DATA*.

*DO NOT COPY PASTE COMMANDS HERE WITHOUT UNDERSTANDING THEM.*

*CAREFULLY PLAN YOUR COMMANDS.*

*HAVE BACKUPS THAT YOU HAVE TESTED.*

Almost all commands in this document require root privilieges.

This document is a work in progress!

## General Advice

Before executing commands that will change your storage you should analyse your storage,
make notes, and prepare your commands in a notepad before you execute the commands. This
will allow you to review before making changes.

## Understanding Your Storage

Before changing your storage configurations you need to understand what you have and what you may
want to achieve.

### List Storage On Your System

`lsblk` is the most important command in your toolbox. It allows you to understand the layout and
set of your storage between making changes. It also allows you to check which disks are in use so
that you can *avoid* them while making changes.

```
# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sr0     11:0    1  372K  0 rom
vda    254:0    0   10G  0 disk
├─vda1 254:1    0    2M  0 part
├─vda2 254:2    0   33M  0 part /boot/efi
└─vda3 254:3    0   10G  0 part /
vdb    254:16   0   50G  0 disk
vdc    254:32   0   50G  0 disk
vdd    254:48   0   50G  0 disk
vde    254:64   0   50G  0 disk
```

```
# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sr0     11:0    1  372K  0 rom
vda    254:0    0   10G  0 disk <---------- this is a whole disk.
                                           /-- these partitions exist on the disk.
├─vda1 254:1    0    2M  0 part            - <- this partition is not mounted
├─vda2 254:2    0   33M  0 part /boot/efi  | <- this partition is mounted at /boot/efi
└─vda3 254:3    0   10G  0 part /          - <- this partition is mounted on /
vdb    254:16   0   50G  0 disk
vdc    254:32   0   50G  0 disk <---------- these disks have no partitions
vdd    254:48   0   50G  0 disk
vde    254:64   0   50G  0 disk
```

### View Filesystems That Mount At Boot

Filesystems are mounted at boot from the *F*ile*S*ystem *TAB*le. These are stored in `/etc/fstab`.

```
# cat /etc/fstab
UUID=ef76b8e7-6017-4757-bd51-3e0e662d408b / xfs defaults 0 1
UUID=F6F5-05FB /boot/efi vfat defaults 0 0
```

This is arranged as a white-space separted table.

```
/- The path or identifier of the device to mount
|                                                          
|                                         /- where to mount the filesystem
|                                         |                   
|                                         |    /- the type of filesysetm on the device
|                                         |    |              
|                                         |    |   /- mount options for the filesystem to be mounted
|                                         |    |   |          
|                                         |    |   |        /- dump to tape on crash. set to 0
|                                         |    |   |        |
|                                         |    |   |        | /- order of filesystem checks at boot.
|                                         |    |   |        | |  0 = do not check
|                                         |    |   |        | |  1 = check first
|                                         |    |   |        | |  2 = check second ...
v                                         v    v   v        v v
UUID=ef76b8e7-6017-4757-bd51-3e0e662d408b /    xfs defaults 0 1
/dev/disk/by-id/wwn-0x5001b448bd8e7de2    /mnt xfs defaults 0 0
```

### Show Disk Path Or Identifiers

Linux allows disks to be referenced by different aliases that can be more accessible or unique
to help prevent mistakes. For example, `vda` and `sda` are very similar but `virtio-pci-0000:04:00.0`
or `wwn-0x5000cca0bbefc231` are distinct and uniquely identify the device. In addition if you move
the device between different ports (e.g. changing sata ports, or sas ports) then some of these identifiers
will stay stable between those changes.

#### Show disks by identifiers

Disk by ID are a stable identifier that should not change between systems or connection of the device.

These are commonly used in ZFS pools or administration commands.

```
# ls -l /dev/disk/by-id
lrwxrwxrwx 1 root root  9 Sep  7 08:51 scsi-1ATA_WDC_WDS200T1R0A-68A4W0_223609A005A5 -> ../../sdg
lrwxrwxrwx 1 root root 10 Sep  7 08:51 scsi-1ATA_WDC_WDS200T1R0A-68A4W0_223609A005A5-part1 -> ../../sdg1
lrwxrwxrwx 1 root root 10 Sep  7 08:51 scsi-1ATA_WDC_WDS200T1R0A-68A4W0_223609A005A5-part9 -> ../../sdg9
...
lrwxrwxrwx 1 root root  9 Sep  7 08:51 wwn-0x5001b448bd8e7de2 -> ../../sdg
lrwxrwxrwx 1 root root 10 Sep  7 08:51 wwn-0x5001b448bd8e7de2-part1 -> ../../sdg1
lrwxrwxrwx 1 root root 10 Sep  7 08:51 wwn-0x5001b448bd8e7de2-part9 -> ../../sdg9
```

#### Show disks by UUID

Generally only partitions with filesystems will have a UUID - this will not show "devices".

UUID's are a stable identifier that should not change between systems or connection of the device.

These are commonly used in `/etc/fstab` for mounting filesystems. These are used with
the `fstab` syntax of `UUID=< ... >`

```
# ls -l /dev/disk/by-uuid
lrwxrwxrwx 1 root root 15 Sep  7 08:51 DA2C-4E2B -> ../../nvme1n1p1
lrwxrwxrwx 1 root root 10 Sep  7 08:51 e3967de9-6cab-4387-8a58-aa6b34dba39f -> ../../dm-9
```

#### Show disks by their physical attachment path

These are commonly used to locate the type of device, and where it may be attached on a system.

```
# ls -l /dev/disk/by-path
lrwxrwxrwx 1 root root  9 Sep  7 08:51 pci-0000:00:17.0-ata-8.0 -> ../../sdg
lrwxrwxrwx 1 root root 10 Sep  7 08:51 pci-0000:00:17.0-ata-8.0-part1 -> ../../sdg1
lrwxrwxrwx 1 root root 10 Sep  7 08:51 pci-0000:00:17.0-ata-8.0-part9 -> ../../sdg9
lrwxrwxrwx 1 root root 13 Sep  7 08:51 pci-0000:01:00.0-nvme-1 -> ../../nvme0n1
lrwxrwxrwx 1 root root 15 Sep  7 08:51 pci-0000:01:00.0-nvme-1-part1 -> ../../nvme0n1p1
lrwxrwxrwx 1 root root 15 Sep  7 08:51 pci-0000:01:00.0-nvme-1-part2 -> ../../nvme0n1p2
lrwxrwxrwx 1 root root 15 Sep  7 08:51 pci-0000:01:00.0-nvme-1-part3 -> ../../nvme0n1p3
```

## What Storage Setup Do I Want?

Here are some questions that may help you to decide how to configure the storage in your system.

### I'm Installing My Favourite Distro On A Laptop/Workstation

* You should use GPT for partitioning.
* You should use LVM to allow resizing partitions, creating raid or changing disks in the future.
* Split Home vs Root OR combined Home + Root is a personal preference.
* If you want fast and highly reliable storage -> Choose XFS
* If you want features like snapshots -> Choose BTRFS

### I'm Adding Non-Root Disks To My Workstation/Server

#### I Want Highly Reliable, Fault Tolerant Storage

* Use ZFS

#### I Can Not Afford To Lose Data Ever.

* Use ZFS

#### I Want One Giant Pool Of Storage That I Will Expand In Future

* Use ZFS

#### I Plan To Add/Remove/Change Disks Again When Ever I Feel Like

* Use LVM+RAID

#### I Just Want Disks Mounted Like A Chaos Goblin

* You should use GPT for partitioning.
* You should use LVM to allow resizing partitions, creating raid or changing disks in the future.
* If you want fast and highly reliable storage -> Choose XFS
* If you want features like snapshots -> Choose BTRFS

## Managing Single Disks

### Reload partition tables

After making changes to partition tables, you may need to force the kernel to re-read them so that
they are reflected in commands like `lsblk`

```
# partprobe
```

## ZFS

todo!();

## LVM

LVM is a Logical Volume Manager for Linux. It allows dynamically changing storage without downtime,
and the ability to warp and shape into complex and weird disk layouts and geometries. It has excellent
observability into the state of storage, and you should consider it a "must have" on all systems.

LVM's single limitation is you can not use it for `/boot` or `EFI System Partitions`. These
must remain as "true" partitions. If in doubt, trust your installer.

LVM combines a set of physical volumes (PV) into a volume group (VG). A volume group contains a pool of available
storage. logical volumes (LV) can then be created within that volume group that consume that storage.
Each logical volume can have it's own characteristics like raid levels. Logical volumes due to
how they work may span multiple physical volumes since an LV consumes space from the VG which can
allocate anywhere in the PV's available. This can be visualised as:

```
┌──────┐ ┌──────────────────────┐           
│  LV  │ │          LV          │           
└──────┘ └──────────────────────┘           
┌──────────────────────────────────────────┐
│                    VG                    │
└──────────────────────────────────────────┘
┌────────────┐ ┌────────────┐ ┌────────────┐
│     PV     │ │     PV     │ │     PV     │
└────────────┘ └────────────┘ └────────────┘
```

Here we have two LV's within a VG. The VG is made from 3 PVs. The storage of the LV's may be anywhere
within the pool of PV's that exist. This allows PVs to be added or removed dynamically as the LV
content can be moved at any time.

### General LVM Administration

#### Read The Man Pages

LVM has some of the *best man pages* ever put onto a Linux system. They are worth reading to understand
the options you have for commands!

> HINT: Some flavours of OpenSUSE may not have man pages. To fix this:

```
# $EDITOR /etc/zypp/zypp.conf
...
rpm.install.excludedocs = no
```

Ensure man is installed, and reinstall lvm2 to make sure it's man pages are present.

```
# zypper install -f man lvm2
```

#### OpenSUSE - Install LVM Tools

```
# zypper in lvm2
# reboot
```

> NOTE: In some cases you may need to install kernel-default so that dm-raid's kernel module exists.
> This can be because kernel-default-base may lack the module.

#### Show all Physical Volumes

```
# pvs
  PV         VG   Fmt  Attr PSize  PFree
  /dev/vdb   vg00 lvm2 a--  50.00g 50.00g
  /dev/vdc   vg00 lvm2 a--  50.00g 50.00g
  /dev/vdd   vg00 lvm2 a--  50.00g 50.00g
  /dev/vde   vg00 lvm2 a--  50.00g 50.00g
```

#### Show all Volume Groups

```
# vgs
  VG   #PV #LV #SN Attr   VSize   VFree
  vg00   4   0   0 wz--n- 199.98g 199.98g
```

#### Show all Logical Volumes

```
# lvs
  LV      VG   Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  lv_raid vg00 rwi-a-r--- 80.00g
```

Show the internal details of LVs

```
# lvs -a
  LV                 VG   Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  lv_raid            vg00 rwi-a-r--- 80.00g                                    18.80
  [lv_raid_rimage_0] vg00 Iwi-aor--- 40.00g
  [lv_raid_rimage_1] vg00 Iwi-aor--- 40.00g
  [lv_raid_rimage_2] vg00 Iwi-aor--- 40.00g
  [lv_raid_rmeta_0]  vg00 ewi-aor---  4.00m
  [lv_raid_rmeta_1]  vg00 ewi-aor---  4.00m
  [lv_raid_rmeta_2]  vg00 ewi-aor---  4.00m
```

Show the internal details of LVs and which devices are backing their storage.

```
# lvs -a -o +devices
  LV                 VG   Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert Devices
  lv_raid            vg00 rwi-a-r--- 80.00g                                    21.35            lv_raid_rimage_0(0),lv_raid_rimage_1(0),lv_raid_rimage_2(0)
  [lv_raid_rimage_0] vg00 Iwi-aor--- 40.00g                                                     /dev/vdb(1)
  [lv_raid_rimage_1] vg00 Iwi-aor--- 40.00g                                                     /dev/vdc(1)
  [lv_raid_rimage_2] vg00 Iwi-aor--- 40.00g                                                     /dev/vdd(1)
  [lv_raid_rmeta_0]  vg00 ewi-aor---  4.00m                                                     /dev/vdb(0)
  [lv_raid_rmeta_1]  vg00 ewi-aor---  4.00m                                                     /dev/vdc(0)
  [lv_raid_rmeta_2]  vg00 ewi-aor---  4.00m                                                     /dev/vdd(0)
```

### Using LVM For Raid

First you need to select your devices that will become the PV's

```
# lsblk
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINTS
sr0     11:0    1  372K  0 rom
vda    254:0    0   10G  0 disk
├─vda1 254:1    0    2M  0 part
├─vda2 254:2    0   33M  0 part /boot/efi
└─vda3 254:3    0   10G  0 part /
vdb    254:16   0   50G  0 disk ----
vdc    254:32   0   50G  0 disk | <-- I will use these 4 devices.
vdd    254:48   0   50G  0 disk |
vde    254:64   0   50G  0 disk ----
```

Create PVs on each member device.

```
# pvcreate /dev/vdb
# pvcreate /dev/disk/by-path/virtio-pci-0000\:09\:00.0
...
```

Create a VG containing all the PVs

```
vgcreate <name of vg> <path to pv> [<path to pv> ...]
# vgcreate vg00 /dev/vdb /dev/vdc /dev/vdd /dev/vde
```

Create a new LV that is at your prefered raid level.

* If you have two PV's choose raid 1
* If you have three or more choose between raid 5 or raid 10

In each case, LVM will make sure that the data of the LV is correctly split to PV's to ensure redundancy.

* Raid 1 mirrors. It has no performance changes.
* Raid 5/6 have better *write* performance but lower *read* performance compared to raid 10.
* Raid 10 has better *read* performance but lower *write* performance compared to raid 5/6

```
lvcreate [options] -n <name of LV> --type <type> [-L|-l] <size of lv> --raidintegrity y <VG to create the LV in>
## Create an lv that consumes all space in the VG
## NOTE: you may need to reduce this from 100% with raidintegrity to allow LVM the space
## to create the LV.
# lvcreate -n lv_raid --type raid10 -l 100%FREE --raidintegrity y vg00
## Create an lv that provides 80G of raid storage, but consumers more of the VG underneath
# lvcreate -n lv_raid --type raid5 -L 80G --raidintegrity y vg00
```

> HINT: The raidintegrity flag enables checksums of extents to allow detection of potential disk corruption

You can then use `lvs` to show the state of the sync process of the LV.

Once created you can make a new filesystem on the volume.

```
mkfs.<fs name> /dev/<vg name>/<lv name>
# mkfs.xfs /dev/vg00/lv_raid
```

This can then be added to `/etc/fstab` to mount on boot.

> HINT: `/dev/<vg name>/<lv name>` paths will never change and can be used reliably in fstab

```
# $EDITOR /etc/fstab
...
/dev/vg00/lv_raid  /mnt/raid    xfs defaults 0 0
```

### Managing LVM Raid

#### Replacing a Working Disk

If you want to expand your array, or just replace an old piece of disk media you can do this
live.

Attach the new disk and locate it with `lsblk`. Note it's name, path or other identifier.

Locate the disk you want to replace by it's path or identifier.

Create a new PV on the new disk.

```
# pvcreate /dev/vdf
```

Extend the VG with the new PV

```
# vgextend vg00 /dev/vdf
```

Check the pv was added to the vg

```
# pvs
```

Move the extents from the original device, to the new device.

```
## This blocks and monitors the move. If you ctrl-c it continues in the background.
# pvmove /dev/vde /dev/vdf
## Run the move in the background
# pvmove -b /dev/vde /dev/vdf
```

If backgrounded, you can monitor the move with:

```
# lvs -a
```

#### Replacing a Corrupted/Missing Disk

When checking lvs if a disk is corrupted or missing you will see errors such as:

```
# lvs
  WARNING: Couldn't find device with uuid weDidc-rBve-EL25-NqTG-X2n6-fGmW-FGCs9l.
  WARNING: VG vg00 is missing PV weDidc-rBve-EL25-NqTG-X2n6-fGmW-FGCs9l (last written to /dev/vdd).
  WARNING: Couldn't find all devices for LV vg00/lv_raid_rimage_2 while checking used and assumed devices.
  WARNING: Couldn't find all devices for LV vg00/lv_raid_rmeta_2 while checking used and assumed devices.
  LV      VG   Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
  lv_raid vg00 rwi-a-r-p- 99.98g                                    100.00
```

Create a new PV on a replacement disk, and add it to the vg.

```
# pvcreate /dev/path/to/disk
# vgextend vg00 /dev/path/to/disk
```

The logical volume must be active to initiate the replacement:

```
# lvchange -ay vg00/lv_raid
```

Replace the failed device allocating the needed extents.

```
## To any free device in the VG
# lvconvert --repair vg00/lv_raid
## To a specific PV
# lvconvert --repair vg00/lv_raid /dev/vde
```

You can view the progress of the repair with `lvs`

Instruct the vg to remove the missing device metadata now that the replacement is complete.

```
# vgreduce --removemissing vg00
```

