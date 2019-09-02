LDAP Guide Part 3: Filters
==========================

.. contents::

In part 2 we discussed how to use searchbases to control what objects were returned from a search by their organisation in the LDAP Tree. We also touched on a simple filter to limit
the result by a single search item.

::

    '(cn=HR Managers)'

If we change this to a different part of the tree, we'll get back too many entries:

*REMEMBER*: All examples in this page work and can be "copy-pasted" so you can try these searches for yourself!

::

    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com'

If this database has thousands of users, we wouldn't be able to scale or handle this. We need to be able to use filters to effectively search for objects.

Simple Filters
--------------

As mentioned before filters are of the format:

::

    (attribute operator value)
    (condition (...) )

These filters are rooted in `set mathematics <https://en.wikipedia.org/wiki/Set_(mathematics)>`_ which may be good as an additional reference.

Filters apply to objects attribute values - not the DN. Remember though, the RDN *must* be an attribute of the object, so you can filter on this. It's a good idea to look at an object to understand what you could filter on:

::

    # test0002, People, example.com
    dn: uid=test0002,ou=People,dc=example,dc=com
    objectClass: top
    objectClass: person
    objectClass: organizationalPerson
    objectClass: inetOrgPerson
    objectClass: posixAccount
    objectClass: shadowAccount
    cn: guest0002
    sn: guest0002
    uid: guest0002
    uid: test0002
    givenName: givenname0002
    description: description0002
    mail: uid0002
    uidNumber: 2
    gidNumber: 2
    shadowMin: 0
    shadowMax: 99999
    shadowInactive: 30
    shadowWarning: 7
    homeDirectory: /home/uid0002
    shadowLastChange: 17427


Equality Filters
----------------

An equality filter requests all objects where attribute is equal to value. IE:

::

    '(uid=test0009)'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(uid=test0009)'

Presence Filter
---------------

A presence filter requests all objects where the attribute is present and has a valid value, but we do not care what the value is.

::

    '(uid=*)'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(uid=*)'

Range Filters
-------------

A range filter requests all objects whose attribute values are greater than or less than a value.

::

    '(uid>=test0005)'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(uid>=test0005)'

    '(uid<=test0005)'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(uid<=test0005)'

Substring filters
-----------------

This requests a partial match of an attribute value on the object. You can use the '*' operator multiple times.

::

    '(uid=*005)'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(uid=*005)'
    '(uid=*st000*)'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(uid=*st000*)'

NOTE: You should always have at least 3 characters in your substring filter, else indexes may not operate efficently. IE this filter may not work efficently:

::

    '(uid=*05)'

AND filters
-----------

Using the filters above we can begin to construct more complex queries. AND requires that for an object to match, all child filter elements must match. This is the "intersection" operation.

::

    '(&(uid=test0006)(uid=guest0006))'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(&(uid=test0006)(uid=guest0006))'

Because the object has both uid=test0006 and uid=guest0006, this returns the object uid=test0006,ou=People,dc=example,dc=com. However, if we changed this condition:

::

    '(&(uid=test0006)(uid=guest0007))'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(&(uid=test0006)(uid=guest0007))'

No objects match both predicates, so we have an empty result set.

OR filters
----------

OR filters will return the aggregate of all child filters. This is the union operation. Provided an object satisfies one condition of the OR, it will be part of the returned set.

::

    '(|(uid=test0006)(uid=guest0007))'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(|(uid=test0006)(uid=guest0007))'

If an object is matched twice in the OR filter, we only return it once.

::

    '(|(uid=test0008)(uid=guest0008))'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(|(uid=test0008)(uid=guest0008))'

NOT filters
-----------

A NOT filter acts to invert the result of the inner set. NOT is the equivalent of a negating AND. For example:

::

    '(!(uid=test0010))'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(!(uid=test0010))'

You can't list multiple parameters to a not condition however:

::

    '(!(uid=test0010)(uid=test0009))'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(!(uid=test0010)(uid=test0009))'
    ...
    ldap_search_ext: Bad search filter (-7)

To combine NOT's you need to use this in conjunction with AND and OR.

Complex filters
---------------

Because AND OR and NOT are filters in their own right, you can nest these to produce more complex directed queries.

::

    '(&(objectClass=person)(objectClass=posixAccount)(|(uid=test000*))(!(uid=test0001)))'
    ldapsearch -H ldap://exampleldap.blackhats.net.au:3389 -x -s sub -b 'ou=People,dc=example,dc=com' '(&(objectClass=person)(objectClass=posixAccount)(|(uid=test000*))(!(uid=test0001)))' uid

I find it useful to break this down to see what is happening

::

    (&
        (objectClass=person)
        (objectClass=posixAccount)
        (|
            (uid=test000*)
        )
        (!(uid=test0001))
    )

This query expresses "All person whose name starts with test000* and not test0001". Once broken down over multiple lines like this it's easy to see which filters belong to which logic components, and how they will interact.

Conclusion
----------

While search bases can help you to direct a query, filters are how searches are efficently expressed over databases of millions of objects. Being able to use them effectively will help your client applications be much faster.

`PART 4, schema! <ldap_guide_part_4_schema_and_objects.html>`_

