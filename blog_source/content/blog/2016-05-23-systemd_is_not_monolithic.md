+++
title = "systemd is not monolithic"
date = 2016-05-23
slug = "2016-05-23-systemd_is_not_monolithic"
# This is relative to the root!
aliases = [ "2016/05/23/systemd_is_not_monolithic.html" ]
+++
# systemd is not monolithic

Go ahead. Please read [this post by Lennart about systemd
myths](http://0pointer.de/blog/projects/the-biggest-myths.html). I\'ll
wait.

Done? Great. You noticed the first point. \"Systemd is monolithic\".
Which is carefully \"debunked\".

So this morning while building Ds, I noticed my compile failed:

    configure: checking for Systemd...
    checking for --with-systemd... using systemd native features
    checking for --with-journald... using journald logging: WARNING, this may cause system instability
    checking for pkg-config... (cached) /usr/bin/pkg-config
    checking for Systemd with pkg-config... configure: error: no Systemd / Journald pkg-config files
    Makefile:84: recipe for target 'ds-configure' failed

I hadn\'t changed this part of the code, and it\'s been reliably
compiling for me \... What changed?

Well on RHEL7 here is the layout of the system libraries:

    /usr/lib64/libsystemd-daemon.so
    /usr/lib64/libsystemd-id128.so
    /usr/lib64/libsystemd-journal.so
    /usr/lib64/libsystemd-login.so
    /usr/lib64/libsystemd.so
    /usr/lib64/libudev.so

They also each come with their own very nice pkg-config file so you can
find them.

    /usr/lib64/pkgconfig/libsystemd-daemon.pc
    /usr/lib64/pkgconfig/libsystemd-id128.pc
    /usr/lib64/pkgconfig/libsystemd-journal.pc
    /usr/lib64/pkgconfig/libsystemd-login.pc
    /usr/lib64/pkgconfig/libsystemd.pc
    /usr/lib64/pkgconfig/libudev.pc

Sure these are big libraries, but it\'s pretty modular. And it\'s nice
they are seperate out.

But today, I compiled on rawhide. What\'s changed:

    /usr/lib64/libsystemd.so
    /usr/lib64/libudev.so

    /usr/lib64/pkgconfig/libsystemd.pc
    /usr/lib64/pkgconfig/libudev.pc

I almost thought this was an error. Surely they put libsystemd-journald
into another package.

No. No they did not.

    I0> readelf -Ws /usr/lib64/libsystemd.so | grep -i journal_print
       297: 00000000000248c0   177 FUNC    GLOBAL DEFAULT   12 sd_journal_print@@LIBSYSTEMD_209
       328: 0000000000024680   564 FUNC    GLOBAL DEFAULT   12 sd_journal_printv@@LIBSYSTEMD_209
       352: 0000000000023d80   788 FUNC    GLOBAL DEFAULT   12 sd_journal_printv_with_location@@LIBSYSTEMD_209
       399: 00000000000240a0   162 FUNC    GLOBAL DEFAULT   12 sd_journal_print_with_location@@LIBSYSTEMD_209

So we went from these small modular libraries:

    -rwxr-xr-x. 1 root root  26K May 12 14:29 /usr/lib64/libsystemd-daemon.so.0.0.12
    -rwxr-xr-x. 1 root root  21K May 12 14:29 /usr/lib64/libsystemd-id128.so.0.0.28
    -rwxr-xr-x. 1 root root 129K May 12 14:29 /usr/lib64/libsystemd-journal.so.0.11.5
    -rwxr-xr-x. 1 root root  56K May 12 14:29 /usr/lib64/libsystemd-login.so.0.9.3
    -rwxr-xr-x. 1 root root 159K May 12 14:29 /usr/lib64/libsystemd.so.0.6.0

To this monolithic library:

    -rwxr-xr-x. 1 root root 556K May 22 14:09 /usr/lib64/libsystemd.so.0.15.0

\"Systemd is not monolithic\".

