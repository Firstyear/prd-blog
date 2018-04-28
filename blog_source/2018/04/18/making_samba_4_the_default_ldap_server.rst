Making Samba 4 the default LDAP server
======================================

Earlier this year Andrew Bartlett set me the challenge: how could we make Samba 4 the default LDAP server in use for Linux and UNIX systems? I've finally decided to tackle this, and write up some
simple changes we can make, and decide on some long term goals to make this a reality.

What makes a unix directory anyway?
-----------------------------------

Great question - this is such a broad topic, even I don't know if I can single out what it means.
For the purposes of this exercise I'll treat it as "what would we need from my previous workplace".
My previous workplace had a dedicated set of 389 Directory Server machines that served lookups mainly
for email routing, application authentication and more. The didn't really process a great deal of login traffic as
the majority of the workstations were Windows - thus connected to AD.

What it did show was that Linux clients and applications:

* Want to use anonymous binds and searchs - Applications and clients are NOT domain members - they just want to do searches
* The content of anonymous lookups should be "public safe" information. (IE nothing private)
* LDAPS is a must for binds
* MemberOf and group filtering is very important for access control
* sshPublicKey and userCertificate;binary is important for 2fa/secure logins

This seems like a pretty simple list - but it's not the model Samba 4 or AD ship with.

You'll also want to harden a few default settings. These include:

* Disable Guest
* Disable 10 machine join policy

AD works under the assumption that all clients are authenticated via kerberos, and that kerberos is the primary
authentication and trust provider. As a result, AD often ships with:

* Disabled anonymous binds - All clients are domain members or service accounts
* No anonymous content available to search
* No LDAPS (GSSAPI is used instead)
* no sshPublicKey or userCertificates (pkinit instead via krb)
* Access control is much more complex topic than just "matching an ldap filter".

As a result, it takes a bit of effort to change Samba 4 to work in a way that suits both, securely.

Isn't anonymous binding insecure?
---------------------------------

Let's get this one out the way - no it's not. In every pen test I have seen if you can get access to a domain joined machine, you probably
have a good chance of taking over the domain in various ways. Domain joined systems and krb allows lateral movement and other issues
that are beyond the scope of this document.

The lack of anonymous lookup is more about preventing information disclosure - security via obscurity. But it doesn't take long to realise
that this is trivially defeated (get one user account, guest account, domain member and you can search ...).

As a result, in some cases it may be better to allow anonymous lookups because then you don't have spurious service accounts, you have a clear
understanding of what is and is not accessible as readable data, and you *don't* need every machine on the network to be domain joined - you prevent
a possible foothold of lateral movement.

So anonymous binding is just fine, as the unix world has shown for a long time. That's why I have very few concerns about enabling it. Your
safety is in the access controls for searches, not in blocking anonymous reads outright.

Installing your DC
------------------

As I run fedora, you will need to build and install samba for source so you can
access the heimdal kerberos functions. Fedora's samba 4 ships ADDC support now, but
lacks some features like RODC that you may want. In the future I expect this will change though.

These documents will help guide you:

`requirements <https://wiki.samba.org/index.php/Package_Dependencies_Required_to_Build_Samba#Fedora_26>`_

`build steps <https://wiki.samba.org/index.php/Build_Samba_from_Source#Introduction>`_

`install a domain <https://wiki.samba.org/index.php/Setting_up_Samba_as_an_Active_Directory_Domain_Controller>`_

I strongly advise you use options similar to:

::

    /usr/local/samba/bin/samba-tool domain provision --server-role=dc --use-rfc2307 --dns-backend=SAMBA_INTERNAL --realm=SAMDOM.EXAMPLE.COM --domain=SAMDOM --adminpass=Passw0rd

Allow anonymous binds and searches
----------------------------------

Now that you have a working domain controller, we should test you have working ldap:

::

    /usr/local/samba/bin/samba-tool forest directory_service dsheuristics 0000002 -H ldaps://localhost --simple-bind-dn='administrator@samdom.example.com'

::

     ldapsearch -b DC=samdom,DC=example,DC=com -H ldaps://localhost -x

You can see the domain object but nothing else. Many other blogs and sites recommend a blanket "anonymous read all" access control, but I think that's
too broad. A better approach is to add the anonymous read to only the few containers that require it.

