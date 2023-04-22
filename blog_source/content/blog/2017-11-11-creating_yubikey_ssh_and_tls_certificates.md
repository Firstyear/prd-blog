+++
title = "Creating yubikey SSH and TLS certificates"
date = 2017-11-11
slug = "2017-11-11-creating_yubikey_ssh_and_tls_certificates"
# This is relative to the root!
aliases = [ "2017/11/11/creating_yubikey_ssh_and_tls_certificates.html", "blog/html/2017/11/11/creating_yubikey_ssh_and_tls_certificates.html" ]
+++
# Creating yubikey SSH and TLS certificates

Recently yubikeys were shown to have a hardware flaw in the way the
generated private keys. This affects the use of them to provide PIV
identies or SSH keys.

However, you can generate the keys externally, and load them to the key
to prevent this issue.

## SSH

First, we\'ll create a new NSS DB on an airgapped secure machine (with
disk encryption or in memory storage!)

    certutil -N -d . -f pwdfile.txt

Now into this, we\'ll create a self-signed cert valid for 10 years.

    certutil -S -f pwdfile.txt -d . -t "C,," -x -n "SSH" -g 2048 -s "cn=william,O=ssh,L=Brisbane,ST=Queensland,C=AU" -v 120

We export this now to PKCS12 for our key to import.

    pk12util -o ssh.p12 -d . -k pwdfile.txt -n SSH

Next we import the key and cert to the hardware in slot 9c

    yubico-piv-tool -s9c -i ssh.p12 -K PKCS12 -aimport-key -aimport-certificate -k

Finally, we can display the ssh-key from the token.

    ssh-keygen -D /usr/lib64/opensc-pkcs11.so -e

Note, we can make this always used by ssh client by adding the following
into .ssh/config:

    PKCS11Provider /usr/lib64/opensc-pkcs11.so

## TLS Identities

The process is almost identical for user certificates.

First, create the request:

    certutil -d . -R -a -o user.csr -f pwdfile.txt -g 4096 -Z SHA256 -v 24 \
    --keyUsage digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment --nsCertType sslClient --extKeyUsage clientAuth \
    -s "CN=username,O=Testing,L=example,ST=Queensland,C=AU"

Once the request is signed, we should have a user.crt back. Import that
to our database:

    certutil -A -d . -f pwdfile.txt -i user.crt -a -n TLS -t ",,"

Import our CA certificate also. Next export this to p12:

    pk12util -o user.p12 -d . -k pwdfile.txt -n TLS

Now import this to the yubikey - remember to use slot 9a this time!

    yubico-piv-tool -s9a -i user.p12 -K PKCS12 -aimport-key -aimport-certificate -k --touch-policy=always

Done!

