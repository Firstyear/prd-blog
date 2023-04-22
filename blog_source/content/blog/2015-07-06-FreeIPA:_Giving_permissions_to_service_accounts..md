+++
title = "FreeIPA: Giving permissions to service accounts."
date = 2015-07-06
slug = "2015-07-06-FreeIPA:_Giving_permissions_to_service_accounts."
# This is relative to the root!
aliases = [ "2015/07/06/FreeIPA:_Giving_permissions_to_service_accounts..html" ]
+++
# FreeIPA: Giving permissions to service accounts.

[I no longer recommend using FreeIPA - Read more
here!](/blog/html/2019/07/10/i_no_longer_recommend_freeipa.html)

I was setting up FreeRADIUS to work with MSCHAPv2 with FreeIPA (Oh god
you\'re a horrible human being I hear you say).

To do this, you need to do a few things, the main one being allowing a
service account a read permission to a normally hidden attribute.
However, service accounts don\'t normally have the ability to be added
to permission classes.

First, to enable this setup, you need to install freeipa-adtrust and do
the initial setup.

    yum install freeipa-server-trust-ad freeradius

    ipa-adtrust-install

Now change an accounts password, then as cn=Directory Manager look at
the account. You should see ipaNTHash on the account now.

    ldapsearch -H ldap://ipa.example.com -x -D 'cn=Directory Manager' -W -LLL -Z '(uid=username)' ipaNTHash

Now we setup the permission and a role to put the service accounts into.

    ipa permission-add 'ipaNTHash service read' --attrs=ipaNTHash --type=user  --right=read
    ipa privilege-add 'Radius services' --desc='Privileges needed to allow radiusd servers to operate'
    ipa privilege-add-permission 'Radius services' --permissions='ipaNTHash service read'
    ipa role-add 'Radius server' --desc="Radius server role"
    ipa role-add-privilege --privileges="Radius services" 'Radius server'

Next, we add the service account.

    ipa service-add 'radius/host.ipa.example.net.au'

Most services should be able to use the service account with either the
keytab for client authentication, or for at least the service to
authenticate to ldap. This is how you get the keytab.

    ipa-getkeytab -p 'radius/host.ipa.example.net.au' -s host.ipa.example.net.au -k /root/radiusd.keytab
    kinit -t /root/radiusd.keytab -k radius/host.ipa.example.net.au
    ldapwhoami -Y GSSAPI

If you plan to use this account with something like radius that only
accepts a password, here is how you can set one.

    dn: krbprincipalname=radius/host.ipa.example.net.au@IPA.EXAMPLE.NET.AU,cn=services,\
    cn=accounts,dc=ipa,dc=example,dc=net,dc=au
    changetype: modify
    add: objectClass
    objectClass: simpleSecurityObject
    -
    add: userPassword
    userPassword: <The service account password>

    ldapmodify -f <path/to/ldif> -D 'cn=Directory Manager' -W -H ldap://host.ipa.example.net.au -Z
    ldapwhoami -Z -D 'krbprincipalname=radius/host.ipa.example.net.au@IPA.EXAMPLE.NET.AU,\
    cn=services,cn=accounts,dc=ipa,dc=example,dc=net,dc=au' -W 

For either whoami test you should see a dn like:

    krbprincipalname=radius/host.ipa.example.net.au@IPA.EXAMPLE.NET.AU,cn=services,cn=accounts,dc=ipa,dc=example,dc=net,dc=au

Finally, we have to edit the cn=Radius server object and add the service
account. This is what the object should look like in the end:

    # Radius server, roles, accounts, ipa.example.net.au
    dn: cn=Radius server,cn=roles,cn=accounts,dc=ipa,dc=example,dc=net,dc=au
    memberOf: cn=Radius services,cn=privileges,cn=pbac,dc=ipa,dc=example,dc=net,
     dc=au
    memberOf: cn=ipaNTHash service read,cn=permissions,cn=pbac,dc=ipa,dc=example
     ,dc=net,dc=au
    description: Radius server role
    cn: Radius server
    objectClass: groupofnames
    objectClass: nestedgroup
    objectClass: top
    member: krbprincipalname=radius/host.ipa.example.net.au@IPA.EXAMPLE.NET.AU
     ,cn=services,cn=accounts,dc=ipa,dc=example,dc=net,dc=au

Now you should be able to use the service account to search and show
ipaNTHash on objects.

If you use this as your identify in raddb/mods-avaliable/ldap, and set
control:NT-Password := \'ipaNTHash\' in the update section, you should
be able to use this as an ldap backend for MSCHAPv2. I will write a more
complete blog on the radius half of this setup later.

NOTES: Thanks to afayzullin for noting the deprecation of \--permission
with ipa permission-add. This has been updated to \--right as per his
suggestion. Additional thanks for pointing out I should include the
command to do the directory manager ldapsearch for ipanthash.
