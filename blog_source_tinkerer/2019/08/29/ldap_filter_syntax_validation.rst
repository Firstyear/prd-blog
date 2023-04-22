LDAP Filter Syntax Validation
=============================

Today I want to do a deep-dive into a change that will be released in 389 Directory Server 1.4.2.
It's a reasonably complicated change for our server, but it has a simple
user interaction for admins and developers. I want to peel back some of the layers to explain what kind of experience, thought and
team work goes into a change like this.

TL;DR - just keep upgrading your 389 Directory Server instance, and our 'correct by default' policy
will apply, and you'll keep having the best LDAP server we can make :)

LDAP Filters and How They Work
------------------------------

`LDAP filters </blog/html/pages/ldap_guide_part_3_filters.html>`_ are one of the primary methods
of expression in LDAP, and are used in almost every aspect of the system - from finding who you
are when you login, to asserting you are member of a group or have other security attributes.

For the purposes of this discussion we'll look at this filter:

::

    '(|(cn=william)(cn=claire))'

In order to execute these queries quickly (LDAP is designed to handle thousands of operations
per second) we heavily rely on indexing. Indexing is often a topic where people believe it to
be some kind of "magic" but it's reasonably simple: indexes are pre-computed partial result sets.
So why do we need these?

We'll imagine we have two entries (invalid, and truncated for brevity).

::

    dn: cn=william,...
    cn: william

    dn: cn=claire,...
    cn: claire

These entries both have entry-ids - these id's are *per-server* in a replication group and are
integers. You can show them by requesting entryid as an attribute in 389.

::

    dn: cn=william,...
    entryid: 1
    cn: william

    dn: cn=claire,...
    entryid: 2
    cn: claire

Our entries are stored in the main-entry database in */var/lib/dirsrv/slapd-standalone1/db/userRoot*
in the file "id2entry.db4". This is a key-value database where the keys are the entryid, and the value
is the serialised entry itself. Roughly, it's:

::

    [ ID ][ Entry             ]
      1     dn: cn=william,...
            cn: william

      2     dn: cn=claire,...
            cn: claire

Now, if we had NO indexes, to evaluate our filters we have to scan every entry of id2entry to determine
if the filter matches. This algorithm is:

::

    candidate_set = []
    for id in id-min to id-max:
        entry = load_entry_by_id(id)
        if apply_filter(filter, entry):
            candidate_set.append(entry)

For two entries, this may be fast, but when you have 1000, 10.000, or even millions, this is
extremely slow. We call these searches *full table scans* or in 389 DS, *ALLIDS* searches.

To make our searches faster we have indexes. An index is a mapping of a partial query term to an
id list (In 389 we call these IDLs). An IDL is a set of integers. Our index for these examples would
likely be something like:

::

    cn
    =william: [1, ]
    =claire: [2, ]

These indexes are also stored in key-value databases in userRoot - you can see this as cn.db4.

So when we have an indexed term, to evaluate the query, we'll load the indexes, then using mathematical
set operations, we then produce a candidate_id_set, and we can then load the entries that
only match.

For example in psuedo python code:

::

    # Assume query is: (cn=william)

    attr = filter.get_attr_name()
    with open('%s.db' % attr) as index:
        idl = index.get('=william') # from the filter :)

    for id in idl:
        ... # as before.

So we can see now that when we load the idl for cn index, this would give us the set [1, ]. Even
if the database had 100 million entries, as our idl is a single value, we only need to load the
one entry that matches. Neat!

When we have a more complex operation such as AND and OR, we can now manipulate the idl sets. For
example:

::

    (|(uid=claire)(uid=william))
       uid =claire -> idl [2, ]
       uid =william -> idl [1, ]

    candidate_idl_set = union([2, ], [1, ])
    # [1, 2]

This means again, even with millions of entries, we only need to load entry 1 and 2 to uphold the
query provided to us.

So we finally know enough to understand how our example query is executed. PHEW!

Unindexed Attributes
--------------------

