NSS and OpenSSL Command Reference
=================================

I am tired of the lack of documentation for how to actually use OpenSSL and NSS to achieve things. Be it missing small important options like "subjectAltNames" in nss commands or openssls cryptic settings. Here is my complete list of everything you would ever want to do with OpenSSL and NSS.

References:

* `certutil mozilla <http://www.mozilla.org/projects/security/pki/nss/tools/certutil.html>`_.
* `nss tools <https://developer.mozilla.org/en-US/docs/NSS_reference/NSS_tools_:_certutil>`_.
* `openssl <https://www.openssl.org/docs/apps/openssl.html>`_.

Nss specific
------------

DB creation and basic listing
-----------------------------

Create a new certificate database if one doesn't exist (You should see key3.db, secmod.db and cert8.db if one exists). 
::
    
    certutil -N -d . 

List all certificates in a database 
::
    
    certutil -L -d .

List all private keys in a database 
::
    
    certutil -K -d . [-f pwdfile.txt]

I have created a password file, which consists of random data on one line in a plain text file. Something like below would suffice. Alternately you can enter a password when prompted by the certutil commands. If you wish to use this for apache start up, you need to use pin.txt 
::
    
    echo "Password" > pwdfile.txt
    echo "internal:Password" > pin.txt

Importing certificates to NSS
-----------------------------

Import the signed certificate into the requesters database.

::

    certutil -A -n "Server-cert" -t ",," -i nss.dev.example.com.crt -d .

Import an openSSL generated key and certificate into an NSS database.

::

    openssl pkcs12 -export -in server.crt -inkey server.key -out server.p12 -name Test-Server-Cert
    pk12util -i server.p12 -d . -k pwdfile.txt

Importing a CA certificate
--------------------------

Import the CA public certificate into the requesters database.

::

    certutil -A -n "CAcert" -t "C,," -i /etc/pki/CA/nss/ca.crt -d .

Exporting certificates
----------------------

Export a secret key and certificate from an NSS database for use with openssl.

::

    pk12util -o server-export.p12 -d . -k pwdfile.txt -n Test-Server-Cert
    openssl pkcs12 -in server-export.p12 -out file.pem -nodes

Note that file.pem contains both the CA cert, cert and private key. You can view just the private key with:

::

    openssl pkcs12 -in server-export.p12 -out file.pem -nocerts -nodes

Or just the cert and CAcert with

::

    openssl pkcs12 -in server-export.p12 -out file.pem -nokeys -nodes

You can easily make ASCII formatted PEM from here.

Both NSS and OpenSSL
--------------------

Self signed certificates
------------------------

Create a self signed certificate.

For nss, note the -n, which creates a "nickname" (And should be unique) and is how applications reference your certificate and key. Also note the -s line, and the CN options. Finally, note the first line has the option -g, which defines the number of bits in the created certificate. Note also the -Z for the hash algorithm.

::

    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert" -g 4096 -Z SHA256 \
    -s "CN=nss.dev.example.com,O=Testing,L=example,ST=Queensland,C=AU"

    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days

::

    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert2" \
    -s "CN=nss2.dev.example.com,O=Testing,L=example,ST=Queensland,C=AU" 

SubjectAltNames
---------------

To add subject alternative names, use a comma seperated list with the option -8 IE:

::

    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert" -g 4096 -Z SHA256 \
    -s "CN=nss.dev.example.com,O=Testing,L=example,ST=Queensland,C=AU" \
    -8 "nss.dev.example.com,nss-alt.dev.example.com"

For OpenSSL this is harder:
    
First, you need to create an altnames.cnf 

::
    
    [req]
    req_extensions = v3_req
    nsComment = "Certificate"
    distinguished_name	= req_distinguished_name
    
    [ req_distinguished_name ]
    
    countryName                     = Country Name (2 letter code)
    countryName_default             = AU
    countryName_min                 = 2
    countryName_max                 = 2
    
    stateOrProvinceName             = State or Province Name (full name)
    stateOrProvinceName_default     = Queensland
    
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
    
Now you run a similar command to before with: 
::
    
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days -config altnames.cnf
    openssl req -key key.pem -out cert.csr -days -config altnames.cnf -new
    
Check a certificate belongs to a specific key
---------------------------------------------

::
    
    openssl rsa -noout -modulus -in client.key | openssl sha1
    openssl req -noout -modulus -in client.csr | openssl sha1
    openssl x509 -noout -modulus -in client.crt | openssl sha1
    
