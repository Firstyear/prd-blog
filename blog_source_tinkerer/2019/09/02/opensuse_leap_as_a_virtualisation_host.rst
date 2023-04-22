OpenSUSE leap as a virtualisation host
======================================

I've been rebuilding my network to use SUSE from CentOS, and the final server was my hypervisor.
Most of the reason for this is the change in my employment, so I feel it's right to dogfood for
my workplace.

What you will need
------------------

* Some computer parts (assembaly may be required)
* OpenSUSE LEAP 15.1 media (dd if=opensuse.iso of=/dev/a_usb_i_hope)

What are we aiming for?
-----------------------

My new machine has dual NVME and dual 8TB spinning disks. The intent is to have the OS on the NVME
and to have a large part of the NVME act as LVM cache for the spinning disk. The host won't
run any applications beside libvirt, and has to connect a number of vlans over a link aggregation.

Useful commands
---------------

Through out this document I'll assume some details about your devices and partitions. To find your
own, and to always check and confirm what you are doing, some command will help:

::

    lsblk  # Shows all block storage devices, and how (if) they are mounted.
    lvs  # shows all active logical volumes
    vgs  # shows all active volume groups
    pvs  # shows all active physical volumes
    dmidecode  # show hardware information
    ls -al /dev/disk/by-<ID TYPE>/  # how to resolve disk path to a uuid etc.

I'm going to assume you have devices like:

::

    /dev/nvme0  # the first nvme of your system that you install to.
    /dev/nvme1  # the second nvme, used later
    /dev/sda    # Two larger block storage devices.
    /dev/sdb

Install
-------

Install and follow the prompts. Importantly when you install you install to a single NVME, and
choose transactional server + lvm, then put btrfs on the /root in the lvm. You want to
partition such that there is free space still in the NVME - I left about 400GB unpartitioned
for this. In other words, the disk should be like:

::

    [ /efi | pv + vg system               | pv (unused) ]
           | /root (btrfs), /boot, /home  |

Remember to leave about 1GB of freespace on the vg system to allow raid 1 metadata later!

Honestly, it may take you a try or two to get this right with YaST, and it was probably the
trickiest part of the install.

You should also select that network management is via networkmanager, not wicked. You may want
to enable ssh here. I disabled the firewall personally because there are no applications and
it interfers with the bridging for the vms.

Packages
--------

Because this is suse transactional we need to add packages and reboot each time. Here is
what I used, but you may find you don't need everything here:

::

    transactional-update pkg install libvirt libvirt-daemon libvirt-daemon-qemu \
      sssd sssd-ad sssd-ldap sssd-tools docker zsh ipcalc python3-docker rdiff-backup \
      vim rsync iotop tmux fwupdate fwupdate-efi bridge-utils qemu-kvm apcupsd

Reboot, and you are ready to partition.

Partitioning - post install
---------------------------

First, copy your gpt from the first NVME to the second. You can do this by hand with:

::

    gdisk /dev/nvme0
    p
    q

    gdisk /dev/nvme1
    c
    <duplicate the parameters as required>

Now we'll make your /efi at least a little redundant

::

    mkfs.fat /dev/nvme1p0
    ls -al /dev/disk/by-uuid/
    # In the above, look for your new /efi fs, IE CE0A-2C1D -> ../../nvme1n1p1
    # Now add a line to /etc/fstab like:
    UUID=CE0A-2C1D    /boot/efi2              vfat   defaults                      0  0

Now to really make this work, because it's transactional, you have to make a change to the
/root, which is readonly! To do this run

::

    transactional-update shell dup

This put's you in a shell at the end. Run:

::

    mkdir /boot/efi2

Now reboot. After the reboot your second efi should be mounted. rsync /boot/efi/* to /boot/efi2/. I
leave it to the reader to decide how to sync this periodically.

Next you can setup the raid 1 mirror for /root and the system vg.

::

    pvcreate /dev/nvme1p1
    vgextend system /dev/nvme1p1

Now we have enough pvs to make a raid 1, so we convert all our volumes:

::

    lvconvert --type raid1 --mirrors 1 system/home
    lvconvert --type raid1 --mirrors 1 system/root
    lvconvert --type raid1 --mirrors 1 system/boot

If this fails with "not enough space to alloc metadata", it's because you didn't leave space on
the vg during install. Honestly, I made this mistake twice due to confusion about things leading to
two reinstalls ...

Getting ready to cache
----------------------

Now lets get ready to cache some data. We'll make pvs and vgs for data:

::

    pvcreate /dev/nvme0p2
    pvcreate /dev/nvme1p2
    pvcreate /dev/sda1
    pvcreate /dev/sda2
    vgcreate data /dev/nvme0p2 /dev/nvme1p2 /dev/sda1 /dev/sdb2

Create the larger volume

::

    lvcreate --type raid1 --mirrors 1 -L7.5T -n libvirt_t2 data /dev/sda1 /dev/sdb1

Prepare the caches

::

    lvcreate --type raid1 --mirrors 1 -L 4G -n libvirt_t2_meta data
    lvcreate --type raid1 --mirrors 1 -L 400G -n libvirt_t2_cache data
    lvconvert --type cache-pool --poolmetadata data/libvirt_t2_meta data/libvirt_t2_cache

Now put the caches in front of the disks. It's important for you to check you have the correct cachemode
at this point, because you can't change it without removing and re-adding the cache. I choose writeback
because my nvme devices are in a raid 1 mirror, and it helps to accelerate writes. You may err to use
the default where the SSD's are read cache only.

::

    lvconvert --type cache --cachemode writeback --cachepool data/libvirt_t2_cache data/libvirt_t2
    mkfs.xfs /dev/mapper/data-libvirt_t2

You can monitor the amount of "cached" data in the data column of lvs.

Now you can add this to /etc/fstab as any other xfs drive. I mounted it to /var/lib/libvirt/images.

Network Manager
---------------

Now, I have to assemble the network bridges. Network Manager has some specific steps to follow to
achieve this. I have:

* two intel gigabit ports
* the ports are link aggregated by 802.3ad
* there are multiple vlans ontop of the link agg
* bridges must be built on top of the vlans

This requires a specific set of steps to layer this, because network manager sees the bridge and
the lagg as seperate things that require the vlan to tie them together.

Configure the link agg, and add our two ethernet phys

::

    nmcli conn add type bond con-name bond0 ifname bond0 mode 802.3ad ipv4.method disabled ipv6.method ignore
    nmcli connection add type ethernet con-name bond0-eth1 ifname eth1 master bond0 slave-type bond
    nmcli connection add type ethernet con-name bond0-eth2 ifname eth2 master bond0 slave-type bond

Add a bridge for a vlan:

::

    nmcli connection add type bridge con-name net_18 ifname net_18 ipv4.method disabled ipv6.method ignore

Now tie together a vlan on the bond, to the bridge we created.

::

    nmcli connection add type vlan con-name bond0.18 ifname bond0.18 dev bond0 id 18 master net_18 slave-type bridge

You will need to repeat these last two commands as required for the vlans you have.

House Keeping
-------------

Finally you need to do some house keeping. Transactional server will automatically reboot and update
so you need to be ready for this. You may disable this with:

::

    systemctl disable transactional-update.timer

You likely want to edit:

::

    /etc/sysconfig/libvirt-guests

To be able to handle guest shutdown policy due to a UPS failure or a reboot.

Now you can enable and start libvirt:

::

    systemctl enable libvirtd
    systemctl start libvirtd

Finally you can build and import virtualmachines.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
