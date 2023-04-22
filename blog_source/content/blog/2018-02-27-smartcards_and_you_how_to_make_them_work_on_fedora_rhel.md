+++
title = "Smartcards and You - How To Make Them Work on Fedora/RHEL"
date = 2018-02-27
slug = "2018-02-27-smartcards_and_you_how_to_make_them_work_on_fedora_rhel"
# This is relative to the root!
aliases = [ "2018/02/27/smartcards_and_you_how_to_make_them_work_on_fedora_rhel.html", "blog/html/2018/02/27/smartcards_and_you_how_to_make_them_work_on_fedora_rhel.html" ]
+++
# Smartcards and You - How To Make Them Work on Fedora/RHEL

Smartcards are a great way to authenticate users. They have a device
(something you have) and a pin (something you know). They prevent
password transmission, use strong crypto and they even come in a variety
of formats. From your \"card\" shapes to yubikeys.

So why aren\'t they used more? It\'s the classic issue of usability -
the setup for them is undocumented, complex, and hard to discover. Today
I hope to change this.

## The Goal

To authenticate a user with a smartcard to a physical linux system,
backed onto LDAP. The public cert in LDAP is validated, as is the chain
to the CA.

## You Will Need

-   LDAP ([here is one I prepared earlier](http://www.port389.org/))
-   One Linux - Fedora 27 or RHEL 7 work best
-   A smartcard (yubikey 4/nano works)

I\'ll be focusing on the yubikey because that\'s what I own.

## Preparing the Smartcard

First we need to make the smartcard hold our certificate. Because of a
crypto issue in yubikey firmware, it\'s best to generate certificates
for these externally.

I\'ve documented this before in another post, but for accesibility here
it is again.

Create an NSS DB, and generate a certificate signing request:

    certutil -d . -N -f pwdfile.txt
    certutil -d . -R -a -o user.csr -f pwdfile.txt -g 4096 -Z SHA256 -v 24 \
    --keyUsage digitalSignature,nonRepudiation,keyEncipherment,dataEncipherment --nsCertType sslClient --extKeyUsage clientAuth \
    -s "CN=username,O=Testing,L=example,ST=Queensland,C=AU"

Once the request is signed, and your certificate is in \"user.crt\",
import this to the database.

    certutil -A -d . -f pwdfile.txt -i user.crt -a -n TLS -t ",,"
    certutil -A -d . -f pwdfile.txt -i ca.crt -a -n TLS -t "CT,,"

Now export that as a p12 bundle for the yubikey to import.

    pk12util -o user.p12 -d . -k pwdfile.txt -n TLS

Now import this to the yubikey - remember to use slot 9a this time! As
well make sure you set the touch policy NOW, because you can\'t change
it later!

    yubico-piv-tool -s9a -i user.p12 -K PKCS12 -aimport-key -aimport-certificate -k --touch-policy=always

## Setting up your LDAP user

First setup your system to work with LDAP via SSSD. You\'ve done that?
Good! Now it\'s time to get our user ready.

Take our user.crt and convert it to DER:

    openssl x509 -inform PEM -outform DER -in user.crt -out user.der

Now you need to transform that into something that LDAP can understand.
In the future I\'ll be adding a tool to 389-ds to make this
\"automatic\", but for now you can use python:

    python3
    >>> import base64
    >>> with open('user.der', 'r') as f:
    >>>    print(base64.b64encode(f.read))

That should output a long base64 string on one line. Add this to your
ldap user with ldapvi:

    uid=william,ou=People,dc=...
    userCertificate;binary:: <BASE64>

Note that \';binary\' tag has an important meaning here for certificate
data, and the \'::\' tells ldap that this is b64 encoded, so it will
decode on addition.

## Setting up the system

Now that you have done that, you need to teach SSSD how to intepret that
attribute.

In your various SSSD sections you\'ll need to make the following
changes:

    [domain/LDAP]
    auth_provider = ldap
    ldap_user_certificate = userCertificate;binary

    [sssd]
    # This controls OCSP checks, you probably want this enabled!
    # certificate_verification = no_verification

    [pam]
    pam_cert_auth = True

Now the TRICK is letting SSSD know to use certificates. You need to run:

    sudo touch /var/lib/sss/pubconf/pam_preauth_available

With out this, SSSD won\'t even try to process CCID authentication!

Add your ca.crt to the system trusted CA store for SSSD to verify:

    certutil -A -d /etc/pki/nssdb -i ca.crt -n USER_CA -t "CT,,"

Add coolkey to the database so it can find smartcards:

    modutil -dbdir /etc/pki/nssdb -add "coolkey" -libfile /usr/lib64/libcoolkeypk11.so

Check that SSSD can find the certs now:

    # sudo /usr/libexec/sssd/p11_child --pre --nssdb=/etc/pki/nssdb
    PIN for william
    william
    /usr/lib64/libcoolkeypk11.so
    0001
    CAC ID Certificate

If you get no output here you are missing something! If this doesn\'t
work, nothing will!

Finally, you need to tweak PAM to make sure that pam_unix isn\'t getting
in the way. I use the following configuration.

    auth        required      pam_env.so
    # This skips pam_unix if the given uid is not local (IE it's from SSSD)
    auth        [default=1 ignore=ignore success=ok] pam_localuser.so
    auth        sufficient    pam_unix.so nullok try_first_pass
    auth        requisite     pam_succeed_if.so uid >= 1000 quiet_success
    auth        sufficient    pam_sss.so prompt_always ignore_unknown_user
    auth        required      pam_deny.so

    account     required      pam_unix.so
    account     sufficient    pam_localuser.so
    account     sufficient    pam_succeed_if.so uid < 1000 quiet
    account     [default=bad success=ok user_unknown=ignore] pam_sss.so
    account     required      pam_permit.so

    password    requisite     pam_pwquality.so try_first_pass local_users_only retry=3 authtok_type=
    password    sufficient    pam_unix.so sha512 shadow try_first_pass use_authtok
    password    sufficient    pam_sss.so use_authtok
    password    required      pam_deny.so

    session     optional      pam_keyinit.so revoke
    session     required      pam_limits.so
    -session    optional      pam_systemd.so
    session     [success=1 default=ignore] pam_succeed_if.so service in crond quiet use_uid
    session     required      pam_unix.so
    session     optional      pam_sss.so

That\'s it! Restart SSSD, and you should be good to go.

Finally, you may find SELinux isn\'t allowing authentication. This is
really sad that smartcards don\'t work with SELinux out of the box and I
have raised a number of bugs, but check this just in case.

Happy authentication!