::

    /usr/local/samba/bin/samba-tool dsacl set --objectdn=DC=samdom,DC=example,DC=com --sddl='(A;;RPLCLORC;;;AN)' --simple-bind-dn="administrator@samdom.example.com" --password=Passw0rd
    /usr/local/samba/bin/samba-tool dsacl set --objectdn=CN=Users,DC=samdom,DC=example,DC=com --sddl='(A;CI;RPLCLORC;;;AN)' --simple-bind-dn="administrator@samdom.example.com" --password=Passw0rd
    /usr/local/samba/bin/samba-tool dsacl set --objectdn=CN=Builtin,DC=samdom,DC=example,DC=com --sddl='(A;CI;RPLCLORC;;;AN)' --simple-bind-dn="administrator@samdom.example.com" --password=Passw0rd


In AD groups and users are found in cn=users, and some groups are in cn=builtin. So we allow read to the root domain object, then we set
a read on cn=users and cn=builtin that inherits to it's child objects. The attribute policies are derived elsewhere, so we can assume
that things like kerberos data and password material are safe with these simple changes.


Configuring LDAPS
-----------------

This is a reasonable simple exercise. Given a ca cert, key and cert we can place these in the correct locations samba expects.
By default this is the private directory. In a custom install, that's /usr/local/samba/private/tls/, but for distros I think
it's /var/lib/samba/private. Simply replace ca.pem, cert.pem and key.pem with your files and restart.

Adding schema
-------------

To allow adding schema to samba 4 you need to reconfigure the dsdb config on the
schema master. To show the current schema master you can use:

::

     /usr/local/samba/bin/samba-tool fsmo show -H ldaps://localhost --simple-bind-dn='administrator@adt.blackhats.net.au' --password=Password1

Look for the value:

::

    SchemaMasterRole owner: CN=NTDS Settings,CN=LDAPKDC,CN=Servers,CN=Default-First-Site-Name,CN=Sites,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au

And note the CN=ldapkdc = that's the hostname of the current schema master.

On the schema master we need to adjust the smb.conf. The change you need to make is:

::

    [global]
        dsdb:schema update allowed = yes

Now restart the instance and we can update the schema. The following LDIF should work if you replace ${DOMAINDN} with your namingContext. You can
apply it with ldapmodify

::

    dn: CN=sshPublicKey,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    changetype: add
    objectClass: top
    objectClass: attributeSchema
    attributeID: 1.3.6.1.4.1.24552.500.1.1.1.13
    cn: sshPublicKey
    name: sshPublicKey
    lDAPDisplayName: sshPublicKey
    description: MANDATORY: OpenSSH Public key
    attributeSyntax: 2.5.5.10
    oMSyntax: 4
    isSingleValued: FALSE

    dn: CN=ldapPublicKey,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    changetype: add
    objectClass: top
    objectClass: classSchema
    governsID: 1.3.6.1.4.1.24552.500.1.1.2.0
    cn: ldapPublicKey
    name: ldapPublicKey
    description: MANDATORY: OpenSSH LPK objectclass
    lDAPDisplayName: ldapPublicKey
    subClassOf: top
    objectClassCategory: 3
    defaultObjectCategory: CN=ldapPublicKey,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    mayContain: sshPublicKey

    dn: CN=User,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    changetype: modify
    replace: auxiliaryClass
    auxiliaryClass: ldapPublicKey
    auxiliaryClass: posixAccount
    auxiliaryClass: shadowAccount
    -

::

    sudo ldapmodify -f sshpubkey.ldif -D 'administrator@adt.blackhats.net.au' -w Password1 -H ldaps://localhost 
    adding new entry "CN=sshPublicKey,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au"

    adding new entry "CN=ldapPublicKey,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au"

    modifying entry "CN=User,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au"

To my surprise, userCertificate already exists! The reason I missed it is a subtle ad schema behaviour I missed. The *ldap attribute* name is stored in the lDAPDisplayName and may not be the same as the CN of the schema element. As a result, you can find this with:

::

    ldapsearch -H ldaps://localhost -b CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au -x -D 'administrator@adt.blackhats.net.au' -W '(attributeId=2.5.4.36)'


This doesn't solve my issues: Because I am a long time user of 389-ds, that means I need some ns compat attributes. Here I add the nsUniqueId value so that I can keep some compatability.

