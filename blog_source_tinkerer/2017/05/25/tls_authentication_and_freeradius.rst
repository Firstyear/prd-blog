TLS Authentication and FreeRADIUS
=================================

In a push to try and limit the amount of passwords sent on my network, I'm changing my wireless to use TLS certificates for authentication.

.. more::

First, you'll need an internal CA and Server Cert's issued for FreeRADIUS. I would advise you follow my NSS how to guide for more on this.

You'll need to create a user-certificate on your machine, and have it signed by your CA too:

::

    certutil -d . -R -a -o user.csr -f pwdfile.txt -g 4096 -Z SHA256 -v 24 --keyUsage digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment --nsCertType sslClient --extKeyUsage clientAuth -s "CN=..."
    # Send user.csr to your CA to sign
    openssl req -in /home/william/user.csr -noout -text
    certutil -C -d . -a -i /home/william/user.csr -o /home/william/user.crt -c BH_LDAP_CA -v 24
    openssl x509 -in /home/william/user.crt -noout -text

The freeRADIUS configuration is surprisingly easy. You need to link check-eap-tls to /etc/raddb/sites-enabled/, then in mods-available/eap edit:

::

    tls {
        # Point to the common TLS configuration
        tls = tls-common
        virtual_server = check-eap-tls
    }


Make sure youl tls-common section in eap is correct!

Next in check-eap-tls you can uncomment the various sections as needed.

Importantly, run with radiusd -X to test. I had an issue with TLS-Client-Cert-Common-Name not being expanded because it wasn't sent to the virtual server: at some point it just "started working" though, so I can offer no good advice on this matter.



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
