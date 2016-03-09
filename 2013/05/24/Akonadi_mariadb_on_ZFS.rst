Akonadi mariadb on ZFS
======================
I have recently bit the bullet and decided to do some upgrades to my laptop. The main focus was getting ZFS as my home drive. 

In doing so Akonadi, the PIM service for kmail broke. 

After some investigation, it is because zfs does not support AIO with maria db.

To fix this add to ~/.local/share/akonadi/myself.conf
::
    
    innodb_use_native_aio=0

