+++
title = "NSS-OpenSSL Command How to: The complete list."
date = 2014-07-10
slug = "2014-07-10-NSS-OpenSSL_Command_How_to:_The_complete_list."
# This is relative to the root!
aliases = [ "2014/07/10/NSS-OpenSSL_Command_How_to:_The_complete_list..html", "blog/html/2014/07/10/NSS-OpenSSL_Command_How_to:_The_complete_list..html" ]
+++
# NSS-OpenSSL Command How to: The complete list.

I am sick and tired of the lack of documentation for how to actually use
OpenSSL and NSS to achieve things. Be it missing small important options
like \"subjectAltNames\" in nss commands or openssls cryptic settings.
Here is my complete list of everything you would ever want to do with
OpenSSL and NSS.

References:

-   [certutil
    mozilla](http://www.mozilla.org/projects/security/pki/nss/tools/certutil.html).
-   [nss
    tools](https://developer.mozilla.org/en-US/docs/NSS_reference/NSS_tools_:_certutil).
-   [openssl](https://www.openssl.org/docs/apps/openssl.html).

## Nss specific

## DB creation and basic listing

Create a new certificate database if one doesn\'t exist (You should see
key3.db, secmod.db and cert8.db if one exists). :

    certutil -N -d . 

List all certificates in a database :

    certutil -L -d .

List all private keys in a database :

    certutil -K -d . [-f pwdfile.txt]

I have created a password file, which consists of random data on one
line in a plain text file. Something like below would suffice.
Alternately you can enter a password when prompted by the certutil
commands. If you wish to use this for apache start up, you need to use
pin.txt :

    echo "Password" > pwdfile.txt
    echo "internal:Password" > pin.txt

## Importing certificates to NSS

Import the signed certificate into the requesters database.

    certutil -A -n "Server-cert" -t ",," -i nss.dev.example.com.crt -d .

Import an openSSL generated key and certificate into an NSS database. :

    openssl pkcs12 -export -in server.crt -inkey server.key -out server.p12 -name Test-Server-Cert
    pk12util -i server.p12 -d . -k pwdfile.txt

## Importing a CA certificate

Import the CA public certificate into the requesters database. :

    certutil -A -n "CAcert" -t "C,," -i /etc/pki/CA/nss/ca.crt -d .

## Exporting certificates

Export a secret key and certificate from an NSS database for use with
openssl. :

    pk12util -o server-export.p12 -d . -k pwdfile.txt -n Test-Server-Cert
    openssl pkcs12 -in server-export.p12 -out file.pem -nodes

Note that file.pem contains both the CA cert, cert and private key. You
can view just the private key with: :

    openssl pkcs12 -in server-export.p12 -out file.pem -nocerts -nodes

Or just the cert and CAcert with :

    openssl pkcs12 -in server-export.p12 -out file.pem -nokeys -nodes

You can easily make ASCII formatted PEM from here.

## Both NSS and OpenSSL

## Self signed certificates

Create a self signed certificate.

For nss, note the -n, which creates a \"nickname\" (And should be
unique) and is how applications reference your certificate and key. Also
note the -s line, and the CN options. Finally, note the first line has
the option -g, which defines the number of bits in the created
certificate. :

    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert" -g 2048\
    -s "CN=nss.dev.example.com,O=Testing,L=example,ST=South Australia,C=AU"

    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days

    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert2" \
    -s "CN=nss2.dev.example.com,O=Testing,L=example,ST=South Australia,C=AU" 

## SubjectAltNames

To add subject alternative names, use a comma seperated list with the
option -8 IE: :

    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert" -g 2048\
    -s "CN=nss.dev.example.com,O=Testing,L=example,ST=South Australia,C=AU" \
    -8 "nss.dev.example.com,nss-alt.dev.example.com"

For OpenSSL this is harder:

First, you need to create an altnames.cnf :

    [req]
    req_extensions = v3_req
    nsComment = "Certificate"
    distinguished_name  = req_distinguished_name

    [ req_distinguished_name ]

    countryName                     = Country Name (2 letter code)
    countryName_default             = AU
    countryName_min                 = 2
    countryName_max                 = 2

    stateOrProvinceName             = State or Province Name (full name)
    stateOrProvinceName_default     = South Australia

    localityName                    = Locality Name (eg, city)
    localityName_default            = example/streetAddress=Level

    0.organizationName              = Organization Name (eg, company)
    0.organizationName_default      = example

    organizationalUnitName          = Organizational Unit Name (eg, section)
    organizationalUnitName_default = TS

    commonName                      = Common Name (eg, your name or your server\'s hostname)
    commonName_max                  = 64

    [ v3_req ]

    # Extensions to add to a certificate request

    basicConstraints = CA:FALSE
    keyUsage = nonRepudiation, digitalSignature, keyEncipherment
    subjectAltName = @alt_names

    [alt_names]
    DNS.1 = server1.yourdomain.tld
    DNS.2 = mail.yourdomain.tld
    DNS.3 = www.yourdomain.tld
    DNS.4 = www.sub.yourdomain.tld
    DNS.5 = mx.yourdomain.tld
    DNS.6 = support.yourdomain.tld

Now you run a similar command to before with: :

    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days -config altnames.cnf
    openssl req -key key.pem -out cert.csr -days -config altnames.cnf -new

## Check a certificate belongs to a specific key

    openssl rsa -noout -modulus -in client.key | openssl sha1
    openssl req -noout -modulus -in client.csr | openssl sha1
    openssl x509 -noout -modulus -in client.crt | openssl sha1

## View a certificate

View the cert :

    certutil -L -d . -n Test-Cert

    openssl x509 -noout -text -in client.crt

View the cert in ASCII PEM form (This can be redirected to a file for
use with openssl)

::

:   certutil -L -d . -n Test-Cert -a certutil -L -d . -n Test-Cert -a \>
    cert.pem

## Creating a CSR

In a second, seperate database to your CA.

Create a new certificate request. Again, remember -8 for subjectAltName
:

    certutil -d . -R -o nss.dev.example.com.csr -f pwdfile.txt \
    -s "CN=nss.dev.example.com,O=Testing,L=example,ST=South Australia,C=AU"

Using openSSL create a server key, and make a CSR :

    openssl genrsa -out client.key 2048
    openssl req -new -key client.key -out client.csr

## Self signed CA

Create a self signed CA (In a different database from the one used by
httpd.) :

    certutil -S -n CAissuer -t "C,C,C" -x -f pwdfile.txt -d . \
    -s "CN=ca.nss.dev.example.com,O=Testing,L=example,ST=South Australia,C=AU"

OpenSSL is the same as a self signed cert. :

    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days

## Signing with the CA

Create a certificate in the same database, and sign it with the CAissuer
certificate. :

    certutil -S -n Test-Cert -t ",," -c CAissuer -f pwdfile.txt -d . \
    -s "CN=test.nss.dev.example.com,O=Testing,L=example,ST=South Australia,C=AU"

If from a CSR, review the CSR you have recieved. :

    /usr/lib[64]/nss/unsupported-tools/derdump -i /etc/httpd/alias/nss.dev.example.com.csr
    openssl req -inform DER -text -in /etc/httpd/alias/nss.dev.example.com.csr  ## if from nss
    openssl req -inform PEM -text -in server.csr  ## if from openssl

On the CA, sign the CSR. :

    certutil -C -d . -f pwdfile.txt -i /etc/httpd/alias/nss.dev.example.com.csr \
    -o /etc/httpd/alias/nss.dev.example.com.crt -c CAissuer

For openssl CSR, note the use of -a that allows an ASCII formatted PEM
input, and will create and ASCII PEM certificate output. :

    certutil -C -d . -f pwdfile.txt -i server.csr -o server.crt -a -c CAissuer

    ### Note, you may need a caserial file ... 
    openssl x509 -req -days 1024 -in client.csr -CA root.crt -CAkey root.key -out client.crt

## Check validity of a certificate

Test the new cert for validity as an SSL server. This assumes the CA
cert is in the DB. (Else you need openssl or to import it) :

    certutil -V -d . -n Test-Cert -u V

    openssl verify -verbose -CAfile ca.crt client.crt

## Export the CA certificate

Export the CA public certificate :

    certutil -L -d . -n CAissuer -r > ca.crt

## NSS sqlite db

Finally, these commands all use the old DBM formatted NSS databases. To
use the new \"shareable\" sqlite formatting, follow the steps found from
[this blog
post](https://blogs.oracle.com/meena/entry/what_s_new_in_nss).

How to upgrade from cert8.db to cert9.db

You can either use environment variables or use sql: prefix in database
directory parameter of certutil:

::

:   \$export NSS_DEFAULT_DB_TYPE=sql \$certutil -K -d /tmp/nss -X

    > OR

    \$certutil -K -d sql:/tmp/nss -X

When you upgrade these are the files you get

    key3.db -> key4.db
    cert8.db -> cert9.db
    secmod.db -> pkcs11.txt

The contents of the pkcs11.txt files are basically identical to the
contents of the old secmod.db, just not in the old Berkeley DB format.
If you run the command \"\$modutil -dbdir DBDIR -rawlist\" on an older
secmod.db file, you should get output similar to what you see in
pkcs11.txt.

What needs to be done in programs / C code

Either add environment variable NSS_DEFAULT_DB_TYPE \"sql\"

NSS_Initialize call in <https://developer.mozilla.org/en/NSS_Initialize>
takes this \"configDir\" parameter as shown below.

    NSS_Initialize(configDir, "", "", "secmod.db", NSS_INIT_READONLY);

For cert9.db, change this first parameter to \"sql:\" + configDir (like
\"sql:/tmp/nss/\") i.e. prefix \"sql:\" in the directory name where
these NSS Databases exist. This code will work with cert8.db as well if
cert9.db is not present.

<https://wiki.mozilla.org/NSS_Shared_DB>

## Display a human readable certificate from an SSL socket

Note: port 636 is LDAPS, but all SSL sockets are supported. For TLS only
a limited set of protocols are supported. Add -starttls to the command.
See man 1 s_client.

    openssl s_client -connect ldap.example.com:636

    [ant@ant-its-example-edu-au ~]$ echo -n | openssl s_client -connect ldap.example.com:636 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' | openssl x509 -noout -text

    depth=3 C = SE, O = AddTrust AB, OU = AddTrust External TTP Network, CN = AddTrust External CA Root
    verify return:1
    depth=2 C = US, ST = UT, L = Salt Lake City, O = The USERTRUST Network, OU = http://www.usertrust.com, CN = UTN-USERFirst-Hardware
    verify return:1
    depth=1 C = AU, O = AusCERT, OU = Certificate Services, CN = AusCERT Server CA
    verify return:1
    depth=0 C = AU, postalCode = 5000, ST = South Australia, L = example, street = Level, street = Place, O =Example, OU = Technology Services, CN = ldap.example.com
    verify return:1
    DONE
    Certificate:
        Data:
            Version: 3 (0x2)
            Serial Number:
        Signature Algorithm: sha1WithRSAEncryption
            Issuer: C=AU, O=AusCERT, OU=Certificate Services, CN=AusCERT Server CA
            Validity
                Not Before: XX
                Not After : XX
            Subject: C=AU/postalCode=5000, ST=South Australia, L=example/street=Level /street=Place, O=Example, OU=Technology Services, CN=ldap.example.com
            Subject Public Key Info:
    <snip>
                X509v3 Subject Alternative Name: 
                    DNS:ldap.example.com
    <snip>

You can use this to display a CA chain if you can\'t get it from other
locations.

    openssl s_client -connect ldap.example.com:636 -showcerts

## mod_nss

To configure mod_nss, you should have a configuration similar to below -
Most of this is the standard nss.conf that comes with mod_nss, but note
the changes to NSSNickname, and the modified NSSPassPhraseDialog and
NSSRandomSeed values. There is documentation on the NSSCipherSuite that
can be found by running \"rpm -qd mod_nss\". Finally, make sure that
apache has read access to the database files and the pin.txt file. If
you leave NSSPassPhraseDialog as \"builtin\", you cannot start httpd
from systemctl. You must run apachectl so that you can enter the NSS
database password on apache startup.

NOTE: mod_nss *DOES NOT* support SNI.

    LoadModule nss_module modules/libmodnss.so
    Listen 8443
    NameVirtualHost *:8443
    AddType application/x-x509-ca-cert .crt
    AddType application/x-pkcs7-crl    .crl
    NSSPassPhraseDialog  file:/etc/httpd/alias/pin.txt
    NSSPassPhraseHelper /usr/sbin/nss_pcache
    NSSSessionCacheSize 10000
    NSSSessionCacheTimeout 100
    NSSSession3CacheTimeout 86400
    NSSEnforceValidCerts off
    NSSRandomSeed startup file:/dev/urandom 512
    NSSRenegotiation off
    NSSRequireSafeNegotiation off
    <VirtualHost *:8443>
    ServerName nss.dev.example.com:8443
    ServerAlias nss.dev.example.com
    ErrorLog /etc/httpd/logs/nss1_error_log
    TransferLog /etc/httpd/logs/nss1_access_log
    LogLevel warn
    NSSEngine on
    NSSProtocol TLSv1
    NSSNickname Server-cert
    NSSCertificateDatabase /etc/httpd/alias
    <Files ~ "\.(cgi|shtml|phtml|php3?)$">
        NSSOptions +StdEnvVars
    </Files>
    <Directory "/var/www/cgi-bin">
        NSSOptions +StdEnvVars
    </Directory>
    </VirtualHost>                                  