However, it's not always so easy. When we have an attribute that isn't indexed, we have to handle
this situation. In these cases, while we operate on the idl set, we may insert an idl with the value
of ALLIDS (which as previously mentioned, is the "set of all entries"). This can have various effects.

If this was an AND query, we can annotate that the filter is *partially* resolved. This means
that if we had:

::

    (&(cn=william)(unindexed=foo))

Because an AND condition, both filter components must be satisfied, we have a partial candidate set
from cn=william of [1, ]. We can load this partial candidate set, and then apply the filter test
as in the full table scan case, but as we only apply it to a single entry this is really fast.

The real problem is OR queries. If we had:

::

    (|(cn=william)(unindexed=foo))

Because OR means that both filter components *could* be satisfied, we have to turn unindexd into
ALLIDS, and the result of the OR as a whole is ALLIDS. So even if we have 30 indexed values in
the OR, a single ALLIDS (unindexed value) will always turn that OR into a full table scan. This is
not good for performance!

Missing Attributes
------------------

So as a weirder case ... what if the attribute doesn't exist in schema at all? For example we
could search for Microsoft AD attributes in 389 Directory Server, or we could submit bogus
filters like "(whargarble=foo)". What happens here?

Well, historically we treated these the same as *unindexed* queries. Which means that any term
that is not in schema, would be treated as ALLIDS. This led to a "quitely known" denial of service
attack again 389 Directory Server where you could emit a large number of queries for attributes
that don't exist, causing the server to attempt many ALLIDS scans. We have some defences like
the allids limit (how many entries you can full table scan before giving up). But it can still cause
entry cache churn and other performance issues.

I was first made aware of this issue in 2014 while working for University of Adelaide where our VMWare
service would query LDAP for MS attributes, causing a large performance issue. We resolved this by
adding the MS attributes to schema and indexing them so that they would create empty indexes - now
we would call this in 389 Directory Server and "idl_alloc(0)" or "empty IDL".

When initially hired by Red Hat in 2015 I knew this issue existed but I didn't know enough about
the server core to really fix it, so it went in the back of my mind ... it was rare to have a customer
raise this issue, but we had the work around and so I was able to advise support services on how
to mitigate this.

In 2019 however, while investigating an issue related to filter optimisation, I was made aware of an
issue with FreeIPA where they were doing certmap queries that requested MS Cert attributes. However
it would cause large performance issues. We now had the issue again, and in a large widely installed
product so it was time to tackle it.

How to handle this?
-------------------

A major issue in this is "never breaking customers". Because we had always supported this behaviour
there is a risk that any solution would cause customer queries to "silently" begin to break if we
issued a fix or change. More accurately, any change to how we execute the filters could cause
results of the filters to change, which would disrupt customers.

Saying this, there is also precedent that 389 Directory Server was handling this incorrectly. From
the RFC for LDAP it was noted:

*Any assertion about the values of such an attribute is only defined if the AttributeType is known by the evaluating mechanism, the purported AttributeValue(s) conforms to the attribute syntax defined for that attribute type, the implied or indicated matching rule is applicable to that attribute type, and (when used) a presented matchValue conforms to the syntax defined for the indicated matching rules. When these conditions are not met, the FilterItem shall evaluate to the logical value UNDEFINED.
An assertion which is defined by these conditions additionally evaluates to UNDEFINED if it relates to an attribute value and the attribute type is not present in an attribute against which the assertion is being tested. An assertion which is defined by these conditions and relates to the presence of an attribute type evaluates to FALSE.*

Translation: If a filter component (IE nonexist=foo) is in a filter but NOT in the schema, the result of the filter's
evaluation is an empty-set aka undefined.

It was also clear that if an engaged and active consumer like FreeIPA is making this mistake, then
it must be overlooked by many others without notice. So there is sometimes value in helping to
raise the standard so that everyone benefits, and highlight mistakes quicker.

The Technical Solution
----------------------

This is the easy part - we add a new configuration option with three states. "on", "off", "warn".
"On" would enable the strictest handling of filters, rejecting them an not continuing if any
attribute requested was not in the schema. "Warn" would provide the rfc compliant behaviour, mapping
to empty-set index, and notifying in the logs that this occured. Finally, "off" would be the previous
"silently allow" behaviour.

