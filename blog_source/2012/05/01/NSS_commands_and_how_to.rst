NSS commands and how to
=======================
I have collated some knowledge on how to use NSS and it's tools for some general purpose usage, including mod_nss. 

Much of this is just assembling the contents of the `certutil documentation <http://www.mozilla.org/projects/security/pki/nss/tools/certutil.html>`_.

In this I have NOT documented the process of deleting certificates, changing trust settings of existing certificates or changing key3.db passwords.

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
    
    echo "soeihcoraiocrthhrcrcae aoriao htuathhhohodrrcrcgg89y99itantmnomtn" > pwdfile.txt
    echo "internal:soeihcoraiocrthhrcrcae aoriao htuathhhohodrrcrcgg89y99itantmnomtn" > pin.txt
    

Create a self signed certificate in your database. Note the -n, which creates a "nickname" (And should be unique) and is how applications reference your certificate and key. Also note the -s line, and the CN options. Finally, note the first line has the option -g, which defines the number of bits in the created certificate.

::
    
    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert" -g 2048\
    -s "CN=nss.dev.example.com,O=Testing,L=Adelaide,ST=South Australia,C=AU"
    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert2" \
    -s "CN=nss2.dev.example.com,O=Testing,L=Adelaide,ST=South Australia,C=AU" 
    

To add subject alternative names, use a comma seperated list with the option -8 IE

::
    
    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "Server-Cert" -g 2048\
    -s "CN=nss.dev.example.com,O=Testing,L=Adelaide,ST=South Australia,C=AU" \
    -8 "nss.dev.example.com,nss-alt.dev.example.com"
    

Create a self signed CA (In a different database from the one used by httpd.)

::
    
    certutil -S -n CAissuer -t "C,C,C" -x -f pwdfile.txt -d . \
    -s "CN=ca.nss.dev.example.com,O=Testing,L=Adelaide,ST=South Australia,C=AU"
    

Create a certificate in the same database, and sign it with the CAissuer certificate. 

::
    
    certutil -S -n Test-Cert -t ",," -c CAissuer -f pwdfile.txt -d . \
    -s "CN=test.nss.dev.example.com,O=Testing,L=Adelaide,ST=South Australia,C=AU"
    

Test the new cert for validity as an SSL server.

::
    
    certutil -V -d . -n Test-Cert -u V
    

View the new cert

::
    
    certutil -L -d . -n Test-Cert
    

View the cert in ASCII form (This can be redirected to a file for use with openssl)

::
    
    certutil -L -d . -n Test-Cert -a
    certutil -L -d . -n Test-Cert -a > cert.pem
    

In a second, seperate database to your CA.

Create a new certificate request. Again, remember -8 for subjectAltName

::
    
    certutil -d . -R -o nss.dev.example.com.csr -f pwdfile.txt \
    -s "CN=nss.dev.example.com,O=Testing,L=Adelaide,ST=South Australia,C=AU"
    

On the CA, review the CSR you have recieved.

::
    
    /usr/lib[64]/nss/unsupported-tools/derdump -i /etc/httpd/alias/nss.dev.example.com.csr
    openssl req -inform DER -text -in /etc/httpd/alias/nss.dev.example.com.csr
    

On the CA, sign the CSR.

::
    
    certutil -C -d . -f pwdfile.txt -i /etc/httpd/alias/nss.dev.example.com.csr \
    -o /etc/httpd/alias/nss.dev.example.com.crt -c CAissuer
    

Export the CA public certificate

::
    
    certutil -L -d . -n CAissuer -r > ca.crt
    

Import the CA public certificate into the requestors database.

::
    
    certutil -A -n "CAcert" -t "C,," -i /etc/pki/CA/nss/ca.crt -d .
    

Import the signed certificate into the requestors database.

::
    
    certutil -A -n "Server-cert" -t ",," -i nss.dev.example.com.crt -d .
    


