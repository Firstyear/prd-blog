+++
title = "Where does that attribute belong?"
date = 2015-12-04
slug = "2015-12-04-Where_does_that_attribute_belong"
# This is relative to the root!
aliases = [ "2015/12/04/Where_does_that_attribute_belong.html", "blog/html/2015/12/04/Where_does_that_attribute_belong.html" ]
+++
# Where does that attribute belong?

A lot of the time in ldap, you spend your time scratching your head
thinking \"Hey, I wish I knew what objectclass I needed for attribute
X\".

Yes, you can go through the schema, grep out what objectclasses. But
it\'s a bit tedious, and it\'s also not very accessible.

In lib389 I have written a pair of tools to help with this.

    lib389/clitools/ds_schema_attributetype_list.py
    lib389/clitools/ds_schema_attributetype_query.py

List does what you expect: It lists the attributes available on a
server, but does so neatly compared to ldapsearch -b cn=schema. The
output for comparison:

ldapsearch -b \'cn=schema\' -x \'(objectClass=\*)\' attributeTypes :

    ...
    attributeTypes: ( 1.2.840.113556.1.2.102 NAME 'memberOf' DESC 'Group that the 
     entry belongs to' SYNTAX 1.3.6.1.4.1.1466.115.121.1.12 X-ORIGIN 'Netscape Del
     egated Administrator' )
    ...

python lib389/clitools/ds_schema_attributetype_list.py -i localhost :

    ( 1.2.840.113556.1.2.102 NAME 'memberOf' DESC 'Group that the entry belongs to' SYNTAX 1.3.6.1.4.1.1466.115.121.1.12 X-ORIGIN 'Netscape Delegated Administrator' )

The big difference is that it\'s on one line: Much easier to grep
through.

The real gem is the query tool.

    python lib389/clitools/ds_schema_attributetype_query.py -i localhost -a memberOf
    ( 1.2.840.113556.1.2.102 NAME 'memberOf' DESC 'Group that the entry belongs to' SYNTAX 1.3.6.1.4.1.1466.115.121.1.12 X-ORIGIN 'Netscape Delegated Administrator' )
    MUST
    MAY
    ( 2.16.840.1.113730.3.2.130 NAME 'inetUser' DESC 'Auxiliary class which must be present in an entry for delivery of subscriber services' SUP top AUXILIARY MAY ( uid $ inetUserStatus $ inetUserHttpURL $ userPassword $ memberOf ) )
    ( 2.16.840.1.113730.3.2.112 NAME 'inetAdmin' DESC 'Marker for an administrative group or user' SUP top AUXILIARY MAY ( aci $ memberOf $ adminRole ) )

Shows you the attribute, and exactly which objectClasses MAY and MUST
host this attribute. Additionally, because we give you the objectClasses
too, you can see the implications of which one you want to enable an add
to your object.

Happy schema querying.

\<pre\>EDIT 2015-12-07 \</pre\> Viktor A pointed out that you can do the
following:

    ldapsearch -o ldif-wrap=no -x -b 'cn=schema'  '(objectClass=*)' attributeTypes
    ...
    attributeTypes: ( 2.16.840.1.113730.3.1.612 NAME 'generation' DESC 'Netscape defined attribute type' SYNTAX 1.3.6.1.4.1.1466.115.121.1.26 X-ORIGIN 'Netscape Directory Server' )
    </pre> 

    This will put all the results onto one line rather than wrapping at 80. Additionally, if you find results that are base64ed:

    un64ldif () {
     while read l; do
      echo "$l" | grep '^\([^:]\+: \|$\)' || \
       echo "${l%%:: *}: $(base64 -d <<< "${l#*:: }")"
     done
     return 0
    }

Thanks for the comment! 41
