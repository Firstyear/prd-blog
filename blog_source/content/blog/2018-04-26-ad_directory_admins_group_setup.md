+++
title = "AD directory admins group setup"
date = 2018-04-26
slug = "2018-04-26-ad_directory_admins_group_setup"
# This is relative to the root!
aliases = [ "2018/04/26/ad_directory_admins_group_setup.html" ]
+++
# AD directory admins group setup

Recently I have been reading many of the Microsoft Active Directory best
practices for security and hardening. These are great resources, and
very well written. The major theme of the articles is \"least
privilege\", where accounts like Administrators or Domain Admins are
over used and lead to further compromise.

A suggestion that is put forward by the author is to have a group that
has no other permissions but to manage the directory service. This
should be used to temporarily make a user an admin, then after a period
of time they should be removed from the group.

This way you have no Administrators or Domain Admins, but you have an AD
only group that can temporarily grant these permissions when required.

I want to explore how to create this and configure the correct access
controls to enable this scheme.

## Create our group

First, lets create a \"Directory Admins\" group which will contain our
members that have the rights to modify or grant other privileges.

    # /usr/local/samba/bin/samba-tool group add 'Directory Admins'
    Added group Directory Admins

It\'s a really good idea to add this to the \"Denied RODC Password
Replication Group\" to limit the risk of these accounts being
compromised during an attack. Additionally, you probably want to make
your \"admin storage\" group also a member of this, but I\'ll leave that
to you.

    # /usr/local/samba/bin/samba-tool group addmembers "Denied RODC Password Replication Group" "Directory Admins"

Now that we have this, lets add a member to it. I strongly advise you
create special accounts just for the purpose of directory
administration - don\'t use your daily account for this!

    # /usr/local/samba/bin/samba-tool user create da_william
    User 'da_william' created successfully
    # /usr/local/samba/bin/samba-tool group addmembers 'Directory Admins' da_william
    Added members to group Directory Admins

## Configure the permissions

Now we need to configure the correct dsacls to allow Directory Admins
full control over directory objects. It could be possible to constrain
this to *only* modification of the cn=builtin and cn=users container
however, as directory admins might not need so much control for things
like dns modification.

If you want to constrain these permissions, only apply the following to
cn=builtins instead - or even just the target groups like Domain Admins.

First we need the objectSID of our Directory Admins group so we can
build the ACE.

    # /usr/local/samba/bin/samba-tool group show 'directory admins' --attributes=cn,objectsid
    dn: CN=Directory Admins,CN=Users,DC=adt,DC=blackhats,DC=net,DC=au
    cn: Directory Admins
    objectSid: S-1-5-21-2488910578-3334016764-1009705076-1104

Now with this we can construct the ACE.

    (A;CI;RPWPLCLORC;;;S-1-5-21-2488910578-3334016764-1009705076-1104)

This permission grants:

-   RP: read property
-   WP: write property
-   LC: list child objects
-   LO: list objects
-   RC: read control

It could be possible to expand these rights: it depends if you want
directory admins to be able to do \"day to day\" ad control jobs, or if
you just use them for granting of privileges. That\'s up to you. An
expanded ACE might be:

    # Same as Enterprise Admins
    (A;CI;RPWPCRCCDCLCLORCWOWDSW;;;S-1-5-21-2488910578-3334016764-1009705076-1104)

Now lets actually apply this and do a test:

    # /usr/local/samba/bin/samba-tool dsacl set --sddl='(A;CI;RPWPLCLORC;;;S-1-5-21-2488910578-3334016764-1009705076-1104)' --objectdn='dc=adt,dc=blackhats,dc=net,dc=au'
    # /usr/local/samba/bin/samba-tool group addmembers 'directory admins' administrator -U 'da_william%...'
    Added members to group directory admins
    # /usr/local/samba/bin/samba-tool group listmembers 'directory admins' -U 'da_william%...'
    da_william
    Administrator

After we have completed our tasks, we remove da_william from the
directory admins group as we no longer required the privileges. You can
self-remove, or have the Administrator account do the removal.

    # /usr/local/samba/bin/samba-tool group removemembers 'directory admins' da_william -U 'da_william%...'
    Removed members from group directory admins

    # /usr/local/samba/bin/samba-tool group removemembers 'directory admins' da_william -U 'Administrator'
    Removed members from group directory admins

Finally check that da_william is no longer in the group.

    # /usr/local/samba/bin/samba-tool group listmembers 'directory admins' -U 'da_william%...'
    Administrator

## Conclusion

With these steps we have created a secure account that has limited admin
rights, able to temporarily promote users with privileges for
administrative work - and able to remove it once the work is complete.