This was easily achieved in filter parsing, by checking the attribute of each filter component against
our schema hashmap. We then tag the filter element, and depending on the current setting level reject
or continue.

In the query execution code, we now check the filter tag to understand if the attribute is schema
present or not. If it's flagged as "undefined", then we immediately shortcut to return idl_alloc(0)
instead of returning ALLIDS on the failure to find the relevant index db.

We can show the performance impact of this change:

Before with non-existant attribute

::

    Average rate:    7.40/thr

After with "warn" enabled (map to empty set)

::

     Average rate: 4808.70/thr

This is a huge improvement, and certainly shows the risk of DOS and how effective the solution was!

The Social Solution
-------------------

Of course, this is the hard part - the 389 Directory Server team are all amazingly smart people, from
many countries, and all live around the world. They all care that the server is the best possible, and that
our standards as a team are high. That means when introducing a change that has a risk of affecting
query result sets like this, they pay attention, and ask many difficult questions about how the
feature will be implemented.

The first important justification - is a change like this worth while? We can see from the performance
results that the risk of DOS is reasonable, so the answer there becomes Yes from a security view. But
it's also important to consider the cost on consumers - is this change going to benefit FreeIPA for
example? As I am biased being the author I want to say "yes" - by notifying or rejecting invalid
filters earlier, we can help FreeIPA developers improve their code quality, without expecting them
to know LDAP inside and out.

The next major question is performance - before the feature was developed there is clearly a risk
of DOS, but when we implement this we are performing additional locking on the schema. Is that
a risk to our standalone performance or normal operating conditions. This had to also be discussed
and assessed.

A really important point that was raised by Thierry is how we communicated these errors too. Previously
we would use the "notes=" field of the access log. It looks like this:

::

    conn=1 op=4 RESULT err=0 tag=101 nentries=13 etime=0.0003795424 notes=U

The challenge with the notes= field, is that it's easy to overlook, and unless you are familar, hard
to see what this is indicating. In this case, notes=U means partially unindexed query (one filter
component but not all returned ALLIDS).

We can't change the notes field due to the risk of breaking our own scripts like logconv.pl, support
tools developed by RH or SUSE, or even integrations to platforms like splunk. But clearly we need
a way to detail what is happening with your filter. So Thierry suggested an extension to have details
about the provided notes. Now we get:

::

    conn=1 op=4 RESULT err=0 tag=101 nentries=13 etime=0.0003795424 notes=U details="Partially Unindexed Filter"
    conn=1 op=8 RESULT err=0 tag=101 nentries=0 etime=0.0001886208 notes=F details="Filter Element Missing From Schema"

So we have extended our log message, but without breaking existing integrations.

The final question is what our defaults should be. It's one thing to have this feature, but what
should we ship with? Do we strictly reject filters? Warn? Or disable, and expect people to turn
this on.

This became a long discussion with Ludwig, Thierry and I - we discussed the risk of DOS in the first
place, what the impact of the levels could be, how it could break legacy applications or sites using
deprecated features or with weird data imports. Many different aspects were considered. We decided
to default to "warn" (non-existant becomes empty-set), and we settled on communication with support
to advise them of the upcoming change, but also we considered that our "back out" plan is to change
the default and ship a patch if there is a large volume of negative feedback.

Conclusion
----------

As of today, the PR is merged, and the code on it's way to the next release. It's a long process
but the process exists to ensure we do what's best for our users, while we try to balance many different
aspects. We have a great team of people, with decades of experience from many backgrounds which means
that these discussions can be long and detailed, but in the end, we hope to give what is the best
product possible to our community.

It's also valuable to share how much thought and effort goes into projects - in your life you may
only interact with 1% of our work through our configuration and system, but we have an iceberg of
decisions and design process that affects you every day, where we have to be responsible and considerate
in our actions.

I hope you enjoyed this exploration of this change!

References
----------

`PR#50379 <https://pagure.io/389-ds-base/pull-request/50379>`_

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
