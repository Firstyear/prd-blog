Unit testing LDAP acis for fun and profit
=========================================
My workplace is a reasonably sized consumer of 389ds. We use it for storing pretty much all our most important identity data from allowing people to authenticate, to group and course membership, to email routing and even internet access. 

As a result, it's a really important service to maintain. We need to treat it as one of the most security sensitive services we run. The definition of security I always come back to is "availability, integrity and confidentiality". Now, we have a highly available environment, and we use TLS with our data to ensure confidentiality of results and queries. Integrity however, is the main target of this post.

LDAP allows objects that exist with in the directory to "bind" (authenticate) and then to manipulate other objects in the directories. A set of ACIs (Access Control Instructions) define what objects can modify other objects and their attributes.

ACIs are probably one of the most complex parts in a directory server environment to "get right" (With the exception maybe of VLV). 

I noticed during a security review of our directories ACIs that took the following pattern. 

::
    
    aci: (targetattr !="cn")(version 3.0;acl "Self write all but cn";allow (write)(userdn = "ldap:///self");)
    aci: (targetattr !="sn")(version 3.0;acl "Self write all but sn";allow (write)(userdn = "ldap:///self");)
    

Now, the rules in question we had were more complex and had more rules, but at their essence looked like this. Seems like an innocuous set of rules. "Allow self write to everything but sn" and "Allow self write to everything but cn".

So at the end we expect to see we can write everything but sn and cn.

Lets use the ldap effective permissions capability to check this:

::
    
    /usr/lib64/mozldap/ldapsearch -D 'cn=Directory Manager' -w - -b 'cn=test,ou=people,dc=example,dc=net,dc=au' \
    -J "1.3.6.1.4.1.42.2.27.9.5.2:false:dn: cn=test,ou=people,dc=example,dc=net,dc=au" "(objectClass=*)"
    
    version: 1
    dn: cn=test,ou=People,dc=example,dc=net,dc=au
    objectClass: top
    objectClass: person
    cn: test
    sn: test
    userPassword: 
    entryLevelRights: v
    attributeLevelRights: objectClass:rscwo, cn:rscwo, sn:rscwo, userPassword:wo
    
    

What! Why does cn have r[ead] s[search] c[ompare] w[rite] o[bliterate]? That was denied? Same for SN.

Well, LDAP treats ACIs as a positive union.

So we have:

::
    
    aci 1 = ( objectclass, sn, userpassword)
    aci 2 = ( objectclass, cn, userpassword)
    aci 1 U aci 2 = ( objectclass, sn, cn, userpassword )
    

As a result, our seemingly secure rules, actually were conflicting and causing our directory to be highly insecure!

So, easy to change this: First we invert the rules (be explicit in all things) to say targetattr = "userpassword" for example. We shouldn't use != rules because they can even conflict between groups and self.

How do we detect these issues though?

I wrote a python library called usl (university simple ldap). In this I have a toolset for unit testing our ldap acis. 

We create a py.test testcase, that states for some set of objects, they should have access to some set of attributes on a second set of objects. IE group admins should have rscwo on all other objects.

We can then run these tests and determine if this is or isn't the case. For example, if we wrote two test cases for the above to test that "self has rscwo to all attributes or self except sn which should be rsc" and a second test "self has rscwo to all attributes or self except cn which should be rsc". Our test cases would have failed, and we would be alerted to these issues.

As a result of these tests for our acis I was able to find many more security issues: Such as users who could self modify groups, self modify acis, account lockouts of other users, or even turn themselves into a container object and create children. At the worst one aci actually allowed objects to edit their own aci's which would have allowed them to give themself more access potentially. The largest offender were rules that defined targetattr != rules: Often these were actually allowing access to write attributes that administrators would over look. 

For example, the rule above allowing all write except cn, would actually allow access to nsAccountLock, nsSizeLimit and other object attributes that don't show up on first inspection. The complete list is below. (Note the addition of the '+' )

::
    
    /usr/lib64/mozldap/ldapsearch -D 'cn=Directory Manager' -w - -b 'cn=test,ou=people,dc=example,dc=net,dc=au' \
    -J "1.3.6.1.4.1.42.2.27.9.5.2:false:dn: cn=test,ou=people,dc=example,dc=net,dc=au" "(objectClass=*)" '+'
    version: 1
    dn: cn=test,ou=People,dc=example,dc=net,dc=au
    entryLevelRights: v
    attributeLevelRights: nsPagedLookThroughLimit:rscwo, passwordGraceUserTime:rsc
     wo, pwdGraceUserTime:rscwo, modifyTimestamp:rscwo, passwordExpWarned:rscwo, 
     pwdExpirationWarned:rscwo, internalModifiersName:rscwo, entrydn:rscwo, dITCo
     ntentRules:rscwo, supportedLDAPVersion:rscwo, altServer:rscwo, vendorName:rs
     cwo, aci:rscwo, nsSizeLimit:rscwo, attributeTypes:rscwo, acctPolicySubentry:
     rscwo, nsAccountLock:rscwo, passwordExpirationTime:rscwo, entryid:rscwo, mat
     chingRuleUse:rscwo, nsIDListScanLimit:rscwo, nsSchemaCSN:rscwo, nsRole:rscwo
     , retryCountResetTime:rscwo, tombstoneNumSubordinates:rscwo, supportedFeatur
     es:rscwo, ldapSchemas:rscwo, copiedFrom:rscwo, nsPagedIDListScanLimit:rscwo,
      internalCreatorsName:rscwo, nsUniqueId:rscwo, lastLoginTime:rscwo, creators
     Name:rscwo, passwordRetryCount:rscwo, dncomp:rscwo, vendorVersion:rscwo, nsT
     imeLimit:rscwo, passwordHistory:rscwo, pwdHistory:rscwo, objectClasses:rscwo
     , nscpEntryDN:rscwo, subschemaSubentry:rscwo, hasSubordinates:rscwo, pwdpoli
     cysubentry:rscwo, structuralObjectClass:rscwo, nsPagedSizeLimit:rscwo, nsRol
     eDN:rscwo, createTimestamp:rscwo, accountUnlockTime:rscwo, dITStructureRules
     :rscwo, supportedSASLMechanisms:rscwo, supportedExtension:rscwo, copyingFrom
     :rscwo, nsLookThroughLimit:rscwo, nsds5ReplConflict:rscwo, modifiersName:rsc
     wo, matchingRules:rscwo, governingStructureRule:rscwo, entryusn:rscwo, nssla
     pd-return-default-opattr:rscwo, parentid:rscwo, pwdUpdateTime:rscwo, support
     edControl:rscwo, passwordAllowChangeTime:rscwo, nsBackendSuffix:rscwo, nsIdl
     eTimeout:rscwo, nameForms:rscwo, ldapSyntaxes:rscwo, numSubordinates:rscwo, 
     namingContexts:rscwo
    

As a result of unit testing our ldap aci's we were able to find many many loop holes in our security, and then we were able to programatically close them all down. Reading the ACI's by hand revealed some issues, but by testing the "expected" aci versus actual behaviour highlighted our edge cases and the complex interactions of LDAP systems.

I will clean up and publish the usl tool set in the future to help other people test their own LDAP secuity controls.
