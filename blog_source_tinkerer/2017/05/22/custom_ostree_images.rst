Custom OSTree images
====================

`Project Atomic <https://www.projectatomic.io/>`_ is in my view, one of the most promising changes to come to linux distributions in a long time. It boasts the ability to atomicupgrade and alter your OS by maintaining A/B roots of the filesystem. It is currently focused on docker and k8s runtimes, but we can use atomic in other locations.

.. more::

Why?
----

I wanted to run atomic on my container hosts, but it wouldn't allow me to overlay amanda-client packages. Attempting to get amanda to work in a container with the root fs passed in was also quite a mess in itself. I was inspired to deploy a custom OSTree image of CentOS 7 which had my required packages added.

Saying this, I also like to blow away and reinstall hosts. I wanted to be able to to kickstart with virt install, making a new atomic host a 1 command process to deploy.

Limitations
-----------

Today, the treefile.json does not support arbitrary file permissions on injected content. I have raised the issue on github. What this prevents is injecting configs like sssd.conf - because the sssd.conf RPM owns the file, I can't have a "site" customisation RPM, and SSSD expects 600 perms on the file. Additionally, the postprocess-script, runs *before* file deployment, so you can not rely on it to correct permissions.

Process
-------

We'll assume you are running a CentOS7 hypervisor for this process. You'll need to pull out some repos from the `atomic sig repo <https://github.com/CentOS/sig-atomic-buildscripts/>`_ to access the ostree packages we need.

::

    [atomic7-testing]
    name=atomic7-testing
    baseurl=http://cbs.centos.org/repos/atomic7-testing/x86_64/os/
    gpgcheck=0
    exclude=atomic ostree rpm-ostree

    [atomic-centos-continuous]
    baseurl=https://ci.centos.org/artifacts/sig-atomic/rdgo/centos-continuous/build
    gpgcheck=0
    priority=1


Now you can install ostree and rpm-ostree to start the process:

::

    yum install -y ostree rpm-ostree