View a certificate
------------------
    
View the cert 
::
    
    certutil -L -d . -n Test-Cert
    
::
    
    openssl x509 -noout -text -in client.crt

View the cert in ASCII PEM form (This can be redirected to a file for use with openssl) 
   
:: 

    certutil -L -d . -n Test-Cert -a
    certutil -L -d . -n Test-Cert -a > cert.pem

Creating a CSR
--------------
    
In a second, seperate database to your CA. 

Create a new certificate request. Again, remember -8 for subjectAltName. This request is for a TLS server.

::

    certutil -d . -R -a -o nss.dev.example.com.csr -f pwdfile.txt -g 4096 -Z SHA256 -v 24 \
    -s "CN=nss.dev.example.com,O=Testing,L=example,ST=Queensland,C=AU"

If you want to request for a TLS client you need to use:

::

    certutil -d . -R -a -o user.csr -f pwdfile.txt -g 4096 -Z SHA256 -v 24 \
    --keyUsage digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment --nsCertType sslClient --extKeyUsage clientAuth \
    -s "CN=username,O=Testing,L=example,ST=Queensland,C=AU"


Using openSSL create a server key, and make a CSR 
::

    openssl genrsa -out client.key 2048
    openssl req -new -key client.key -out client.csr

Self signed CA
--------------
    
Create a self signed CA (In a different database from the one used by httpd.) 
::
    
    certutil -S -n CAissuer -t "C,C,C" -x -f pwdfile.txt -d . -v 24 -g 4096 -Z SHA256 \
    --keyUsage certSigning -2 --nsCertType sslCA \
    -s "CN=ca.nss.dev.example.com,O=Testing,L=example,ST=Queensland,C=AU"

Nss will ask you about the constraints on this certificate. Here is a sample output. Note the path length of 0 still allows this CA to issue certificates, but it cannot issue an intermediate CA.

::

    Generating key.  This may take a few moments...

            0 - Digital Signature
            1 - Non-repudiation
            2 - Key encipherment
            3 - Data encipherment
            4 - Key agreement
            5 - Cert signing key
            6 - CRL signing key
            Other to finish
     > 5
            0 - Digital Signature
            1 - Non-repudiation
            2 - Key encipherment
            3 - Data encipherment
            4 - Key agreement
            5 - Cert signing key
            6 - CRL signing key
            Other to finish
     > 9
    Is this a critical extension [y/N]?
    n
    Is this a CA certificate [y/N]?
    y
    Enter the path length constraint, enter to skip [<0 for unlimited path]: > 0
    Is this a critical extension [y/N]?
    y
            0 - SSL Client
            1 - SSL Server
            2 - S/MIME
            3 - Object Signing
            4 - Reserved for future use
            5 - SSL CA
            6 - S/MIME CA
            7 - Object Signing CA
            Other to finish
     > 5
            0 - SSL Client
            1 - SSL Server
            2 - S/MIME
            3 - Object Signing
            4 - Reserved for future use
            5 - SSL CA
            6 - S/MIME CA
            7 - Object Signing CA
            Other to finish
     > 9
    Is this a critical extension [y/N]?
    n


OpenSSL is the same as a self signed cert. It's probably wise to add path length and other policies here.
::
    
    openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days
    

Renewing the self signed CA
---------------------------

This happens if your CA is about to or has expired. You need to reissue all your certs after this is done!

::

    certutil -d . -R -k "NSS Certificate DB:ca" -s "CN=ca.net.blackhats.net.au,O=Blackhats,L=Brisbane,ST=Queensland,C=AU" -a -o renew.req -1 -2 -5

    certutil -C -d . -c "ca" -a -i renew.req -t "C,C,C" -o cacert.crt -v 12

    certutil -A -d . -n "ca" -a -i cacert.crt -t "C,C,C"


Signing with the CA
-------------------

Create a certificate in the same database, and sign it with the CAissuer certificate. 

::
    
    certutil -S -n Test-Cert -t ",," -c CAissuer -f pwdfile.txt -d . \
    -s "CN=test.nss.dev.example.com,O=Testing,L=example,ST=Queensland,C=AU"

If from a CSR, review the CSR you have recieved. 

::
    
    /usr/lib[64]/nss/unsupported-tools/derdump -i /etc/httpd/alias/nss.dev.example.com.csr
    openssl req -inform DER -text -in /etc/httpd/alias/nss.dev.example.com.csr  ## if from nss
    openssl req -inform PEM -text -in server.csr  ## if from openssl

