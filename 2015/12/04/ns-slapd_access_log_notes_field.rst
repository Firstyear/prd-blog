ns-slapd access log notes field
===============================
It would appear we don't have any documentation for the tricky little notes field in ns-slapd. 

Sometimes in a search you'll see:

::
    
    [26/Nov/2015:10:22:00 +1000] conn=5 op=1 SRCH base="" scope=0 notes="U" filter="(cn=foo)" attrs="cn"
    

See the notes="U"? Well, it turns out it's the DS trying to help you out.

First, the two to look out for are notes=U and notes=A. 

notes=A is BAD. You never want to get this one. It means that all candidate attributes in the filter are unindexed, so we need to make a full table scan. This can quickly hit the nsslapd-lookthroughlimit.

To rectify this, look at the search, and identify the attributes. Look them up in cn=schema:

::
    
    ldapsearch -H ldap://localhost -b 'cn=schema' -x '(objectClass=*)' attributeTypes
    

And make sure it has an equality syntax:

::
    
    attributeTypes: ( 2.5.4.3 NAME ( 'cn' 'commonName' )  SUP name EQUALITY caseIg
     noreMatch SUBSTR caseIgnoreSubstringsMatch SYNTAX 1.3.6.1.4.1.1466.115.121.1.
     15 X-ORIGIN 'RFC 4519' X-DEPRECATED 'commonName' )
    

If you don't have an equality syntax, DO NOT ADD AN INDEX. Terrible things will happen!


notes=U means one of two things. It means that a candidate attribute in the filter is unindexed, but there is still an indexed candidate. Or it means that the search has hit the idlistscanlimit.

If you have the query like below, check your nsslapd indexes. cn is probably indexed, but then you need to add the index for sn. Follow the rules as above, and make sure it has an equality syntax.
::

        "(|(cn=foo)(sn=bar))" 


Second, if that's not the issue, and you think you are hitting idlistscanlimit, you can either:

* Adjust it globally
* Adjust it for the single entry

Doing it on the entry, can cause the query to become sometimes more efficient, because you can de-preference certain indexes. There is more to read about here in the <a href="http://www.port389.org/docs/389ds/design/fine-grained-id-list-size.html">id scan limit docs</a>.

Remember to test offline, in a production replica!


40
