+++
title = "Akonadi mariadb on ZFS"
date = 2013-05-24
slug = "2013-05-24-Akonadi_mariadb_on_ZFS"
# This is relative to the root!
aliases = [ "2013/05/24/Akonadi_mariadb_on_ZFS.html", "blog/html/2013/05/24/Akonadi_mariadb_on_ZFS.html" ]
+++
# Akonadi mariadb on ZFS

I have recently bit the bullet and decided to do some upgrades to my
laptop. The main focus was getting ZFS as my home drive.

In doing so Akonadi, the PIM service for kmail broke.

After some investigation, it is because zfs does not support AIO with
maria db.

To fix this add to \~/.local/share/akonadi/myself.conf :

    innodb_use_native_aio=0
