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

So anonymous binding is just fine, as the unix world has shown for a long time. That's why I have very few concerns about enabling it.

Installing your DC
------------------

As I run fedora, you will need to build and install samba for source so you can
access the heimdal kerberos functions. Fedora's samba 4 ships ADDC support now, but
lacks some features like RODC that you may want.

These documents will help guide you:

`requirements <https://wiki.samba.org/index.php/Package_Dependencies_Required_to_Build_Samba#Fedora_26>`_

`build steps <https://wiki.samba.org/index.php/Build_Samba_from_Source#Introduction>`_

`install a domain <https://wiki.samba.org/index.php/Setting_up_Samba_as_an_Active_Directory_Domain_Controller>`_

Allow anonymous binds and searches
----------------------------------

Now that you have a working domain controller, we should test you have working ldap:

::

    ...

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