::

    dn: CN=nsUniqueId,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    changetype: add
    objectClass: top
    objectClass: attributeSchema
    attributeID: 2.16.840.1.113730.3.1.542
    cn: nsUniqueId
    name: nsUniqueId
    lDAPDisplayName: nsUniqueId
    description: MANDATORY: nsUniqueId compatability
    attributeSyntax: 2.5.5.10
    oMSyntax: 4
    isSingleValued: TRUE

    dn: CN=nsOrgPerson,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    changetype: add
    objectClass: top
    objectClass: classSchema
    governsID: 2.16.840.1.113730.3.2.334
    cn: nsOrgPerson
    name: nsOrgPerson
    description: MANDATORY: Netscape DS compat person
    lDAPDisplayName: nsOrgPerson
    subClassOf: top
    objectClassCategory: 3
    defaultObjectCategory: CN=nsOrgPerson,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    mayContain: nsUniqueId

    dn: CN=User,CN=Schema,CN=Configuration,DC=adt,DC=blackhats,DC=net,DC=au
    changetype: modify
    replace: auxiliaryClass
    auxiliaryClass: ldapPublicKey
    auxiliaryClass: posixAccount
    auxiliaryClass: shadowAccount
    auxiliaryClass: nsOrgPerson
    -


Now with this you can extend your users with the required data for SSH, certificates and maybe 389-ds compatability.

::

    /usr/local/samba/bin/samba-tool user edit william  -H ldaps://localhost --simple-bind-dn='administrator@adt.blackhats.net.au'

AD Hardening
------------

We want to harden a few default settings that could be considered insecure. First, let's stop "any user from being able to domain join machines".

::

    /usr/local/samba/bin/samba-tool domain settings account_machine_join_quota 0 -H ldaps://localhost --simple-bind-dn='administrator@adt.blackhats.net.au'

Now let's disable the Guest account

::

    /usr/local/samba/bin/samba-tool user disable Guest -H ldaps://localhost --simple-bind-dn='administrator@adt.blackhats.net.au'

I plan to write a more complete samba-tool extension for auditing these and more options, so stay tuned!

SSSD configuration
------------------

Now that our directory service is configured, we need to configure our clients to utilise it correctly.

Here is my SSSD configuration, that supports sshPublicKey distribution, userCertificate authentication on workstations
and SID -> uid mapping. In the future I want to explore sudo rules in LDAP with AD, and maybe even HBAC rules rather
than GPO.

Please refer to my other blog posts on configuration of the userCertificates and sshKey distribution.

::

    [domain/blackhats.net.au]
    ignore_group_members = False

    debug_level=3
    # There is a bug in SSSD where this actually means "ipv6 only".
    # lookup_family_order=ipv6_first
    cache_credentials = True
    id_provider = ldap
    auth_provider = ldap
    access_provider = ldap
    chpass_provider = ldap
    ldap_search_base = dc=blackhats,dc=net,dc=au

    # This prevents an infinite referral loop.
    ldap_referrals = False
    ldap_id_mapping = True
    ldap_schema = ad
    # Rather that being in domain users group, create a user private group
    # automatically on login.
    # This is very important as a security setting on unix!!!
    # See this bug if it doesn't work correctly.
    # https://pagure.io/SSSD/sssd/issue/3723
    auto_private_groups = true

    ldap_uri = ldaps://ad.blackhats.net.au
    ldap_tls_reqcert = demand
    ldap_tls_cacert = /etc/pki/tls/certs/bh_ldap.crt

    # Workstation access
    ldap_access_filter = (memberOf=CN=Workstation Operators,CN=Users,DC=blackhats,DC=net,DC=au)

    ldap_user_member_of = memberof
    ldap_user_gecos = cn
    ldap_user_uuid = objectGUID
    ldap_group_uuid = objectGUID
    # This is really important as it allows SSSD to respect nsAccountLock
    ldap_account_expire_policy = ad
    ldap_access_order = filter, expire
    # Setup for ssh keys
    ldap_user_ssh_public_key = sshPublicKey
    # This does not require ;binary tag with AD.
    ldap_user_certificate = userCertificate
    # This is required for the homeDirectory to be looked up in the sssd schema
    ldap_user_home_directory = homeDirectory


    [sssd]
    services = nss, pam, ssh, sudo
    config_file_version = 2
    certificate_verification = no_verification

    domains = blackhats.net.au
    [nss]
    homedir_substring = /home

    [pam]
    pam_cert_auth = True

    [sudo]

    [autofs]

    [ssh]

    [pac]

    [ifp]


Conclusion
----------

With these simple changes we can easily make samba 4 able to perform the roles of other unix focused LDAP servers. This allows stateless clients,
secure ssh key authentication, certificate authentication and more.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
