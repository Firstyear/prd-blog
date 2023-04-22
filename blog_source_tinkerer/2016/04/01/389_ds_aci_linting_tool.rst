389 ds aci linting tool
=======================

In the past I have discussed aci's and their management in directory server.

It's a very complex topic, and there are issues that can arise.

I have now created an aci linting tool which can connect to a directory server and detect common mistakes in acis, along with explinations of how to correct them.

This will be in a release of lib389 in the future. For now, it's under review and hopefully will be accepted soon!

Here is sample output below.

::

    -------------------------------------------------------------------------------
    Directory Server Aci Lint Error: DSALE0001
    Severity: HIGH

    Affected Acis:
    (targetattr!="userPassword")(version 3.0; acl "Enable anonymous access"; allow (read, search, compare) userdn="ldap:///anyone";)
    (targetattr !="cn || sn || uid")(targetfilter ="(ou=Accounting)")(version 3.0;acl "Accounting Managers Group Permissions";allow (write)(groupdn = "ldap:///cn=Accounting Managers,ou=groups,dc=example,dc=com");)
    (targetattr !="cn || sn || uid")(targetfilter ="(ou=Human Resources)")(version 3.0;acl "HR Group Permissions";allow (write)(groupdn = "ldap:///cn=HR Managers,ou=groups,dc=example,dc=com");)
    (targetattr !="cn ||sn || uid")(targetfilter ="(ou=Product Testing)")(version 3.0;acl "QA Group Permissions";allow (write)(groupdn = "ldap:///cn=QA Managers,ou=groups,dc=example,dc=com");)
    (targetattr !="cn || sn || uid")(targetfilter ="(ou=Product Development)")(version 3.0;acl "Engineering Group Permissions";allow (write)(groupdn = "ldap:///cn=PD Managers,ou=groups,dc=example,dc=com");)

    Details: 
    An aci of the form "(targetAttr!="attr")" exists on your system. This aci
    will internally be expanded to mean "all possible attributes including system,
    excluding the listed attributes".

    This may allow access to a bound user or anonymous to read more data about
    directory internals, including aci state or user limits. In the case of write 
    acis it may allow a dn to set their own resource limits, unlock passwords or
    their own aci.

    The ability to change the aci on the object may lead to privilege escalation in
    some cases.
                        

    Advice: 
    Convert the aci to the form "(targetAttr="x || y || z")".
                        
    -------------------------------------------------------------------------------
    Directory Server Aci Lint Error: DSALE0002
    Severity: HIGH

    Affected Acis:
    ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Accounting)")(version 3.0;acl "Accounting Managers Group Permissions";allow (write)(groupdn = "ldap:///cn=Accounting Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Human Resources)")(version 3.0;acl "HR Group Permissions";allow (write)(groupdn = "ldap:///cn=HR Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn ||sn || uid")(targetfilter ="(ou=Product Testing)")(version 3.0;acl "QA Group Permissions";allow (write)(groupdn = "ldap:///cn=QA Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Product Development)")(version 3.0;acl "Engineering Group Permissions";allow (write)(groupdn = "ldap:///cn=PD Managers,ou=groups,dc=example,dc=com");)

    ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Human Resources)")(version 3.0;acl "HR Group Permissions";allow (write)(groupdn = "ldap:///cn=HR Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Accounting)")(version 3.0;acl "Accounting Managers Group Permissions";allow (write)(groupdn = "ldap:///cn=Accounting Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn ||sn || uid")(targetfilter ="(ou=Product Testing)")(version 3.0;acl "QA Group Permissions";allow (write)(groupdn = "ldap:///cn=QA Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Product Development)")(version 3.0;acl "Engineering Group Permissions";allow (write)(groupdn = "ldap:///cn=PD Managers,ou=groups,dc=example,dc=com");)

    ou=People,dc=example,dc=com (targetattr !="cn ||sn || uid")(targetfilter ="(ou=Product Testing)")(version 3.0;acl "QA Group Permissions";allow (write)(groupdn = "ldap:///cn=QA Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Accounting)")(version 3.0;acl "Accounting Managers Group Permissions";allow (write)(groupdn = "ldap:///cn=Accounting Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Human Resources)")(version 3.0;acl "HR Group Permissions";allow (write)(groupdn = "ldap:///cn=HR Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Product Development)")(version 3.0;acl "Engineering Group Permissions";allow (write)(groupdn = "ldap:///cn=PD Managers,ou=groups,dc=example,dc=com");)

    ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Product Development)")(version 3.0;acl "Engineering Group Permissions";allow (write)(groupdn = "ldap:///cn=PD Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Accounting)")(version 3.0;acl "Accounting Managers Group Permissions";allow (write)(groupdn = "ldap:///cn=Accounting Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn || sn || uid")(targetfilter ="(ou=Human Resources)")(version 3.0;acl "HR Group Permissions";allow (write)(groupdn = "ldap:///cn=HR Managers,ou=groups,dc=example,dc=com");)
    |- ou=People,dc=example,dc=com (targetattr !="cn ||sn || uid")(targetfilter ="(ou=Product Testing)")(version 3.0;acl "QA Group Permissions";allow (write)(groupdn = "ldap:///cn=QA Managers,ou=groups,dc=example,dc=com");)


    Details: 
    Acis on your system exist which are both not equals targetattr, and overlap in
    scope.

    The way that directory server processes these, is to invert them to to white
    lists, then union the results.

    As a result, these acis *may* allow access to the attributes you want them to
    exclude.

    Consider:

    aci: (targetattr !="cn")(version 3.0;acl "Self write all but cn";allow (write)
        (userdn = "ldap:///self");)
    aci: (targetattr !="sn")(version 3.0;acl "Self write all but sn";allow (write)
        (userdn = "ldap:///self");)

    This combination allows self write to *all* attributes within the subtree.

    In cases where the target is members of a group, it may allow a member who is
    within two groups to have elevated privilege.
                        

    Advice: 
    Convert the aci to the form "(targetAttr="x || y || z")".

    Prevent the acis from overlapping, and have them on unique subtrees.
                        
    -------------------------------------------------------------------------------
    FAIL



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
