+++
title = "Ovirt with ldap authentication source"
date = 2015-07-15
slug = "2015-07-15-Ovirt_with_ldap_authentication_source"
# This is relative to the root!
aliases = [ "2015/07/15/Ovirt_with_ldap_authentication_source.html", "blog/html/2015/07/15/Ovirt_with_ldap_authentication_source.html" ]
+++
# Ovirt with ldap authentication source

I want ovirt to auth to our work\'s ldap server, but the default engine
domain system expects you to have kerberos. There is however a new AAA
module that you can use.

First, install it

    yum install ovirt-engine-extension-aaa-ldap

So we have a look at the package listing to see what could be a good
example:

    rpm -ql ovirt-engine-extension-aaa-ldap
    ....
    /usr/share/ovirt-engine-extension-aaa-ldap/examples/simple/

So we copy our example in place:

    cp -r /usr/share/ovirt-engine-extension-aaa-ldap/examples/simple/* /etc/ovirt-engine/

Now we edit the values in /etc/ovirt-engine/aaa/profile1.properties to
match our site, then restart the engine service.

Finally, we need to login is as our admin user, then go to configure and
assign our user a role. This should allow them to login.

I\'m seeing some issues with group permissions at the moment, but I
suspect that is a schema mismatch issue.

This was a really valuable resource.

[access.redhat.com](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Virtualization/3.5/html/Administration_Guide/sect-Directory_Users.html).
