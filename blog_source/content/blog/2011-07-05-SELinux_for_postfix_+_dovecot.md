+++
title = "SELinux for postfix + dovecot"
date = 2011-07-05
slug = "2011-07-05-SELinux_for_postfix_+_dovecot"
# This is relative to the root!
aliases = [ "2011/07/05/SELinux_for_postfix_+_dovecot.html" ]
+++
# SELinux for postfix + dovecot

> I am currently in the middle of creating an email solution for the
> doctors surgery that I work for. I have previously tried exchange, but
> found it to slow, and unreliable for my needs. Instead, I have decided
> to go with postfix + dovecot for the doctors needs.

In my experimenting, I have been using a fedora VM, with SElinux
enabled. However, SELinux has decided to hate on everything I do for
this, and thus in my inability to accept defeat, I have created an
SELinux module that should allow postfix and dovecot to work as per
following [this email setup
guide](http://www.1a-centosserver.com/centos_linux_mail_server/centos_mail_server.php).

the module is

    module postfixmysql 1.0;

    require {
        type mysqld_var_run_t;
        type postfix_map_t;
        type usr_t;
        type mysqld_t;
        type mysqld_db_t;
        type postfix_virtual_t;
        type postfix_smtpd_t;
        type postfix_cleanup_t;
        class sock_file write;
        class unix_stream_socket connectto;
        class file getattr;
        class dir search;
    }

    #============= postfix_cleanup_t ==============
    allow postfix_cleanup_t mysqld_db_t:dir search;
    allow postfix_cleanup_t mysqld_t:unix_stream_socket connectto;
    allow postfix_cleanup_t mysqld_var_run_t:sock_file write;
    allow postfix_cleanup_t usr_t:file getattr;

    #============= postfix_map_t ==============
    allow postfix_map_t mysqld_db_t:dir search;
    allow postfix_map_t mysqld_t:unix_stream_socket connectto;
    allow postfix_map_t mysqld_var_run_t:sock_file write;

    #============= postfix_smtpd_t ==============
    allow postfix_smtpd_t mysqld_db_t:dir search;
    allow postfix_smtpd_t mysqld_t:unix_stream_socket connectto;
    allow postfix_smtpd_t mysqld_var_run_t:sock_file write;

    #============= postfix_virtual_t ==============
    allow postfix_virtual_t mysqld_db_t:dir search;
    allow postfix_virtual_t mysqld_t:unix_stream_socket connectto;
    allow postfix_virtual_t mysqld_var_run_t:sock_file write;

This can be built and installed with a command like such (as root)

    checkmodule -M -m -o postfixmysql.mod postfixmysql.te; semodule_package -m postfixmysql.mod -o postfixmysql.pp; semodule -i postfixmysql.pp 
