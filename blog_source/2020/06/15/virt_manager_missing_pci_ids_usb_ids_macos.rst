virt-manager missing pci.ids usb.ids macos
==========================================

I got the following error:

::

    /usr/local/Cellar/libosinfo/1.8.0/share/libosinfo/pci.ids No such file or directory


This appears to be an issue in libosinfo from homebrew. Looking at the libosinfo source, there
are some aux download files. You can fix this with:

::

    mkdir -p /usr/local/Cellar/libosinfo/1.8.0/share/libosinfo/
    cd /usr/local/Cellar/libosinfo/1.8.0/share/libosinfo/
    wget -q -O pci.ids http://pciids.sourceforge.net/v2.2/pci.ids
    wget -q -O usb.ids http://www.linux-usb.org/usb.ids

All is happy again with virt-manager



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
