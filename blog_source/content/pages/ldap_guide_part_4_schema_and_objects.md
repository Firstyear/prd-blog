+++
title = "LDAP Guide Part 4: Schema and Objects"
slug = "ldap_guide_part_4_schema_and_objects"
date = 2016-07-08
# This is relative to the root!
aliases = [ "blog/html/pages/ldap_guide_part_4_schema_and_objects.html" ]
+++
# LDAP Guide Part 4: Schema and Objects

So far we have seen that LDAP is a tree based database, that allows
complex filters over objects attribute value pairs.

Unlike a no-sql or schemaless database, LDAP has a schema for it\'s
objects, making it stricter than json or other similar-looking
representations. This schema is based on objectClasses, similar to
object-oriented programming.

## Searching the schema

Sadly, schema is a bit difficult to parse due to it\'s representation as
a single object. You can show all the objectClasses and attributeTypes
definitions with the following search.

    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -b 'cn=schema' '(objectClass=*)' +

*note*: We have a tool in development that makes searching for these
details easier, but we haven\'t released it yet.

You\'ll notice two important types here. The first is an attributeType:

    attributeTypes: ( 2.5.4.4 NAME ( 'sn' 'surName' )  SUP name
     EQUALITY caseIgnoreMatch SUBSTR caseIgnoreSubstringsMatch
     SYNTAX 1.3.6.1.4.1.1466.115.121.1.15 X-ORIGIN 'RFC 4519'
     X-DEPRECATED 'surName' )

This is the definition of how an attribute is named and represented. We
can see this attribute can be named \"sn\" or \"surName\" (but surName
is deprecated), it uses a case-insensitive match for checks (ie Brown
and brown are the same), and the syntax oid defines the data this can
hold: in this case a utf8 string.

For the most part you won\'t need to play with attributeTypes unless you
have an odd data edge case you are trying to represent.

The second important type is the objectClass definition:

    objectClasses: ( 2.5.6.6 NAME 'person' SUP top STRUCTURAL MUST ( sn $ cn )
     MAY ( userPassword $ telephoneNumber $ seeAlso $ description )
     X-ORIGIN 'RFC 4519' )

This defines an objectClass called \"person\". It\'s parent is the
\"top\" objectClass, and for this to exist on an object the object MUST
have sn and cn attributes present. You may optionally include the MAY
attributes on the object also.

## Example

So using our person objectclass we can create a simple object:

    cn=user,dc=...
    objectClass: top
    objectClass: person
    cn: user
    sn: user

Let\'s go through a few things. First, note that the rdn (cn=user), is a
valid attribute on the object (cn: user). If we omitted this or changed
it, it would not be valid. This for example is invalid:

    cn=user,dc=...
    objectClass: top
    objectClass: person
    cn: somethingelse
    sn: user
    description: invalid!

If we don\'t satisfy the schema\'s \"MUST\" requirements, the object is
also invalid:

    cn=user,dc=...
    objectClass: top
    objectClass: person
    sn: user
    description: invalid, missing cn!

It IS valid to add any of the MAY types to an object of course, but they
can also be absent (as per the examples above):

    cn=user,dc=...
    objectClass: top
    objectClass: person
    cn: user
    sn: user
    telephoneNumber: 0118999....
    description: valid with may attrs.

## Complex objects

You are not limited to a single objectClass per object either. You can
list multiple objectClasses:

    objectClass: account
    objectClass: inetOrgPerson
    objectClass: inetUser
    objectClass: ldapPublicKey
    objectClass: ntUser
    objectClass: organizationalPerson
    objectClass: person
    objectClass: posixaccount
    objectClass: top

Provided that all the MUST requirements of all objectClasses are
satisfied, this is valid.

If an attribute exists in both a MUST and a MAY of an objectClass, then
the stricter requirement is enforced, IE MUST. Here, both objectClasses
define cn, but ldapsubentry defines it as \"MAY\" and person as
\"MUST\". Therfore, on an object that contained both of these, CN is a
must attribute.

    objectClasses: ( 2.16.840.1.113719.2.142.6.1.1 NAME 'ldapSubEntry' DESC 'LDAP 
     Subentry class, version 1' SUP top STRUCTURAL MAY cn X-ORIGIN 'LDAP Subentry 
     Internet Draft' )
    objectClasses: ( 2.5.6.6 NAME 'person' SUP top STRUCTURAL MUST ( sn $ cn )
     MAY ( userPassword $ telephoneNumber $ seeAlso $ description )
     X-ORIGIN 'RFC 4519' )

## Building your own objects

Knowing this now you can use this to create your own objects. There are
some common attributes that generally need to be satisfied to allow user
objects to resolve on unix systems. You\'ll probably need:

-   uid
-   displayName
-   loginShell
-   homeDirectory
-   uidNumber
-   gidNumber
-   memberOf

For a group to resolve you need:

-   gidNumber
-   member

*NOTE*: This is assuming rfc2307bis behaviour for your client. In sssd
this is \"ldap_schema = rfc2307bis\", in the domain provider. For other
clients you may need to alter other parameters. This is the most
efficent way to resolve groups and users on unix, so strongly consider
it.

Knowing you need these values, you can search the schema to create
objectClass definitions to match. Try this out:

## Answers

For the group, this is pretty easy. You should have:

    objectClass: top
    objectClass: posixGroup
    objectClass: groupOfNames

The user is a bit tricker. You should have something similar to:

    objectClass: top
    objectClass: account
    objectClass: person
    objectClass: posixAccount

Remember, there is more than one way to put these objects together to
have valid attributes that you require - just try to make sure you pick
classes that don\'t have excess attributes. A bad choice for example is:

    objectClass: top
    objectClass: nsValueItem

nsValueItem gives you a \"MUST\" cn, but it gives \"MAY\" of many other
attributes you will never use or need. So account or person are better
choices. Generally the clue is in the objectClass name.

If you have your own LDAP server you can try creating objects now with
these classes.
