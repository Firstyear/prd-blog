+++
title = "Fixing opensuse virtual machines with resume"
date = 2019-12-15
slug = "2019-12-15-fixing_opensuse_virtual_machines_with_resume"
# This is relative to the root!
aliases = [ "2019/12/15/fixing_opensuse_virtual_machines_with_resume.html" ]
+++
# Fixing opensuse virtual machines with resume

Today I hit an unexpected issue - after changing a virtual machines root
disk to scsi, I was unable to boot the machine.

The host is opensuse leap 15.1, and the vm is the same. What\'s
happening!

The first issue appears to be that opensuse 15.1 doesn\'t support scsi
disks from libvirt. I\'m honestly not sure what\'s wrong here.

The second is that by default opensuse leap configures suspend and
resume to disk - by it uses the pci path instead of a swap volume UUID.
So when you change the bus type, it renames the path making the volume
inaccessible. This causes boot to fail.

To work around you can remove \"resume=/disk/path\" from the cli. Then
to fix it permanently you need:

    transactional-update shell
    vim /etc/default/grub
    # Edit this line to remove "resume"
    GRUB_CMDLINE_LINUX_DEFAULT="console=ttyS0,115200 resume=/dev/disk/by-path/pci-0000:00:07.0-part3 splash=silent quiet showopts"

    vim /etc/default/grub_installdevice
    # Edit the path to the correct swap location as by ls -al /dev/disk/by-path
    /dev/disk/by-path/pci-0000:00:07.0-part3

I have reported these issues, and I hope they are resolved.