Using openSSL create a server key, and make a CSR

::
    
    openssl genrsa -out server.key 2048
    openssl req -new -key server.key -out server.csr
    

On the CA, review the CSR.

::
    
    openssl req -inform PEM -text -in server.csr
    

On the CA, sign the request. Note the use of -a that allows an ASCII formatted PEM input, and will create and ASCII PEM certificate output.

::
    
    certutil -C -d . -f pwdfile.txt -i server.csr -o server.crt -a -c CAissuer
    

Import an openSSL generated key and certificate into an NSS database.

::
    
    openssl pkcs12 -export -in server.crt -inkey server.key -out server.p12 -name Test-Server-Cert
    pk12util -i server.p12 -d . -k pwdfile.txt
    

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

Finally, these commands all use the old DBM formatted NSS databases. To use the new "shareable" sqlite formatting, follow the steps found from `this blog post <https://blogs.oracle.com/meena/entry/what_s_new_in_nss1>`_. 

To configure mod_nss, you should have a configuration similar to below - Most of this is the standard nss.conf that comes with mod_nss, but note the changes to NSSNickname, and the modified NSSPassPhraseDialog and NSSRandomSeed values. There is documentation on the NSSCipherSuite that can be found by running "rpm -qd mod_nss". Finally, make sure that apache has read access to the database files and the pin.txt file. If you leave NSSPassPhraseDialog as "builtin", you cannot start httpd from systemctl. You must run apachectl so that you can enter the NSS database password on apache startup. 

NOTE:  mod_nss *might* support SNI. In my testing and examples, this works to create multiple sites via SNI, however, other developers claim this is not a supported feature. I have had issues with it in other instances also. For now, I would avoid it. 

::
    
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
    NSSCipherSuite +rsa_rc4_128_md5,+rsa_rc4_128_sha,+rsa_3des_sha,+fips_3des_sha,+rsa_aes_128_sha,+rsa_aes_256_sha,\
    -rsa_des_sha,-rsa_rc4_40_md5,-rsa_rc2_40_md5,-rsa_null_md5,-rsa_null_sha,-fips_des_sha,-fortezza,-fortezza_rc4_128_sha,\
    -fortezza_null,-rsa_des_56_sha,-rsa_rc4_56_sha
    NSSProtocol SSLv3,TLSv1
    NSSNickname Server-cert
    NSSCertificateDatabase /etc/httpd/alias
    <Files ~ "\.(cgi|shtml|phtml|php3?)$">
        NSSOptions +StdEnvVars
    </Files>
    <Directory "/var/www/cgi-bin">
        NSSOptions +StdEnvVars
    </Directory>
    </VirtualHost>                                  
    <VirtualHost *:8443>
    ServerName nss2.dev.example.com:8443
    ServerAlias nss2.dev.example.com
    ErrorLog /etc/httpd/logs/nss2_error_log
    TransferLog /etc/httpd/logs/nss2_access_log
    LogLevel warn
    NSSEngine on
    NSSCipherSuite +rsa_rc4_128_md5,+rsa_rc4_128_sha,+rsa_3des_sha,+fips_3des_sha,+rsa_aes_128_sha,+rsa_aes_256_sha,\
    -rsa_des_sha,-rsa_rc4_40_md5,-rsa_rc2_40_md5,-rsa_null_md5,-rsa_null_sha,-fips_des_sha,-fortezza,-fortezza_rc4_128_sha,\
    -fortezza_null,-rsa_des_56_sha,-rsa_rc4_56_sha
    NSSProtocol SSLv3,TLSv1
    NSSNickname Server-Cert2
    NSSCertificateDatabase /etc/httpd/alias
    <Files ~ "\.(cgi|shtml|phtml|php3?)$">
        NSSOptions +StdEnvVars
    </Files>
    <Directory "/var/www/cgi-bin">
        NSSOptions +StdEnvVars
    </Directory>
    </VirtualHost> 
    
