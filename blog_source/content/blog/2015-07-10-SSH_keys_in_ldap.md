+++
title = "SSH keys in ldap"
date = 2015-07-10
slug = "2015-07-10-SSH_keys_in_ldap"
# This is relative to the root!
aliases = [ "2015/07/10/SSH_keys_in_ldap.html" ]
+++
# SSH keys in ldap

At the dawn of time, we all used passwords to access systems. It was
good, but having to type your password tens, hundreds of times a day got
old. So along comes ssh keys. However, as we have grown the number of
systems we have it\'s hard to put your ssh key on all systems easily.
Then let alone the mess of needing to revoke an ssh key if it were
compromised.

Wouldn\'t it be easier if we could store one copy of your public key,
and make it available to all systems? When you revoke that key in one
location, it revokes on all systems?

Enter ssh public keys in ldap.

I think that FreeIPA is a great project, and they enable this by
default. However, we all don\'t have the luxury of just setting up IPA.
We have existing systems to maintain, in my case, 389ds.

So I had to work out how to setup this system myself.

First, you need to setup the LDAP server parts. I applied this ldif:

    dn: cn=schema
    changetype: modify
    add: attributetypes
    attributetypes: ( 1.3.6.1.4.1.24552.500.1.1.1.13 NAME 'sshPublicKey' DESC 'MANDATORY: OpenSSH Public key' EQUALITY octetStringMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.40 )
    -
    add: objectclasses
    objectClasses: ( 1.3.6.1.4.1.24552.500.1.1.2.0 NAME 'ldapPublicKey' SUP top AUXILIARY DESC 'MANDATORY: OpenSSH LPK objectclass' MUST ( uid ) MAY ( sshPublicKey ) )
    -

    dn: cn=sshpublickey,cn=default indexes,cn=config,cn=ldbm database,cn=plugins,cn=config
    changetype: add
    cn: sshpublickey
    nsIndexType: eq
    nsIndexType: pres
    nsSystemIndex: false
    objectClass: top
    objectClass: nsIndex

    dn: cn=sshpublickey_self_manage,ou=groups,dc=example,dc=com
    changetype: add
    objectClass: top
    objectClass: groupofuniquenames
    cn: sshpublickey_self_manage
    description: Members of this group gain the ability to edit their own sshPublicKey field

    dn: dc=example,dc=com
    changetype: modify
    add: aci
    aci: (targetattr = "sshPublicKey") (version 3.0; acl "Allow members of sshpublickey_self_manage to edit their keys"; allow(write) (groupdn = "ldap:///cn=sshpublickey_self_manage,ou=groups,dc=example,dc=com" and userdn="ldap:///self" ); )
    -

For the keen eyed, this is the schema from openssd-ldap but with the
objectClass altered to MAY instead of MUST take sshPublicKey. This
allows me to add the objectClass to our staff accounts, without needing
to set a key for them.

Members of the group in question can now self edit their ssh key. It
will look like :

    dn: uid=william,ou=People,dc=example,dc=com
    sshPublicKey: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDI/xgEMzqNwkXMIjjdDO2+xfru
     HK248uIKZ2CHFGIM+BlEhBjqvLpbrFZDYVsme8997p98ENPHGItFch87GCbRhWrpDHINQAnMQkLvD
     eykE1CpYpMWaeyygRZwCUaFfYJD3OgxVoqcUpAc8ZvtGQmHpo++RD5WPNedXOeq/vZzEPbp96ndOn
     b3WejCxl a1176360@strawberry

Now we configure SSSD.

    [domain/foo]
    ldap_account_expire_policy = rhds
    ldap_access_order = filter, expire
    ldap_user_ssh_public_key = sshPublicKey

    [sssd]
    ...
    services = nss, pam, ssh

The expire policy is extremely important. In 389ds we set nsAccountLock
to true to lock out an account. Normally this would cause the password
auth to fail, effectively denying access to servers.

However, with ssh keys, this process bypasses the password
authentication mechanism. So a valid ssh key could still access a server
even if the account lock was set.

So we setup this policy, to make sure that the account is locked out
from servers even if ssh key authentication is used.

This configuration can be tested by running:

    sss_ssh_authorizedkeys william

You should see a public key.

Finally, we configure sshd to check for these keys

    AuthorizedKeysCommand /usr/bin/sss_ssh_authorizedkeys
    AuthorizedKeysCommandUser root

Now you should be able to ssh into your systems.

It\'s a really simple setup to achieve this, and can have some really
great outcomes in the business.
