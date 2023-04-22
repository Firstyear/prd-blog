+++
title = "GDB autoloads for 389 DS"
date = 2019-04-03
slug = "2019-04-03-gdb_autoloads_for_389_ds"
# This is relative to the root!
aliases = [ "2019/04/03/gdb_autoloads_for_389_ds.html", "blog/html/2019/04/03/gdb_autoloads_for_389_ds.html" ]
+++
# GDB autoloads for 389 DS

I\'ve been writing a set of extensions to help debug 389-ds a bit
easier. Thanks to the magic of python, writing GDB extensions is really
easy.

On OpenSUSE, when you start your DS instance under GDB, all of the
extensions are automatically loaded. This will help make debugging a
breeze.

    zypper in 389-ds gdb
    gdb /usr/sbin/ns-slapd

    GNU gdb (GDB; openSUSE Tumbleweed) 8.2
    (gdb) ds-
    ds-access-log  ds-backtrace
    (gdb) set args -d 0 -D /etc/dirsrv/slapd-<instance name>
    (gdb) run
    ...

All the extensions are under the ds- namespace, so they are easy to
find. There are some new ones on the way, which I\'ll discuss here too:

## ds-backtrace

As DS is a multithreaded process, it can be really hard to find the
active thread involved in a problem. So we provided a command that knows
how to fold duplicated stacks, and to highlight idle threads that you
can (generally) skip over.

    ===== BEGIN ACTIVE THREADS =====
    Thread 37 (LWP 70054))
    Thread 36 (LWP 70053))
    Thread 35 (LWP 70052))
    Thread 34 (LWP 70051))
    Thread 33 (LWP 70050))
    Thread 32 (LWP 70049))
    Thread 31 (LWP 70048))
    Thread 30 (LWP 70047))
    Thread 29 (LWP 70046))
    Thread 28 (LWP 70045))
    Thread 27 (LWP 70044))
    Thread 26 (LWP 70043))
    Thread 25 (LWP 70042))
    Thread 24 (LWP 70041))
    Thread 23 (LWP 70040))
    Thread 22 (LWP 70039))
    Thread 21 (LWP 70038))
    Thread 20 (LWP 70037))
    Thread 19 (LWP 70036))
    Thread 18 (LWP 70035))
    Thread 17 (LWP 70034))
    Thread 16 (LWP 70033))
    Thread 15 (LWP 70032))
    Thread 14 (LWP 70031))
    Thread 13 (LWP 70030))
    Thread 12 (LWP 70029))
    Thread 11 (LWP 70028))
    Thread 10 (LWP 70027))
    #0  0x00007ffff65db03c in pthread_cond_wait@@GLIBC_2.3.2 () at /lib64/libpthread.so.0
    #1  0x00007ffff66318b0 in PR_WaitCondVar () at /usr/lib64/libnspr4.so
    #2  0x00000000004220e0 in [IDLE THREAD] connection_wait_for_new_work (pb=0x608000498020, interval=4294967295) at /home/william/development/389ds/ds/ldap/servers/slapd/connection.c:970
    #3  0x0000000000425a31 in connection_threadmain () at /home/william/development/389ds/ds/ldap/servers/slapd/connection.c:1536
    #4  0x00007ffff6637484 in None () at /usr/lib64/libnspr4.so
    #5  0x00007ffff65d4fab in start_thread () at /lib64/libpthread.so.0
    #6  0x00007ffff6afc6af in clone () at /lib64/libc.so.6

This example shows that there are 17 idle threads (look at frame 2)
here, that all share the same trace.

## ds-access-log

The access log is buffered before writing, so if you have a coredump,
and want to see the last few events *before* they were written to disk,
you can use this to display the content:

    (gdb) ds-access-log
    ===== BEGIN ACCESS LOG =====
    $2 = 0x7ffff3c3f800 "[03/Apr/2019:10:58:42.836246400 +1000] conn=1 fd=64 slot=64 connection from 127.0.0.1 to 127.0.0.1
    [03/Apr/2019:10:58:42.837199400 +1000] conn=1 op=0 BIND dn=\"\" method=128 version=3
    [03/Apr/2019:10:58:42.837694800 +1000] conn=1 op=0 RESULT err=0 tag=97 nentries=0 etime=0.0001200300 dn=\"\"
    [03/Apr/2019:10:58:42.838881800 +1000] conn=1 op=1 SRCH base=\"\" scope=2 filter=\"(objectClass=*)\" attrs=ALL
    [03/Apr/2019:10:58:42.839107600 +1000] conn=1 op=1 RESULT err=32 tag=101 nentries=0 etime=0.0001070800
    [03/Apr/2019:10:58:42.840687400 +1000] conn=1 op=2 UNBIND
    [03/Apr/2019:10:58:42.840749500 +1000] conn=1 op=2 fd=64 closed - U1
    ", '\276' <repeats 3470 times>

At the end the line that repeats shows the log is \"empty\" in that
segment of the buffer.

## ds-entry-print

This command shows the in-memory entry. It can be common to see
Slapi_Entry \* pointers in the codebase, so being able to display these
is really helpful to isolate what\'s occuring on the entry. Your first
argument should be the Slapi_Entry pointer.

    (gdb) ds-entry-print ec
    Display Slapi_Entry: cn=config
    cn: config
    objectClass: top
    objectClass: extensibleObject
    objectClass: nsslapdConfig
    nsslapd-schemadir: /opt/dirsrv/etc/dirsrv/slapd-standalone1/schema
    nsslapd-lockdir: /opt/dirsrv/var/lock/dirsrv/slapd-standalone1
    nsslapd-tmpdir: /tmp
    nsslapd-certdir: /opt/dirsrv/etc/dirsrv/slapd-standalone1
    ...

