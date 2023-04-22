+++
title = "ldctl to generate test objects"
date = 2016-02-23
slug = "2016-02-23-ldctl_to_generate_test_objects"
# This is relative to the root!
aliases = [ "2016/02/23/ldctl_to_generate_test_objects.html" ]
+++
# ldctl to generate test objects

I was told by some coworkers today at Red Hat that I can infact use
ldctl to generate my databases for load testing with 389-ds.

First, create a template.ldif

    objectClass: top
    objectclass: person
    objectClass: organizationalPerson
    objectClass: inetorgperson
    objectClass: posixAccount
    objectClass: shadowAccount
    sn: testnew[A]
    cn: testnew[A]
    uid: testnew[A]
    givenName: testnew[A]
    description: description[A]
    userPassword: testnew[A]
    mail: testnew[A]@redhat.com
    uidNumber: 3[A]
    gidNumber: 4[A]
    shadowMin: 0
    shadowMax: 99999
    shadowInactive: 30
    shadowWarning: 7
    homeDirectory: /home/uid[A]

Now you can use ldctl to actually load in the data:

    ldclt -h localhost -p 389 -D "cn=Directory Manager" -w password -b "ou=people,dc=example,dc=com" \
    -I 68 -e add,commoncounter -e "object=/tmp/template.ldif,rdn=uid:[A=INCRNNOLOOP(0;3999;5)]"

Thanks to vashirov and spichugi for their advice and this example!
