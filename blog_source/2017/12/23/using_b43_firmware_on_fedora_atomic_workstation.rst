Using b43 firmware on Fedora Atomic Workstation
===============================================

My Macbook Pro has a broadcom b43 wireless chipset. This is notorious for being one of the most annoying wireless adapters on linux. When you first install Fedora you don’t even see “wifi” as an option, and unless you poke around in dmesg, you won’t find how to enable b43 to work on your platform.

b43
---

The b43 driver requires proprietary firmware to be loaded else the wifi chip will not run. There are a number of steps for this process found on the linux wireless page . You’ll note that one of the steps is:

::

    export FIRMWARE_INSTALL_DIR="/lib/firmware"
    ...
    sudo b43-fwcutter -w "$FIRMWARE_INSTALL_DIR" broadcom-wl-5.100.138/linux/wl_apsta.o

So we need to be able to write and extract our firmware to /usr/lib/firmware, and then reboot and out wifi works.

Fedora Atomic Workstation
-------------------------

Atomic WS is similar to atomic server, that it’s a read-only ostree based deployment of fedora. This comes with a number of unique challenges and quirks but for this issue:

::

    sudo touch /usr/lib/firmware/test
    /bin/touch: cannot touch '/usr/lib/firmware/test': Read-only file system

So we can’t extract our firmware!

Normally linux also supports reading from /usr/local/lib/firmware (which on atomic IS writeable ...) but for some reason fedora doesn’t allow this path.

Solution: Layered RPMs
----------------------

Atomic has support for “rpm layering”. Ontop of the ostree image (which is composed of rpms) you can supply a supplemental list of packages that are “installed” at rpm-ostree update time.

This way you still have an atomic base platform, with read-only behaviours, but you gain the ability to customise your system. To achive it, it must be possible to write to locations in /usr during rpm install.

This means our problem has a simple solution: Create a b43 rpm package. Note, that you can make this for yourself privately, but you can’t distribute it for legal reasons.

Get setup on atomic to build the packages:

::

    rpm-ostree install rpm-build createrepo
    reboot

RPM specfile:

::
    %define debug_package %{nil}
    Summary: Allow b43 fw to install on ostree installs due to bz1512452
    Name: b43-fw
    Version: 1.0.0
    Release: 1
    License: Proprietary, DO NOT DISTRIBUTE BINARY FORMS
    URL: http://linuxwireless.sipsolutions.net/en/users/Drivers/b43/
    Group: System Environment/Kernel

    BuildRequires: b43-fwcutter

    Source0: http://www.lwfinger.com/b43-firmware/broadcom-wl-5.100.138.tar.bz2

    %description
    Broadcom firmware for b43 chips.

    %prep
    %setup -q -n broadcom-wl-5.100.138

    %build
    true

    %install
    pwd
    mkdir -p %{buildroot}/usr/lib/firmware
    b43-fwcutter -w %{buildroot}/usr/lib/firmware linux/wl_apsta.o

    %files
    %defattr(-,root,root,-)
    %dir %{_prefix}/lib/firmware/b43
    %{_prefix}/lib/firmware/b43/*

    %changelog
    * Fri Dec 22 2017 William Brown <william at blackhats.net.au> - 1.0.0
    - Initial version

Now you can put this into a folder like so:

::

    mkdir -p ~/rpmbuild/{SPECS,SOURCES}
    <editor> ~/rpmbuild/SPECS/b43-fw.spec
    wget -O ~/rpmbuild/SOURCES/broadcom-wl-5.100.138.tar.bz2 http://www.lwfinger.com/b43-firmware/broadcom-wl-5.100.138.tar.bz2

We are now ready to build!

::

    rpmbuild -bb ~/rpmbuild/SPECS/b43-fw.spec
    createrepo ~/rpmbuild/RPMS/x86_64/

Finally, we can install this. Create a yum repos file:

::

    [local-rpms]
    name=local-rpms
    baseurl=file:///home/<YOUR USERNAME HERE>/rpmbuild/RPMS/x86_64
    enabled=1
    gpgcheck=0
    type=rpm

::

    rpm-ostree install b43-fw

Now reboot and enjoy wifi on your Fedora Atomic Macbook Pro!


.. author:: default
.. categories:: none
.. tags:: none
.. comments::