On the CA, sign the CSR. 

::
    
    certutil -C -d . -f pwdfile.txt -a -i /etc/httpd/alias/nss.dev.example.com.csr \
    -o /etc/httpd/alias/nss.dev.example.com.crt -c CAissuer

For openssl CSR, note the use of -a that allows an ASCII formatted PEM input, and will create and ASCII PEM certificate output. 

::
    
    certutil -C -d . -f pwdfile.txt -i server.csr -o server.crt -a -c CAissuer
    
::
    
    ### Note, you may need a caserial file ... 
    openssl x509 -req -days 1024 -in client.csr -CA root.crt -CAkey root.key -out client.crt

Check validity of a certificate
-------------------------------
    
Test the new cert for validity as an SSL server. This assumes the CA cert is in the DB. (Else you need openssl or to import it). The second example is validating a user certificate.

::
    
    certutil -V -d . -n Test-Cert -u V

    certutil -V -d . -n usercert -u C

::
    
    openssl verify -verbose -CAfile ca.crt client.crt

Export the CA certificate
-------------------------
    
Export the CA public certificate 
::
    
    certutil -L -d . -n CAissuer -r > ca.crt
    
NSS sqlite db
-------------
    
Finally, these commands all use the old DBM formatted NSS databases. To use the new "shareable" sqlite formatting, follow the steps found from `this blog post <https://blogs.oracle.com/meena/entry/what_s_new_in_nss>`_.

How to upgrade from cert8.db to cert9.db 

You can either use environment variables or use sql: prefix in database directory parameter of certutil:

::

    $export NSS_DEFAULT_DB_TYPE=sql
    $certutil -K -d /tmp/nss -X

            OR

    $certutil -K -d sql:/tmp/nss -X

When you upgrade these are the files you get

::
    
            key3.db -> key4.db
           cert8.db -> cert9.db
           secmod.db -> pkcs11.txt
    
The contents of the pkcs11.txt files are basically identical to the contents of the old secmod.db, just not in the old Berkeley DB format. If you run the command "$modutil -dbdir DBDIR -rawlist" on an older secmod.db file, you should get output similar to what you see in pkcs11.txt.
    
What needs to be done in programs / C code 

Either add environment variable NSS_DEFAULT_DB_TYPE "sql"

NSS_Initialize call in https://developer.mozilla.org/en/NSS_Initialize takes this "configDir" parameter as shown below.

::
    
    NSS_Initialize(configDir, "", "", "secmod.db", NSS_INIT_READONLY);
    
For cert9.db, change this first parameter to "sql:" + configDir (like "sql:/tmp/nss/") i.e. prefix "sql:" in the directory name where these NSS Databases exist.
This code will work with cert8.db as well if cert9.db is not present.

https://wiki.mozilla.org/NSS_Shared_DB 
    
Display a human readable certificate from an SSL socket
-------------------------------------------------------
    
Note: port 636 is LDAPS, but all SSL sockets are supported. For TLS only a limited set of protocols are supported. Add -starttls to the command. See man 1 s_client.
    
::
    
    openssl s_client -connect ldap.example.com:636
    

::
    
    [ant@ant-its-example-edu-au ~]$ echo -n | openssl s_client -connect ldap.example.com:636 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' | openssl x509 -noout -text
    
    depth=3 C = SE, O = AddTrust AB, OU = AddTrust External TTP Network, CN = AddTrust External CA Root
    verify return:1
    depth=2 C = US, ST = UT, L = Salt Lake City, O = The USERTRUST Network, OU = http://www.usertrust.com, CN = UTN-USERFirst-Hardware
    verify return:1
    depth=1 C = AU, O = AusCERT, OU = Certificate Services, CN = AusCERT Server CA
    verify return:1
    depth=0 C = AU, postalCode = 5000, ST = Queensland, L = example, street = Level, street = Place, O =Example, OU = Technology Services, CN = ldap.example.com
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
            Subject: C=AU/postalCode=4000, ST=Queensland, L=example/street=Level /street=Place, O=Example, OU=Technology Services, CN=ldap.example.com
            Subject Public Key Info:
    <snip>
                X509v3 Subject Alternative Name: 
                    DNS:ldap.example.com
    <snip>
    

You can use this to display a CA chain if you can't get it from other locations.

::
    
    openssl s_client -connect ldap.example.com:636 -showcerts
    

