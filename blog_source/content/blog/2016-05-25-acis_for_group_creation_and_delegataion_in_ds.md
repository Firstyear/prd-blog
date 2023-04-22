+++
title = "Acis for group creation and delegataion in DS"
date = 2016-05-25
slug = "2016-05-25-acis_for_group_creation_and_delegataion_in_ds"
# This is relative to the root!
aliases = [ "2016/05/25/acis_for_group_creation_and_delegataion_in_ds.html", "blog/html/2016/05/25/acis_for_group_creation_and_delegataion_in_ds.html" ]
+++
# Acis for group creation and delegataion in DS

Something I get asked about frequently is ACI\'s in Directory Server.
They are a little bit of an art, and they have a lot of edge cases that
you can hit.

I am asked about \"how do I give access to uid=X to create groups in
some ou=Y\".

TL;DR: You want the ACI at the end of the post. All the others are
insecure in some way.

So lets do it.

First, I have my user:

    dn: uid=test,ou=People,dc=example,dc=com
    objectClass: top
    objectClass: account
    objectClass: simpleSecurityObject
    uid: test
    userPassword: {SSHA}LQKDZWFI1cw6EnnYtv74v622aPeNZ9cxXc/QIA==

And I have the ou I want them to edit:

    dn: ou=custom,ou=Groups,dc=example,dc=com
    objectClass: top
    objectClass: organizationalUnit
    ou: custom

So I would put the aci onto ou=custom,ou=Groups,dc=example,dc=com, and
away I go:

    aci: (target = "ldap:///ou=custom,ou=groups,dc=example,dc=com")
         (version 3.0; acl "example"; allow (read, search, write, add)
            (userdn = "ldap:///uid=test,ou=People,dc=example,dc=com");
         )

Great! Now I can add a group under
ou=custom,ou=Groups,dc=example,dc=com!

But this ACI is REALLY BAD AND INSECURE. Why?

First, it allows uid=test,ou=People,dc=example,dc=com write access to
the ou=custom itself, which means that it can alter the aci, and
potentially grant further rights. That\'s bad.

So lets tighten that up.

    aci: (target = "ldap:///cn=*,ou=custom,ou=groups,dc=example,dc=com")
         (version 3.0; acl "example"; allow (read, search, write, add) 
            (userdn = "ldap:///uid=test,ou=People,dc=example,dc=com");
         )

Better! Now we can only create objects with cn=\* under that ou, and we
can\'t edit the ou or it\'s aci\'s itself. But this is still insecure!
Imagine, that I made:

    dn: cn=fake_root,ou=custom,ou=groups,dc=example,dc=com
    ....
    uid: xxxx
    userClass: secure
    memberOf: cn=some_privileged_group,....

Many sites often have their pam_ldap/nslcd/sssd set to search from the
*root* IE dc=example,dc=com. Because ldap doesn\'t define a *sort* order
of responses, this entry may over-ride an exist admin user, or it could
be a new user that matches authorisation filters. This just granted
someone in your org access to all your servers!

But we can prevent this.

    aci: (target = "ldap:///cn=*,ou=custom,ou=groups,dc=example,dc=com")
         (targetfilter="(&(objectClass=top)(objectClass=groupOfUniqueNames))")
         (version 3.0; acl "example"; allow (read, search, write, add)
            (userdn = "ldap:///uid=test,ou=People,dc=example,dc=com");
         )

Looks better! Now we can only create objects with objectClass top, and
groupOfUniqueNames.

Then again \....

    dn: cn=bar,ou=custom,ou=Groups,dc=example,dc=com
    objectClass: top
    objectClass: groupOfUniqueNames
    objectClass: simpleSecurityObject
    cn: bar
    userPassword: {SSHA}UYVTFfPFZrN01puFXYJM3nUcn8lQcVSWtJmQIw==

Just because we say it has to have top and groupOfUniqueNames DOESN\'T
exclude adding more objectClasses!

Finally, if we make the delegation aci:

    # This is the secure aci
    aci: (target = "ldap:///cn=*,ou=custom,ou=groups,dc=example,dc=com")
         (targetfilter="(&(objectClass=top)(objectClass=groupOfUniqueNames))")
         (targetattr="cn || uniqueMember || objectclass")
         (version 3.0; acl "example"; allow (read, search, write, add)
            (userdn = "ldap:///uid=test,ou=People,dc=example,dc=com");
         )

This aci limits creation to *only* groups of unique names and top, and
limits the attributes to only what can be made in those objectClasses.
*Finally* we have a secure aci. Even though we can add other
objectClasses, we can never actually add the attributes to satisfy them,
so we effectively limit this to the types show. Even if we add other
objectClasses that take \"may\" as the attribute, we can never fill in
those attributes either.

Summary: Acis are hard.

