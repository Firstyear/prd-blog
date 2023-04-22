+++
title = "Changing SSSD cert"
date = 2013-04-25
slug = "2013-04-25-Changing_SSSD_cert"
# This is relative to the root!
aliases = [ "2013/04/25/Changing_SSSD_cert.html" ]
+++
# Changing SSSD cert

After re-provisioning my Samba 4 domain, I found SSSD giving m a strange
error: :

    ldap_install_tls failed: [Connect error]
     [TLS error -8054:You are attempting to import a cert with the same issuer/serial as an existing cert, but that is not the same cert.]

It seems SSSD caches the ca cert of your ldap service (even if you
change the SSSD domain name). I couldn\'t find where to flush this, but
changing some of the tls options will fix it.

In SSSD.conf:

    ldap_id_use_start_tls = True
    ldap_tls_cacertdir = /usr/local/samba/private/tls
    ldap_tls_reqcert = demand

Now to make the cacertdir work you need to run

    cacertdir_rehash /usr/local/samba/private/tls

Your SSSD should now be working again.