From the same repo, you can lift what you need to make a minimal centos image. I cloned then copied the centos resources `here <https://github.com/Firstyear/ansible-home/tree/master/roles/bh-libvirt/files/atomic-buildscripts>`_ as a template to base my images from. Using the docs on `treefiles <https://rpm-ostree.readthedocs.io/en/latest/manual/treefile/>`_ I was able to customise my `treefile specification <https://github.com/Firstyear/ansible-home/blob/master/roles/bh-libvirt/files/atomic-buildscripts/centos-atomic-host-test.json>`_ - notably adding documentation by default, and enabling the en_AU localisation (because I don't like the letter Z).

Almost there: We just need to setup the repo for our objects to land in, and setup apache.

::

    yum install -y httpd
    systemctl enable httpd
    cd /var/www/html && ostree --repo=repo init --mode=archive-z2

Now we can trigger the build of the OSTree image.

::

    http_proxy=http://proxy...:3128 rpm-ostree compose tree --repo=/var/www/html/repo /root/atomic-buildscripts/centos-atomic-host-test.json

That's it! Tree is built. If you want, you can use an existing host to consume this:

::

    ostree remote add testrepo http://192.168.122.20/repo/ --no-gpg-verify
    ostree remote refs testrepo
    ostree pull testrepo centos-atomic-host-test/7/x86_64/standard
    rpm-ostree status
    rpm-ostree rebase testrepo:centos-atomic-host-test/7/x86_64/standard

Kickstart and virt-install
--------------------------

But why stop there: I want to automatically deploy these images.

First, we need to get the kernel and boot images out we need. I used the latest centos-atomic-installer.iso. You can't use the normal centos images as they don't have the working anaconda support.

::

    # find /var/www/html/pub/centos/7/os/x86_64 
    /var/www/html/pub/centos/7/os/x86_64
    /var/www/html/pub/centos/7/os/x86_64/EFI
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/fonts
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/fonts/TRANS.TBL
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/fonts/unicode.pf2
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/BOOTX64.EFI
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/MokManager.efi
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/TRANS.TBL
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/grub.cfg
    /var/www/html/pub/centos/7/os/x86_64/EFI/BOOT/grubx64.efi
    /var/www/html/pub/centos/7/os/x86_64/LiveOS
    /var/www/html/pub/centos/7/os/x86_64/LiveOS/TRANS.TBL
    /var/www/html/pub/centos/7/os/x86_64/LiveOS/squashfs.img
    /var/www/html/pub/centos/7/os/x86_64/images
    /var/www/html/pub/centos/7/os/x86_64/images/pxeboot
    /var/www/html/pub/centos/7/os/x86_64/images/pxeboot/TRANS.TBL
    /var/www/html/pub/centos/7/os/x86_64/images/pxeboot/initrd.img
    /var/www/html/pub/centos/7/os/x86_64/images/pxeboot/upgrade.img
    /var/www/html/pub/centos/7/os/x86_64/images/pxeboot/vmlinuz
    /var/www/html/pub/centos/7/os/x86_64/images/TRANS.TBL
    /var/www/html/pub/centos/7/os/x86_64/images/efiboot.img
    /var/www/html/pub/centos/7/os/x86_64/isolinux
    /var/www/html/pub/centos/7/os/x86_64/isolinux/TRANS.TBL
    /var/www/html/pub/centos/7/os/x86_64/isolinux/boot.cat
    /var/www/html/pub/centos/7/os/x86_64/isolinux/boot.msg
    /var/www/html/pub/centos/7/os/x86_64/isolinux/grub.conf
    /var/www/html/pub/centos/7/os/x86_64/isolinux/initrd.img
    /var/www/html/pub/centos/7/os/x86_64/isolinux/isolinux.bin
    /var/www/html/pub/centos/7/os/x86_64/isolinux/isolinux.cfg
    /var/www/html/pub/centos/7/os/x86_64/isolinux/memtest
    /var/www/html/pub/centos/7/os/x86_64/isolinux/splash.png
    /var/www/html/pub/centos/7/os/x86_64/isolinux/upgrade.img
    /var/www/html/pub/centos/7/os/x86_64/isolinux/vesamenu.c32
    /var/www/html/pub/centos/7/os/x86_64/isolinux/vmlinuz

Now we need to get kickstart to work. I have configured one to look like below. Largely this is lifted from an atomic install's /root/anaconda-ks.conf.

::

    #### MUST CHANGE THIS
    network  --hostname=atomic.dev.blackhats.net.au

    #version=DEVEL
    # System authorization information
    auth --enableshadow --passalgo=sha512
    # OSTree setup
    ostreesetup --osname="centos-atomic-host-test" --remote="centos-blackhats-repo" --url="http://ostree.net.blackhats.net.au/repo" --ref="centos-atomic-host-test/7/x86_64/standard" --nogpg
    # Use graphical install
    text
    # Run the Setup Agent on first boot
    firstboot --disable
    ignoredisk --only-use=vda
    # Keyboard layouts
    keyboard --vckeymap=us-dvorak-alt-intl --xlayouts='us (dvorak-alt-intl)'
    # System language
    lang en_AU.UTF-8

    # Network information
    network --device=eth0 --bootproto=dhcp --ipv6=auto --activate


    #Root password
    rootpw --lock
    # System services
    services --disabled="cloud-init,cloud-config,cloud-final,cloud-init-local"
    # System timezone
    timezone Australia/Brisbane --isUtc
    user --groups=wheel --name=admin --password=... --iscrypted --gecos="admin"
    # System bootloader configuration
    bootloader --append=" crashkernel=auto" --location=mbr --boot-drive=vda
    # Partition clearing information
    clearpart --initlabel --all
    # Disk partitioning information
    part /boot --fstype=xfs --size=512 --asprimary --fsoptions=x-systemd.automount,nodev,nosuid,defaults
    # LVM
    part pv.2 --size=16896 --grow --asprimary
    volgroup vg00 pv.2
    logvol swap --fstype=swap --size=2048 --name=swap_lv --vgname=vg00
    #logvol /boot --fstype="xfs" --size=512 --name=boot_lv --vgname=vg00
    # This may be leaving some space on the PV?
    #logvol "none" --fstype="none" --name=tp00 --vgname=vg00 --grow --percent=100 --thinpool
    logvol / --fstype=xfs --size=8192 --name=root_lv --vgname=vg00 --fsoptions=defaults
    logvol /var/lib  --fstype=xfs --size=2048 --name=var_lv --vgname=vg00 --fsoptions=nodev,nosuid,noexec,defaults
    logvol /var/log --fstype="xfs" --size=1536 --name=var_log_lv --vgname=vg00 --fsoptions=nodev,nosuid,noexec,defaults
    # Can't mount /var seperately yet, see https://bugzilla.redhat.com/show_bug.cgi?id=1098303

    %post --erroronfail
    cp /etc/skel/.bash* /var/roothome
    fn=/etc/ostree/remotes.d/centos-atomic-host.conf; if test -f ${fn} && grep -q -e '^url=file:///install/ostree' ${fn}; then rm ${fn}; fi
    %end

    %packages
    kexec-tools

    %end

    %addon com_redhat_kdump --enable --reserve-mb='auto'
    %end

    %anaconda
    pwpolicy root --minlen=6 --minquality=50 --notstrict --nochanges --notempty
    pwpolicy user --minlen=6 --minquality=50 --notstrict --nochanges --notempty
    pwpolicy luks --minlen=6 --minquality=50 --notstrict --nochanges --notempty
    %end

The really critical line is this one:

::

    ostreesetup --osname="centos-atomic-host-test" --remote="centos-blackhats-repo" --url="http://ostree.net.blackhats.net.au/repo" --ref="centos-atomic-host-test/7/x86_64/standard" --nogpg

This lists the repo for ostree which has our tree output that we previously built, and tells anaconda to install it by default.

Finally we can configure this with virt install:

::

    #!/bin/bash
    if [ -z ${1} ]
    then
        echo "Must provide a VM name."
        exit 1
    fi

    DISKSIZE=20
    MIRROR=ostree.net.blackhats.net.au
    KSNAME=${1}.cfg
    KSPATH=/root/vmscripts/ks/${KSNAME}
    NETIF=net_servers
    CENTOS_VERSION=7

    virt-install --connect=qemu:///system -n $1 \
        --os-variant=rhel7 \
        --ram=2048 --vcpus=1 --security type=dynamic \
        --serial pty \
        --disk path=/var/lib/exports/t1/def_t1_nfs_sas/${1}.img,sparse=true,format=raw,bus=virtio,size=${DISKSIZE} \
        --location=http://${MIRROR}/pub/centos/7/os/x86_64/ \
        --network=bridge=${NETIF} \
        --extra-args "ks=http://${MIRROR}/ks/${KSNAME} console=ttyS0 cmdline ip=dhcp"


That's it: you can now use virsh console NAME to connect and see the install in process.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
