+++
title = "Using the latest 389-ds on OpenSUSE"
date = 2019-01-30
slug = "2019-01-30-using_the_latest_389_ds_on_opensuse"
# This is relative to the root!
aliases = [ "2019/01/30/using_the_latest_389_ds_on_opensuse.html" ]
+++
# Using the latest 389-ds on OpenSUSE

Thanks to some help from my friend who works on OBS, I\'ve finally got a
good package in review for submission to tumbleweed. However, if you are
impatient and want to use the \"latest\" and greatest 389-ds version on
OpenSUSE.

    zypper ar obs://network:ldap network:ldap
    zypper in 389-ds

## Docker

    docker run --rm -i -t registry.opensuse.org/home/firstyear/containers/389-ds-container:latest

To make it persistent:

    docker run -v 389ds_data:/data <your options here ...> registry.opensuse.org/home/firstyear/containers/389-ds-container:latest

Then to run the admin tools:

    docker exec -i -t <container name> /usr/sbin/dsconf ...
    docker exec -i -t <container name> /usr/sbin/dsidm ...

## Testing in docker?

If you are \"testing\" in docker (please don\'t do this in production:
for production see above) you\'ll need to do some tweaks to get around
the lack of systemd.

    docker run -i -t opensuse/tumbleweed:latest
    zypper ar obs://network:ldap network:ldap
    zypper in 389-ds

    vim /usr/share/dirsrv/inf/defaults.inf
    # change the following to match:
    with_systemd = 0

## What next?

After this, you should now be able to follow our [new quickstart
guide](http://www.port389.org/docs/389ds/howto/quickstart.html) on the
389-ds website.

If you followed the docker steps, skip to [adding users and
groups](http://www.port389.org/docs/389ds/howto/quickstart.html#add-users-and-groups)

The network:ldap repo and the container listed are updated when upstream
makes releases so you\'ll always get the latest 389-ds

EDIT: Updated 2019-04-03 to change repo as changes have progressed
forward.

EDIT: Updated 2019-08-27 Improve clarity about when you need to do
docker tweaks, and add docker image steps

