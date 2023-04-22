+++
title = "Understanding AD Access Control Entries"
date = 2018-04-20
slug = "2018-04-20-understanding_ad_access_control_entries"
# This is relative to the root!
aliases = [ "2018/04/20/understanding_ad_access_control_entries.html" ]
+++
# Understanding AD Access Control Entries

A few days ago I set out to work on making samba 4 my default LDAP
server. In the process I was forced to learn about Active Directory
Access controls. I found that while there was significant documentation
around the syntax of these structures, very little existed explaining
how to use them effectively.

## What\'s in an ACE?

If you look at the the ACL of an entry in AD you\'ll see something like:

    O:DAG:DAD:AI
    (A;CI;RPLCLORC;;;AN)
    (A;;RPWPCRCCDCLCLORCWOWDSDDTSW;;;SY)
    (A;;RPWPCRCCDCLCLORCWOWDSW;;;DA)
    (OA;;CCDC;bf967aba-0de6-11d0-a285-00aa003049e2;;AO)
    (OA;;CCDC;bf967a9c-0de6-11d0-a285-00aa003049e2;;AO)
    (OA;;CCDC;bf967aa8-0de6-11d0-a285-00aa003049e2;;PO)
    (A;;RPLCLORC;;;AU)
    (OA;;CCDC;4828cc14-1437-45bc-9b07-ad6f015e5f28;;AO)
    (OA;CIIOID;RP;4c164200-20c0-11d0-a768-00aa006e0529;4828cc14-1437-45bc-9b07-ad6f015e5f28;RU)
    (OA;CIIOID;RP;4c164200-20c0-11d0-a768-00aa006e0529;bf967aba-0de6-11d0-a285-00aa003049e2;RU)
    (OA;CIIOID;RP;5f202010-79a5-11d0-9020-00c04fc2d4cf;4828cc14-1437-45bc-9b07-ad6f015e5f28;RU)
    (OA;CIIOID;RP;5f202010-79a5-11d0-9020-00c04fc2d4cf;bf967aba-0de6-11d0-a285-00aa003049e2;RU)
    (OA;CIIOID;RP;bc0ac240-79a9-11d0-9020-00c04fc2d4cf;4828cc14-1437-45bc-9b07-ad6f015e5f28;RU)
    (OA;CIIOID;RP;bc0ac240-79a9-11d0-9020-00c04fc2d4cf;bf967aba-0de6-11d0-a285-00aa003049e2;RU)
    (OA;CIIOID;RP;59ba2f42-79a2-11d0-9020-00c04fc2d3cf;4828cc14-1437-45bc-9b07-ad6f015e5f28;RU)
    (OA;CIIOID;RP;59ba2f42-79a2-11d0-9020-00c04fc2d3cf;bf967aba-0de6-11d0-a285-00aa003049e2;RU)
    (OA;CIIOID;RP;037088f8-0ae1-11d2-b422-00a0c968f939;4828cc14-1437-45bc-9b07-ad6f015e5f28;RU)
    (OA;CIIOID;RP;037088f8-0ae1-11d2-b422-00a0c968f939;bf967aba-0de6-11d0-a285-00aa003049e2;RU)
    (OA;CIIOID;RP;b7c69e6d-2cc7-11d2-854e-00a0c983f608;bf967a86-0de6-11d0-a285-00aa003049e2;ED)
    (OA;CIIOID;RP;b7c69e6d-2cc7-11d2-854e-00a0c983f608;bf967a9c-0de6-11d0-a285-00aa003049e2;ED)
    (OA;CIIOID;RP;b7c69e6d-2cc7-11d2-854e-00a0c983f608;bf967aba-0de6-11d0-a285-00aa003049e2;ED)
    (OA;CIIOID;RPLCLORC;;4828cc14-1437-45bc-9b07-ad6f015e5f28;RU)
    (OA;CIIOID;RPLCLORC;;bf967a9c-0de6-11d0-a285-00aa003049e2;RU)
    (OA;CIIOID;RPLCLORC;;bf967aba-0de6-11d0-a285-00aa003049e2;RU)
    (OA;CIID;RPWPCR;91e647de-d96f-4b70-9557-d63ff4f3ccd8;;PS)
    (A;CIID;RPWPCRCCDCLCLORCWOWDSDDTSW;;;EA)
    (A;CIID;LC;;;RU)
    (A;CIID;RPWPCRCCLCLORCWOWDSDSW;;;BA)
    S:AI
    (OU;CIIOIDSA;WP;f30e3bbe-9ff0-11d1-b603-0000f80367c1;bf967aa5-0de6-11d0-a285-00aa003049e2;WD)
    (OU;CIIOIDSA;WP;f30e3bbf-9ff0-11d1-b603-0000f80367c1;bf967aa5-0de6-11d0-a285-00aa003049e2;WD)

This seems very confusing and complex (and someone should write a tool
to explain these \... maybe me). But once you can see the structure it
starts to make sense.

Most of the access controls you are viewing here are DACLs or
Discrestionary Access Control Lists. These make up the majority of the
output after \'O:DAG:DAD:AI\'. TODO: What does \'O:DAG:DAD:AI\' mean
completely?

After that there are many ACEs defined in SDDL or ???. The structure is
as follows:

    (type;flags;rights;object_guid;inherit_object_guid;sid(;attribute))

Each of these fields can take varies types. These interact to form the
access control rules that allow or deny access. Thankfully, you don\'t
need to adjust many fields to make useful ACE entries.

MS maintains a document of these [field values
here.](https://msdn.microsoft.com/en-us/library/aa374928(d=printer,v=vs.85).aspx)

They also maintain a list of wellknown [SID values
here](https://msdn.microsoft.com/en-us/library/aa379602(d=printer,v=vs.85).aspx)

I want to cover some common values you may see though:

## type

Most of the types you\'ll see are \"A\" and \"OA\". These mean the ACE
allows an access by the SID.

## flags

These change the behaviour of the ACE. Common values you may want to set
are CI and OI. These determine that the ACE should be inherited to child
objects. As far as the MS docs say, these behave the same way.

If you see ID in this field it means the ACE has been inherited from a
parent object. In this case the inherit_object_guid field will be set to
the guid of the parent that set the ACE. This is great, as it allows you
to backtrace the origin of access controls!

## rights

This is the important part of the ACE - it determines what access the
SID has over this object. The MS docs are very comprehensive of what
this does, but common values are:

-   RP: read property
-   WP: write property
-   CR: control rights
-   CC: child create (create new objects)
-   DC: delete child
-   LC: list child objects
-   LO: list objects
-   RC: read control
-   WO: write owner (change the owner of an object)
-   WD: write dac (allow writing ACE)
-   SW: self write
-   SD: standard delete
-   DT: delete tree

I\'m not 100% sure of all the subtle behaviours of these, because they
are *not* documented that well. If someone can help explain these to me,
it would be great.

## sid

We will skip some fields and go straight to SID. This is the SID of the
object that is allowed the rights from the rights field. This field can
take a GUID of the object, or it can take a \"well known\" value of the
SID. For example \'AN\' means \"anonymous users\", or \'AU\' meaning
authenticated users.

## conclusion

I won\'t claim to be an AD ACE expert, but I did find the docs hard to
interpret at first. Having a breakdown and explanation of the behaviour
of the fields can help others, and I really want to hear from people who
know more about this topic on me so that I can expand this resource to
help others really understand how AD ACE\'s work.

