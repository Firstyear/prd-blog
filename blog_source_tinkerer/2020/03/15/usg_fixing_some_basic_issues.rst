USG fixing avahi
================

Sadly on the USG pro 4 avahi will regularly spiral out of control taking up 100%
cpu. To fix this, we set an hourly restart:

::

    sudo -s
    crontab -e

Then add:

::

    15 * * * * /usr/sbin/service avahi-daemon restart



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
