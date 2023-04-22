+++
title = "389ds in containers"
date = 2020-03-28
slug = "2020-03-28-389ds_in_containers"
# This is relative to the root!
aliases = [ "2020/03/28/389ds_in_containers.html", "blog/html/2020/03/28/389ds_in_containers.html" ]
+++
# 389ds in containers

I\'ve spent a number of years working in the background to get 389-ds
working in containers. I think it\'s very close to production ready
([one issue outstanding!](https://pagure.io/389-ds-base/issue/50989))
and I\'m now using it at home for my production LDAP needs.

So here\'s a run down on using 389ds in a container!

## Getting it Started

The team provides an image for pre-release testing which you can get
with docker pull:

    docker pull 389ds/dirsrv:latest
    # OR, if you want to be pinned to the 1.4 release series.
    docker pull 389ds/dirsrv:1.4

The image can be run in an ephemeral mode (data will be lost on stop of
the container) so you can test it:

    docker run 389ds/dirsrv:1.4

## Making it Persistent

To make your data persistent, you\'ll need to add a volume, and bind it
to the container.

    docker volume create 389ds

You can run 389ds where the container instance is removed each time the
container stops, but the data persists (I promise this is safe!) with:

    docker run --rm -v 389ds:/data -p 3636:3636 389ds/dirsrv:latest

Check your instance is working with an ldapsearch:

    LDAPTLS_REQCERT=never ldapsearch -H ldaps://127.0.0.1:3636 -x -b '' -s base vendorVersion

*NOTE: Setting the environment variable \`LDAPTLS_REQCERT\` to \`never\`
disables CA verification of the LDAPS connection. Only use this in
testing environments!*

If you want to make the container instance permanent (uses docker
start/stop/restart etc) then you\'ll need to do a docker create with
similar arguments:

    docker create  -v 389ds:/data -p 3636:3636 389ds/dirsrv:latest
    docker ps -a
    CONTAINER ID        IMAGE                 ...  NAMES
    89b342c2e058        389ds/dirsrv:latest   ...  adoring_bartik

Remember, even if you rm the container instance, the volume stores all
the data so you can re-pull the image and recreate the container and
continue.

## Administering the Instance

The best way is to the use the local LDAPI socket - by default the
cn=Directory Manager password is randomised so that it can\'t be
accessed remotely.

To use the local LDAPI socket, you\'ll use docker exec into the running
instance.

    docker start <container name>
    docker exec -i -t <container name> /usr/sbin/dsconf localhost <cmd>
    docker exec -i -t <container name> /usr/sbin/dsconf localhost backend suffix list
    No backends

In a container, the instance is always named \"localhost\". So lets add
a database backend now to our instance:

    docker exec -i -t <cn> /usr/sbin/dsconf localhost backend create --suffix dc=example,dc=com --be-name userRoot
    The database was sucessfully created

You can even go ahead and populate your backend now. To make it easier,
specify your basedn into the volume\'s /data/config/container.inf. Once
that\'s done we can setup sample data (including access controls), and
create some users and groups.

    docker exec -i -t <cn> /bin/sh -c "echo -e '\nbasedn = dc=example,dc=com' >> /data/config/container.inf"
    docker exec -i -t <cn> /usr/sbin/dsidm localhost initialise
    docker exec -i -t <cn> /usr/sbin/dsidm localhost user create --uid william --cn william \
        --displayName William --uidNumber 1000 --gidNumber 1000 --homeDirectory /home/william
    docker exec -i -t <cn> /usr/sbin/dsidm localhost group create --cn test_group
    docker exec -i -t <cn> /usr/sbin/dsidm localhost group add_member test_group uid=william,ou=people,dc=example,dc=com
    docker exec -i -t <cn> /usr/sbin/dsidm localhost account reset_password uid=william,ou=people,dc=example,dc=com
    LDAPTLS_REQCERT=never ldapwhoami -H ldaps://127.0.0.1:3636 -x -D uid=william,ou=people,dc=example,dc=com -W
        Enter LDAP Password:
        dn: uid=william,ou=people,dc=example,dc=com

There is much more you can do with these tools of course, but it\'s very
easy to get started and working with an ldap server like this.

## Further Configuration

Because this runs in a container, the approach to some configuration is
a bit different. Some settings can be configured through either the
content of the volume, or through environment variables.

You can reset the directory manager password on startup but use the
environment variable DS_DM_PASSWORD. Of course, please use a better
password than \"password\". pwgen is a good tool for this! This password
persists across restarts, so you should make sure it\'s good.

    docker run --rm -e DS_DM_PASSWORD=password -v 389ds:/data -p 3636:3636 389ds/dirsrv:latest
    LDAPTLS_REQCERT=never ldapwhoami -H ldaps://127.0.0.1:3636 -x -D 'cn=Directory Manager' -w password
        dn: cn=directory manager

You can also configure certificates through pem files.

    /data/tls/server.key
    /data/tls/server.crt
    /data/tls/ca/*.crt

All the certs in /data/tls/ca/ will be imported as CA\'s and the server
key and crt will be used for the TLS server.

If for some reason you need to reindex your db at startup, you can use:

    docker run --rm -e DS_REINDEX=true -v 389ds:/data -p 3636:3636 389ds/dirsrv:latest

After the reindex is complete the instance will start like normal.

## Conclusion

389ds in a container is one of the easiest and quickest ways to get a
working LDAP environment today. Please test it and let us know what you
think!

