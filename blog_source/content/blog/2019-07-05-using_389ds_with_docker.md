+++
title = "Using 389ds with docker"
date = 2019-07-05
slug = "2019-07-05-using_389ds_with_docker"
# This is relative to the root!
aliases = [ "2019/07/05/using_389ds_with_docker.html", "blog/html/2019/07/05/using_389ds_with_docker.html" ]
+++
# Using 389ds with docker

I\'ve been wanting to containerise 389 Directory Server for a long
time - it\'s been a long road to get here, but I think that our
container support is getting very close to a production ready and
capable level. It took so long due to health issues and generally my
obsession to do everything right.

Today, container support along with our new command line tools makes 389
a complete breeze to administer. So lets go through an example of a
deployment now.

Please note: the container image here is a git-master build and is not
production ready as of 2019-07, hopefully this changes soon.

## Getting the Container

    docker pull firstyear/389ds:latest

If you want to run an ephemeral instance (IE you will LOSE all your data
on a restart)

    docker run firstyear/389ds:latest

If you want your data to persist, you need to attach a volume at /data:

    docker volume create 389ds_data
    docker run -v 389ds_data:/data firstyear/389ds:latest

The image exposes ports 3389 and 3636, so you may want to consider
publishing these if you want external access.

The container should now setup and run an instance! That\'s it, LDAP has
never been easier to deploy!

## Actually Adding Some Data \...

LDAP only really matters if we have some data! So we\'ll create a new
backend. You need to run these instructions inside the current
container, so I prefix these with:

    docker exec -i -t <name of container> <command>
    docker exec -i -t 389inst dsconf ....

This uses the ldapi socket via /data, and authenticates you based on
your process uid to map you to the LDAP administrator account -
basically, it\'s secure, host only admin access to your data.

Now you can choose any suffix you like, generally based on your dns name
(IE I use dc=blackhats,dc=net,dc=au).

    dsconf localhost backend create --suffix dc=example,dc=com --be-name userRoot
    > The database was sucessfully created

Now fill in the suffix details into your configuration of the container.
You\'ll need to find where docker stores the volume on your host for
this (docker inspect will help you). My location is listed here:

    vim /var/lib/docker/volumes/389ds_data/_data/config/container.inf

    --> change
    # basedn ...
    --> to
    basedn = dc=example,dc=com

Now you can populate data into that: The dsidm command is our tool to
manage users and groups of a backend, and it can provide initialised
data which has best-practice aci\'s, demo users and groups and starts as
a great place for you to build an IDM system.

    dsidm localhost initialise

That\'s it! You can now see you have a user and a group!

    dsidm localhost user list
    > demo_user
    dsidm localhost group list
    > demo_group

You can create your own user:

    dsidm localhost user create --uid william --cn William --displayName 'William Brown' --uidNumber 1000 --gidNumber 1000 --homeDirectory /home/william
    > Successfully created william
    dsidm localhost user get william

It\'s trivial to add an ssh key to the user:

    dsidm localhost user modify william add:nsSshPublicKey:AAA...
    > Successfully modified uid=william,ou=people,dc=example,dc=com

Or to add them to a group:

    dsidm localhost group add_member demo_group uid=william,ou=people,dc=example,dc=com
    > added member: uid=william,ou=people,dc=example,dc=com
    dsidm localhost group members demo_group
    > dn: uid=william,ou=people,dc=example,dc=com

Finally, we can even generale config templates for your applications:

    dsidm localhost client_config sssd.conf
    dsidm localhost client_config ldap.conf
    dsidm localhost client_config display

I\'m happy to say, LDAP administration has never been easier - we plan
to add more functionality to enabled broader ranges of administrative
tasks, especially in the IDM area and management of the configuration.
It\'s honestly hard to beleve that in a shortlist of commands you can
now have a fully functional LDAP IDM solution working.

