+++
title = "KRB5 setup for ldap server testing"
date = 2015-11-05
slug = "2015-11-05-KRB5_setup_for_ldap_server_testing"
# This is relative to the root!
aliases = [ "2015/11/05/KRB5_setup_for_ldap_server_testing.html", "blog/html/2015/11/05/KRB5_setup_for_ldap_server_testing.html" ]
+++
# KRB5 setup for ldap server testing

UPDATE: 2019 this is now automated, but I [don\'t recommend using
kerberos - read more
here.](/blog/html/2017/05/23/kerberos_why_the_world_moved_on.html)

This will eventually get automated, but here is a quick krb recipe for
testing. Works in docker containers too!

## \-- krb5 without ldap backend.

Add kerberos.example.com as an entry to /etc/hosts for this local
machine. It should be the first entry.

Edit /etc/krb5.conf.d/example.com

NOTE: This doesn\'t work, you need to add it to krb5.conf. Why doesn\'t
it work?

    [realms]
    EXAMPLE.COM = {
     kdc = kerberos.example.com
     admin_server = kerberos.example.com
    }

    [domain_realm]
    .example.com = EXAMPLE.COM
    example.com = EXAMPLE.COM

Edit /var/kerberos/krb5kdc/kdc.conf

\# Note, I think the defalt kdc.conf is good. :

    [kdcdefaults]
     kdc_ports = 88
     kdc_tcp_ports = 88

    [realms]
     EXAMPLE.COM = {
      #master_key_type = aes256-cts
      acl_file = /var/kerberos/krb5kdc/kadm5.acl
      dict_file = /usr/share/dict/words
      admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
      supported_enctypes = aes256-cts:normal aes128-cts:normal des3-hmac-sha1:normal arcfour-hmac:normal camellia256-cts:normal camellia128-cts:normal des-hmac-sha1:normal des-cbc-md5:normal des-cbc-crc:normal
     }

Now setup the database.

    /usr/sbin/kdb5_util create -r EXAMPLE.COM -s  # Prompts for password. Is there a way to avoid prompt?

Edit /var/kerberos/krb5kdc/kadm5.acl

    /usr/sbin/kadmin.local -r EXAMPLE.COM -q listprincs

Add our LDAP servers

\# There is a way to submit these on the CLI, but I get kadmin.local:
Cannot find master key record in database while initializing
kadmin.local interface

    /usr/sbin/kadmin.local -r EXAMPLE.COM                                                                
    add_principal -randkey ldap/kerberos.example.com@EXAMPLE.COM
    ktadd -k /opt/dirsrv/etc/dirsrv/slapd-localhost/ldap.keytab ldap/kerberos.example.com
    add_principal -pw password client
    exit

Start the kdc

    /usr/sbin/krb5kdc -P /var/run/krb5kdc.pid -r EXAMPLE.COM

OR

    # You need to edit /etc/sysconfig/krb5kdc and put -r EXAMPLE.COM into args
    systemctl start krb5kdc

    KRB5_TRACE=/tmp/foo kinit client@EXAMPLE.COM
    klist
    Ticket cache: KEYRING:persistent:0:0
    Default principal: client@EXAMPLE.COM

    Valid starting     Expires            Service principal
    05/11/15 11:35:37  06/11/15 11:35:37  krbtgt/EXAMPLE.COM@EXAMPLE.COM

Now setup the DS instance.

    # Note, might be dirsrv in newer installs.
    chown nobody: /opt/dirsrv/etc/dirsrv/slapd-localhost/ldap.keytab

Add:

    KRB5_KTNAME=/opt/dirsrv/etc/dirsrv/slapd-localhost/ldap.keytab ; export KRB5_KTNAME    

To /opt/dirsrv/etc/sysconfig/dirsrv-localhost

Now restart the DS

    /opt/dirsrv/etc/rc.d/init.d/dirsrv restart

Add a client object:

    uid=client,ou=People,dc=example,dc=com
    objectClass: top
    objectClass: account
    uid: client

Now check the GSSAPI is working.

    ldapwhoami -Y GSSAPI -H ldap://kerberos.example.com:389    
    SASL/GSSAPI authentication started
    SASL username: client@EXAMPLE.COM
    SASL SSF: 56
    SASL data security layer installed.
    dn: uid=client,ou=people,dc=example,dc=com

All ready to go!

I have created some helpers in lib389 that are able to do this now.

TODO: How to setup krb5 with ldap backend.

create instance:

/opt/dirsrv/sbin/setup-ds.pl \--silent \--debug
\--file=/home/wibrown/development/389ds/setup.inf

Now, add the krb5 schema

cd /opt/dirsrv/etc/dirsrv/slapd-localhost/schema ln -s
../../../../../../usr/share/doc/krb5-server-ldap/60kerberos.ldif

/opt/dirsrv/etc/rc.d/init.d/dirsrv restart

Query the schema:

python
/home/wibrown/development/389ds/lib389/clitools/ds_schema_attributetype_list.py
\| grep krb
