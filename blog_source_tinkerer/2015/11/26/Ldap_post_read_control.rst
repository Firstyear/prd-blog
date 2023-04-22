Ldap post read control
======================
This was a bit of a pain to use in python.

If we want to modify and entry and immediately check it's entryUSN so that we can track the update status of objects in ldap, we can use the post read control so that after the add/mod/modrdn is complete, we can immediately check the result of usn atomically. This lets us compare entryusn to know if the object has changed or not. 

To use in python:

::
    
    >>> conn.modify_ext( 'cn=Directory Administrators,dc=example,dc=com',
          ldap.modlist.modifyModlist({}, {'description' : ['oeusoeutlnsoe'] } ),
         [PostReadControl(criticality=True,attrList=['nsUniqueId'])]  
         ) 
    6
    >>> _,_,_,resp_ctrls = conn.result3(6)
    >>> resp_ctrls
    [<ldap.controls.readentry.PostReadControl instance at 0x2389cf8>]
    >>> resp_ctrls[0].dn
    'cn=Directory Administrators,dc=example,dc=com'
    >>> resp_ctrls[0].entry
    {'nsUniqueId': ['826cc526-8caf11e5-93ba8a51-c5ee9f85']}
    
    

See also, `PostRead <http://www.python-ldap.org/doc/html/ldap-controls.html>`_ and `python-ldap <http://www.python-ldap.org/doc/html/ldap.html>`_.
