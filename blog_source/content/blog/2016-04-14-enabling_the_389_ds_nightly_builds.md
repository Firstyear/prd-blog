+++
title = "Enabling the 389 ds nightly builds"
date = 2016-04-14
slug = "2016-04-14-enabling_the_389_ds_nightly_builds"
# This is relative to the root!
aliases = [ "2016/04/14/enabling_the_389_ds_nightly_builds.html", "blog/html/2016/04/14/enabling_the_389_ds_nightly_builds.html" ]
+++
# Enabling the 389 ds nightly builds

I maintain a copr repo which I try to keep update with \"nightly\"
builds of 389-ds.

You can use the following to enable them for EL7:

    sudo -s
    cd /etc/yum.repos.d
    wget https://copr.fedorainfracloud.org/coprs/firstyear/ds/repo/epel-7/firstyear-ds-epel-7.repo
    wget https://copr.fedorainfracloud.org/coprs/firstyear/svrcore/repo/epel-7/firstyear-svrcore-epel-7.repo
    wget https://copr.fedorainfracloud.org/coprs/firstyear/rest389/repo/epel-7/firstyear-rest389-epel-7.repo
    wget https://copr.fedorainfracloud.org/coprs/firstyear/lib389/repo/epel-7/firstyear-lib389-epel-7.repo
    yum install python-lib389 python-rest389 389-ds-base

