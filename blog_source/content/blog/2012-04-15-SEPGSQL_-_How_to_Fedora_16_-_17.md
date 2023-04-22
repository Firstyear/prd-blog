+++
title = "SEPGSQL - How to Fedora 16 - 17"
date = 2012-04-15
slug = "2012-04-15-SEPGSQL_-_How_to_Fedora_16_-_17"
# This is relative to the root!
aliases = [ "2012/04/15/SEPGSQL_-_How_to_Fedora_16_-_17.html", "blog/html/2012/04/15/SEPGSQL_-_How_to_Fedora_16_-_17.html" ]
+++
# SEPGSQL - How to Fedora 16 - 17

First, we install what we will be using.

    yum install postgresql postgresql-server postgresql-contrib 

First, we want to setup sepgsql. sepgsql.so is part of the contrib
package. These modules are installed on a per database basis, so we need
to initdb first

    postgresql-setup initdb

Edit vim /var/lib/pgsql/data/postgresql.conf +126

    shared_preload_libraries = 'sepgsql'            # (change requires restart)

Now, we need to re-label all the default postgres tables.

    su postgres
    export PGDATA=/var/lib/pgsql/data
    for DBNAME in template0 template1 postgres; do postgres --single -F -c exit_on_error=true $DBNAME /dev/null; done
    exit

Now we can start postgresql.

    systemctl start postgresql.service

Moment of truth - time to find out if we have selinux contexts in
postgresql.

    # su postgres
    # psql -U postgres postgres -c 'select sepgsql_getcon();'
    could not change directory to "/root"
                        sepgsql_getcon                     
    -------------------------------------------------------
     unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
    (1 row)

We can create a new database. Lets call it setest. We also add an apache
user for the django threads to connect to later. Finally, we want to
setup password authentication, and change ownership of the new setest db
to apache.

    createdb setest
    createuser 
    Enter name of role to add: apache
    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) n
    Shall the new role be allowed to create more new roles? (y/n) n
    psql -U postgres template1 -c "alter user apache with password 'password'"
    psql -U postgres template1 -c "alter user postgres with password 'password'"
    psql -U postgres template1 -c "alter database setest owner to apache"

Now we change our auth in postgres to be md5 in the file
\$PGDATA/pg_hdb.conf

    # "local" is for Unix domain socket connections only
    local   all             all                                     md5
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            md5
    # IPv6 local connections:
    host    all             all             ::1/128                 md5

    systemctl restart postgresql.service

Now you should be able to login in with a password as both users.

    # psql -U postgres -W
    Password for user postgres: 
    psql (9.1.3)
    Type "help" for help.

    postgres=# 
    # psql -U apache -W setest
    Password for user apache: 
    psql (9.1.3)
    Type "help" for help.

    setest=# 

Lets also take this chance, to take a look at the per column and per
table selinux permissions.

    psql -U postgres -W setest -c "SELECT objtype, objname, label FROM pg_seclabels WHERE provider = 'selinux' AND  objtype in ('table', 'column')"

To update these

    SECURITY LABEL FOR selinux ON TABLE mytable IS 'system_u:object_r:sepgsql_table_t:s0';

See
[also](http://www.postgresql.org/docs/9.1/static/sql-security-label.html).

This is very useful, especially if combined with my next blog post.
