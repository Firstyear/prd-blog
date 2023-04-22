+++
title = "Managing replication conflicts for humans in 389"
date = 2015-11-25
slug = "2015-11-25-Managing_replication_conflicts_for_humans_in_389"
# This is relative to the root!
aliases = [ "2015/11/25/Managing_replication_conflicts_for_humans_in_389.html" ]
+++
# Managing replication conflicts for humans in 389

I would like to thank side_control at runlevelone dot net for putting me
onto this challenge.

If we have a replication conflict in 389, we generall have two results.
A and B. In the case A is the live object and B is the conflict, and we
want to keep A as live object, it\'s as easy as:

    dn: idnsname=_kerberos._udp.Default-First-Site-Name._sites.dc._msdcs+nsuniqueid=910d8837-4c3c11e5-83eea63b-366c3f94,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    changetype: delete

But say we want to swap them over: We want to keep B, but A is live. How
do we recover this?

I plan to make a tool to do this, because it\'s a right pain.

This is the only way I got it to work, but I suspect there is a shortcut
somewhere that doesn\'t need the blackmagic that is extensibleObject.
(If you use extensibleObject in production I will come for your
personally.)

First, we need to get the object out of being a multivalued rdn object
so we can manipulate it easier. We give it a cn to match it\'s uniqueId.

    dn: idnsname=_kerberos._udp.dc._msdcs+nsuniqueid=910d8842-4c3c11e5-83eea63b-366c3f94,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    changetype: modify
    add: cn
    cn: 910d8842-4c3c11e5-83eea63b-366c3f94
    -
    replace: objectClass
    objectClass: extensibleObject
    objectClass: idnsrecord
    objectClass: top
    -

    dn: idnsname=_kerberos._udp.dc._msdcs+nsuniqueid=910d8842-4c3c11e5-83eea63b-366c3f94,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    changetype: modrdn
    newrdn: cn=910d8842-4c3c11e5-83eea63b-366c3f94
    deleteoldrdn: 0
    newsuperior:
    idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan

Now, we can get rid of the repl conflict:

    dn: cn=910d8842-4c3c11e5-83eea63b-366c3f94,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    changetype: modify
    delete: nsds5ReplConflict
    nsds5ReplConflict:
    namingConflictidnsname=_kerberos._udp.dc._msdcs,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    -

We have \"B\" ready to go. So lets get A out of the way, and drop B in.

    dn: idnsname=_kerberos._udp.Default-First-Site-Name._sites.dc._msdcs+nsuniqueid=910d8837-4c3c11e5-83eea63b-366c3f94,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    changetype: delete

    dn: cn=910d8842-4c3c11e5-83eea63b-366c3f94,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    changetype: modrdn
    newrdn: idnsName=_kerberos._udp.dc._msdcs
    deleteoldrdn: 0
    newsuperior: idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan

Finally, we need to fix the objectClass and get rid of the cn.

    dn: idnsName=_kerberos._udp.dc._msdcs,idnsname=lab.example.lan.,cn=dns,dc=lab,dc=example,dc=lan
    changetype: modify
    delete: cn
    cn: 910d8842-4c3c11e5-83eea63b-366c3f94
    -
    replace: objectClass
    objectClass: idnsrecord
    objectClass: top
    -

I think a tool to do this would be really helpful.
