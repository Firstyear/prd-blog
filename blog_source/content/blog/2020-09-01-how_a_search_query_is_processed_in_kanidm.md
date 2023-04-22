+++
title = "How a Search Query is Processed in Kanidm"
date = 2020-09-01
slug = "2020-09-01-how_a_search_query_is_processed_in_kanidm"
# This is relative to the root!
aliases = [ "2020/09/01/how_a_search_query_is_processed_in_kanidm.html" ]
+++
# How a Search Query is Processed in Kanidm

Databases from postgres to sqlite, mongodb, and even LDAP all need to
take a query and turn that into a meaningful result set. This process
can often seem like magic, especially when you consider an LDAP server
is able to process thousands of parallel queries, with a database
spanning millions of entries and still can return results in less than a
millisecond. Even more impressive is that every one of these databases
can be expected to return the correct result, every time. This level of
performance, correctness and precision is an astounding feat of
engineering, but is rooted in a simple set of design patterns.

## Disclaimer

This will be a very long post. You may want to set aside some time for
it :)

This post will discuss how [Kanidm](https://github.com/kanidm/kanidm)
processes queries. This means that some implementation specifics are
specific to the Kanidm project. However conceptually this is very close
to the operation of LDAP servers (389-ds, samba 4, openldap) and
MongoDB, and certainly there are still many overlaps and similarities to
SQLite and Postgres. At the least, I hope it gives you some foundation
to research the specifics behaviours you chosen database.

This post does NOT discuss how creation or modification paths operate.
That is likely worthy of a post of it\'s own. Saying this, search relies
heavily on correct function of the write paths, and they are always
intertwined.

The referenced code and links relate to commit
[dbfe87e](https://github.com/kanidm/kanidm/tree/dbfe87e675beac7fd931a445fd80cf439c2c6e61)
from 2020-08-24. The project may have changed since this point, so it\'s
best if you can look at the latest commits in the tree if possible.

## Introduction

Kanidm uses a structured document store model, similar to LDAP or
MongoDB. You can consider entries to be like a JSON document. For
example,

    {
        "class": [
            "object",
            "memberof",
            "account",
            "posixaccount"
        ],
        "displayname": [
            "William"
        ],
        "gidnumber": [
            "1000"
        ],
        "loginshell": [
            "/bin/zsh"
        ],
        "name": [
            "william"
        ],
        "uuid": [
            "5e01622e-740a-4bea-b694-e952653252b4"
        ],
        "memberof": [
            "admins",
            "users",
            "radius"
        ],
        "ssh_publickey": [
            {
                "tag": "laptop",
                "key": "...."
            }
        ]
    }

Something of note here is that an entry has many attributes, and those
attributes can consist of one or more values. values themself can be
structured such as the ssh_publickey value which has a tag and the
public key, or the uuid which enforces uuid syntax.

## Filters / Queries

During a search we want to find entries that match specific attribute
value assertions or attribute assertions. We also want to be able to use
logic to provide complex conditions or logic in how we perform the
search. We could consider the search in terms of SQL such as:

    select from entries where name = william and class = account;

Or in LDAP syntax

    (&(objectClass=account)(name=william))

In Kanidm JSON (which admitedly, is a bit rough, we don\'t expect people
to use this much!)

    { "and": [{"eq": ["class", "account"]}, {"eq": ["name": "william"]} ]}

Regardless of how we structure these, they are the same query. We want
to find entries where the property of class=account and name=william
hold true. There are many other types of logic we could apply
(especially true for sql), but in Kanidm we support the following
[proto(col)
filters](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidm_proto/src/v1.rs#L305)

    pub enum Filter {
        Eq(String, String),
        Sub(String, String),
        Pres(String),
        Or(Vec<Filter>),
        And(Vec<Filter>),
        AndNot(Box<Filter>),
        SelfUUID,
    }

These represent:

-   Eq(uality) - an attribute of name, has at least one value matching
    the term
-   Sub(string) - an attribute of name, has at least one value matching
    the substring term
-   Pres(ence) - an attribute of name, regardless of value exists on the
    entry
-   Or - One or more of the nested conditions must evaluate to true
-   And - All nested conditions must be true, or the and returns false
-   AndNot - Within an And query, the inner term must not be true
    relative to the related and term
-   SelfUUID - A dynamic Eq(uality) where the authenticated user\'s UUID
    is added. Essentially, this substitutes to \"eq (uuid, selfuuid)\"

Comparing to the previous example entry, we can see that [{ \"and\":
\[{\"eq\": \[\"class\", \"account\"\]}, {\"eq\": \[\"name\":
\"william\"\]} \]}]{.title-ref} would be true, where [{ \"eq\":
\[\"name\": \"claire\"\]}]{.title-ref} would be false as no matching
name attribute-value exists on the entry.

## Recieving the Query

There are multiple ways that a query could find it\'s way into Kanidm.
It may be submitted from the raw search api, it could be generated from
a REST endpoint request, it may be translated via the LDAP
compatability. The most important part is that it is then recieved by a
worker thread in the query server. For this discussion we\'ll assume we
recieved a raw search via the front end.

[handle_search](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/actors/v1_read.rs#L245)
is the entry point of a worker thread to process a search operation. The
first thing we do is begin a read transaction over the various elements
of the database we need.

    fn handle(&mut self, msg: SearchMessage, _: &mut Self::Context) -> Self::Result {
    let mut audit = AuditScope::new("search", msg.eventid, self.log_level);
    let res = lperf_op_segment!(&mut audit, "actors::v1_read::handle<SearchMessage>", || {
        // Begin a read
        let qs_read = self.qs.read();

The call to
[qs.read](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/server.rs#L732)
takes three transactions - the backend, the schema cache and the access
control cache.

    pub fn read(&self) -> QueryServerReadTransaction {
        QueryServerReadTransaction {
            be_txn: self.be.read(),
            schema: self.schema.read(),
            accesscontrols: self.accesscontrols.read(),
        }
    }

The [backend
read](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/mod.rs#L1348)
takes two transactions internally - the database layers, and the
indexing metadata cache.

    pub fn read(&self) -> BackendReadTransaction {
        BackendReadTransaction {
            idlayer: UnsafeCell::new(self.idlayer.read()),
            idxmeta: self.idxmeta.read(),
        }
    }

Once complete, we can now transform the submitted request, into an
internal event. By structuring all requests as event, we standarise all
operations to a subset of operations, and we ensure that that all
resources required are available in the event. The [search
event](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/event.rs#L255)
as processed stores an event origin aka the identiy of the event origin.
The search query is stored in the [filter]{.title-ref} attribute, and
the original query is stored in the [filter_orig]{.title-ref}. There is
a reason for this duplication.

    pub fn from_message(
        audit: &mut AuditScope,
        msg: SearchMessage,
        qs: &QueryServerReadTransaction,
    ) -> Result<Self, OperationError> {
        let event = Event::from_ro_uat(audit, qs, msg.uat.as_ref())?;
        let f = Filter::from_ro(audit, &event, &msg.req.filter, qs)?;
        // We do need to do this twice to account for the ignore_hidden
        // changes.
        let filter = f
            .clone()
            .into_ignore_hidden()
            .validate(qs.get_schema())
            .map_err(OperationError::SchemaViolation)?;
        let filter_orig = f
            .validate(qs.get_schema())
            .map_err(OperationError::SchemaViolation)?;
        Ok(SearchEvent {
            event,
            filter,
            filter_orig,
            // We can't get this from the SearchMessage because it's annoying with the
            // current macro design.
            attrs: None,
        })
    }

As [filter]{.title-ref} is processed it is transformed by the server to
change it\'s semantics. This is due to the call to
[into_ignore_hidden](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/filter.rs#L504).
This function adds a wrapping layer to the outside of the query that
hides certain classes of entries from view unless explicitly requested.
In the case of kanidm this transformation is to add:

    { "and": [
        { "andnot" : { "or" [
            {"eq": ["class", "tombstone"]},
            {"eq": ["class", "recycled"]}
        }]},
        <original query>
    ]}

This prevents the display of deleted (recycle bin) entries, and the
display of tombstones - marker entries representing that an entry with
this UUID once existed in this location. These tombstones are part of
the (future) eventually consistent replication machinery to allow
deletes to be processed.

This is why [filter_orig]{.title-ref} is stored. We require a copy of
the \"query as intended by the caller\" for the purpose of checking
access controls later. A user may not have access to the attribute
\"class\" which would mean that the addition of the
[into_ignore_hidden]{.title-ref} could cause them to not have any
results at all. We should not penalise the user for something they
didn\'t ask for!

After the query is transformed, we now
[validate](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/event.rs#L277)
it\'s content. This validation ensures that queries contain only
attributes that truly exist in schema, and that their representation in
the query is sound. This prevents a number of security issues related to
denial of service or possible information disclosures. The query has
every attribute-value
[compared](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/filter.rs#L545)
to the schema to ensure that they exist and are correct syntax types.

## Start Processing the Query

Now that the search event has been created and we know that is is valid
within a set of rules, we can submit it to the
[search_ext(ernal)](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/actors/v1_read.rs#L265)
interface of the query server. Because everything we need is contained
in the search event we are able to process the query from this point.
Search external is a wrapper to the internal search, where
[search_ext](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/server.rs#L90)
is able to wrap and apply access controls to the results from the
operation.

    fn search_ext(
        &self,
        au: &mut AuditScope,
        se: &SearchEvent,
    ) -> Result<Vec<Entry<EntryReduced, EntryCommitted>>, OperationError> {
        lperf_segment!(au, "server::search_ext", || {
            /*
             * This just wraps search, but it's for the external interface
             * so as a result it also reduces the entry set's attributes at
             * the end.
             */
            let entries = self.search(au, se)?;

            let access = self.get_accesscontrols();
            access
                .search_filter_entry_attributes(au, se, entries)
                .map_err(|e| {
                    // Log and fail if something went wrong.
                    ladmin_error!(au, "Failed to filter entry attributes {:?}", e);
                    e
                })
            // This now returns the reduced vec.
        })
    }

The [internal
search](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/server.rs#L90)
function is now called, and we begin to prepare for the backend to
handle the query.

We have a final transformation we must apply to the query that we intend
to pass to the backend. We must attach metadata to the query elements so
that we can perform informed optimisation of the query.

    let be_txn = self.get_be_txn();
    let idxmeta = be_txn.get_idxmeta_ref();
    // Now resolve all references and indexes.
    let vfr = lperf_trace_segment!(au, "server::search<filter_resolve>", || {
        se.filter.resolve(&se.event, Some(idxmeta))
    })

This is done by retreiving indexing metadata from the backend, which
defines which attributes and types of indexes exist. This indexing
metadata is passed to the filter to [be
resolved](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/filter.rs#L504).
In the case of tests we may not pass index metadata, which is why filter
resolve accounts for the possibility of idxmeta being None. The filter
elements are transformed, for example we change [eq to have a
boolean](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/filter.rs#L973)
associated if the attribute is indexed. In our example this would change
the query:

    { "and": [
        { "andnot" : { "or" [
            {"eq": ["class", "tombstone"]},
            {"eq": ["class", "recycled"]}
        }]},
        { "and": [
            {"eq": ["class", "account"]},
            {"eq": ["name": "william"]}
        ]}
    ]}

To

    { "and": [
        { "andnot" : { "or" [
            {"eq": ["class", "tombstone", true]},
            {"eq": ["class", "recycled", true]}
        }]},
        { "and": [
            {"eq": ["class", "account", true]},
            {"eq": ["name": "william", true]}
        ]}
    ]}

With this metadata associated to the query, we can now submit it to the
backend for processing.

## Backend Processing

We are now in a position where the backend can begin to do work to
actually process the query. The first step of the [backend
search](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/mod.rs#L474)
function is to perform the final optimisation of the filter.

    fn search(
        &self,
        au: &mut AuditScope,
        erl: &EventLimits,
        filt: &Filter<FilterValidResolved>,
    ) -> Result<Vec<Entry<EntrySealed, EntryCommitted>>, OperationError> {
        lperf_trace_segment!(au, "be::search", || {
            // Do a final optimise of the filter
            let filt =
                lperf_trace_segment!(au, "be::search<filt::optimise>", || { filt.optimise() });

Query optimisation is critical to make searches fast. In Kanidm it
relies on a specific behaviour of the indexing application process. I
will highlight that step shortly.

For now, the way query optimisation works is by sorting and folding
terms in the query. This is because there are a number of logical
equivalences, but also that due to the associated metadata and
experience we know that some terms may be better in different areas.
Optimisation relies on a [sorting
function](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/filter.rs#L1088)
that will rearrange terms as needed.

An example is that a nested [and]{.title-ref} term, can be folded to the
parent because logically an [and]{.title-ref} inside and
[and]{.title-ref} is the same. Similar for [or]{.title-ref} inside
[or]{.title-ref}.

Within the [and]{.title-ref} term, we can then rearrange the terms,
because the order of the terms does not matter in an [and]{.title-ref}
or [or]{.title-ref}, only that the other logical elements hold true. We
sort indexed equality terms first because we know that they are always
going to resolve \"faster\" than the nested [andnot]{.title-ref} term.

    { "and": [
        {"eq": ["class", "account", true]},
        {"eq": ["name": "william", true]},
        { "andnot" : { "or" [
            {"eq": ["class", "tombstone", true]},
            {"eq": ["class", "recycled", true]}
        }]}
    ]}

In the future, an improvement here is to put name before class, which
will happen as part of the issue
[#238](https://github.com/kanidm/kanidm/issues/238) which allows us to
work out which indexes are going to yield the best information content.
So we can sort them first in the query.

Finally, we are at the point where we can begin to actually load some
data! 🎉

The filter is submitted to
[filter2idl](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/mod.rs#L109).
To understand this function, we need to understand how indexes and
entries are stored.

    let (idl, fplan) = lperf_trace_segment!(au, "be::search -> filter2idl", || {
        self.filter2idl(au, filt.to_inner(), FILTER_SEARCH_TEST_THRESHOLD)
    })?;

All databases at the lowest levels are built on collections of key-value
stores. That keyvalue store may be a in memory tree or hashmap, or an on
disk tree. Some common stores are BDB, LMDB, SLED. In Kanidm we use
SQLite as a key-value store, through tables that only contain two
columns. The intent is to swap to SLED in the future once it gains
transactions over a collection of trees, and that trees can be
created/removed in transactions.

The primary storage of all entries is in the table
[id2entry](https://github.com/kanidm/kanidm/blob/master/kanidmd/src/lib/be/idl_sqlite.rs#L1134)
which has an id column (the key) and stores serialised entries in the
data column.

Indexes are stored in a collection of their own tables, named in the
scheme \"idx\_\<type\>\_\<attr\>\". For example, \"idx_eq_name\" or
\"idx_pres_class\". These are stored as two columns, where the \"key\"
column is a precomputed result of a value in the entry, and the
\"value\" is a set of integer ID\'s related to the entries that contain
the relevant match.

As a bit more of a graphic example, you can imagine these as:

    id2entry
    | id | data                                    |
    | 1  | { "name": "william", ... }
    | 2  | { "name": "claire", ... }

    idx_eq_name
    | key     |
    | william | [1, ]
    | claire  | [2, ]

    idm_eq_class
    | account | [1, 2, ... ]

As these are key-value stores, they are able to be cached through an
in-memory key value store to speed up the process. Initially, we\'ll
assume these are not cache.

## filter2idl

Back to [filter2idl]{.title-ref}. The query begins by processing the
outer [and]{.title-ref} term. As the [and]{.title-ref} progresses inner
elements are [iterated
over](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/mod.rs#L229)
and then recursively sent to [filter2idl]{.title-ref}.

    FilterResolved::And(l) => {
        // First, setup the two filter lists. We always apply AndNot after positive
        // and terms.
        let (f_andnot, f_rem): (Vec<_>, Vec<_>) = l.iter().partition(|f| f.is_andnot());

        // We make this an iter, so everything comes off in order. if we used pop it means we
        // pull from the tail, which is the WORST item to start with!
        let mut f_rem_iter = f_rem.iter();

        // Setup the initial result.
        let (mut cand_idl, fp) = match f_rem_iter.next() {
            Some(f) => self.filter2idl(au, f, thres)?,
            None => {
                lfilter_error!(au, "WARNING: And filter was empty, or contains only AndNot, can not evaluate.");
                return Ok((IDL::Indexed(IDLBitRange::new()), FilterPlan::Invalid));
            }
        };
        ...

The first term we encounter is [{\"eq\": \[\"class\", \"account\",
true\]}]{.title-ref}. At this point [filter2idl]{.title-ref} is able to
[request the id
list](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/mod.rs#L123)
from the lower levels.

    FilterResolved::Eq(attr, value, idx) => {
        if *idx {
            // Get the idx_key
            let idx_key = value.get_idx_eq_key();
            // Get the idl for this
            match self
                .get_idlayer()
                .get_idl(au, attr, &IndexType::EQUALITY, &idx_key)?
            {
                Some(idl) => (
                    IDL::Indexed(idl),
                    FilterPlan::EqIndexed(attr.to_string(), idx_key),
                ),
                None => (IDL::ALLIDS, FilterPlan::EqCorrupt(attr.to_string())),
            }
        } else {
            // Schema believes this is not indexed
            (IDL::ALLIDS, FilterPlan::EqUnindexed(attr.to_string()))
        }
    }

The first level that is able to serve the request for the key to be
resolved is the [ARCache
layer](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/idl_arc_sqlite.rs#L178).
This tries to lookup the combination of (\"class\", \"account\", eq) in
the cache. If found it is returned to the caller. If not, it is
requested from the [sqlite
layer](https://github.com/kanidm/kanidm/blob/master/kanidmd/src/lib/be/idl_sqlite.rs#L220).

    let cache_key = IdlCacheKey {
        a: $attr.to_string(),
        i: $itype.clone(),
        k: $idx_key.to_string(),
    };
    let cache_r = $self.idl_cache.get(&cache_key);
    // If hit, continue.
    if let Some(ref data) = cache_r {
        ltrace!(
            $audit,
            "Got cached idl for index {:?} {:?} -> {}",
            $itype,
            $attr,
            data
        );
        return Ok(Some(data.as_ref().clone()));
    }
    // If miss, get from db *and* insert to the cache.
    let db_r = $self.db.get_idl($audit, $attr, $itype, $idx_key)?;
    if let Some(ref idl) = db_r {
        $self.idl_cache.insert(cache_key, Box::new(idl.clone()))
    }

This sqlite layer performs the select from the
\"idx\_\<type\>\_\<attr\>\" table, and then deserialises the stored id
list (IDL).

    let mut stmt = self.get_conn().prepare(query.as_str()).map_err(|e| {
        ladmin_error!(audit, "SQLite Error {:?}", e);
        OperationError::SQLiteError
    })?;
    let idl_raw: Option<Vec<u8>> = stmt
        .query_row_named(&[(":idx_key", &idx_key)], |row| row.get(0))
        // We don't mind if it doesn't exist
        .optional()
        .map_err(|e| {
            ladmin_error!(audit, "SQLite Error {:?}", e);
            OperationError::SQLiteError
        })?;

    let idl = match idl_raw {
        Some(d) => serde_cbor::from_slice(d.as_slice())
            .map_err(|_| OperationError::SerdeCborError)?,
        // We don't have this value, it must be empty (or we
        // have a corrupted index .....
        None => IDLBitRange::new(),
    };

The IDL is returned and cached, then returned to the
[filter2idl]{.title-ref} caller. At this point the IDL is the \"partial
candidate set\". It contains the ID numbers of entries that we know
partially match this query at this point. Since the first term is
[{\"eq\": \[\"class\", \"account\", true\]}]{.title-ref} the current
candidate set is [\[1, 2, \...\]]{.title-ref}.

The
[and](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/mod.rs#L284)
path in [filter2idl]{.title-ref} continues, and the next term
encountered is [{\"eq\": \[\"name\": \"william\", true\]}]{.title-ref}.
This resolves into another IDL. The two IDL\'s are merged through an
[and]{.title-ref} operation leaving only the ID numbers that were
present in both.

    (IDL::Indexed(ia), IDL::Indexed(ib)) => {
        let r = ia & ib;
        ...

For this example this means in our example that the state of r(esult
set) is the below;

    res = ia & ib;
    res = [1, 2, ....] & [1, ];
    res == [1, ]

We know that only the entry with [ID == 1]{.title-ref} matches both
[name = william]{.title-ref} and [class = account]{.title-ref}.

We now perform a check called the \"filter threshold check\". If the
number of ID\'s in the IDL is less than a certain number, we can
*shortcut* and return early even though we are not finished processing.

    if r.len() < thres && f_rem_count > 0 {
        // When below thres, we have to return partials to trigger the entry_no_match_filter check.
        let setplan = FilterPlan::AndPartialThreshold(plan);
        return Ok((IDL::PartialThreshold(r), setplan));
    } else if r.is_empty() {
        // Regardless of the input state, if it's empty, this can never
        // be satisfied, so return we are indexed and complete.
        let setplan = FilterPlan::AndEmptyCand(plan);
        return Ok((IDL::Indexed(IDLBitRange::new()), setplan));
    } else {
        IDL::Indexed(r)
    }

This is because the IDL is now small, and continuing to load more
indexes may cost more time and resources. The IDL can only ever shrink
or stay the same from this point, never expand, so we know it must stay
small.

However, you may correctly have deduced that there are still two terms
we must check. That is the terms contained within the
[andnot]{.title-ref} of the query. I promise you, we will check them :)

So at this point we now step out of [filter2idl]{.title-ref} and begin
the process of post-processing the results we have.

## Resolving the Partial Set

We check the way that the [IDL is
tagged](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/mod.rs#L498)
so that we understand what post processing is required, and check some
security controls. If the search was unindexed aka [ALLIDS]{.title-ref},
and if the account is not allowed to access fully unindexed searches,
then we return a failure at this point. We also now check if the query
was [Partial(ly)]{.title-ref} unindexed, and if it is, we assert limits
over the number of entries we may load and test.

    match &idl {
        IDL::ALLIDS => {
            if !erl.unindexed_allow {
                ladmin_error!(au, "filter (search) is fully unindexed, and not allowed by resource limits");
                return Err(OperationError::ResourceLimit);
            }
        }
        IDL::Partial(idl_br) => {
            if idl_br.len() > erl.search_max_filter_test {
                ladmin_error!(au, "filter (search) is partial indexed and greater than search_max_filter_test allowed by resource limits");
                return Err(OperationError::ResourceLimit);
            }
        }
        IDL::PartialThreshold(_) => {
            // Since we opted for this, this is not the fault
            // of the user and we should not penalise them by limiting on partial.
        }
        IDL::Indexed(idl_br) => {
            // We know this is resolved here, so we can attempt the limit
            // check. This has to fold the whole index, but you know, class=pres is
            // indexed ...
            if idl_br.len() > erl.search_max_results {
                ladmin_error!(au, "filter (search) is indexed and greater than search_max_results allowed by resource limits");
                return Err(OperationError::ResourceLimit);
            }
        }
    };

We then load the related entries from the IDL we have. Initially, this
is called through the entry cache of the ARCache.

    let entries = self.get_idlayer().get_identry(au, &idl).map_err(|e| {
        ladmin_error!(au, "get_identry failed {:?}", e);
        e
    })?;

As many entries as possible are [loaded from the
ARCache](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/be/idl_arc_sqlite.rs#L93).
The remaining ID\'s that were missed are stored in a secondary IDL set.
The missed entry set is then submitted to [the sqlite
layer](https://github.com/kanidm/kanidm/blob/master/kanidmd/src/lib/be/idl_sqlite.rs#L99)
where the entries are loaded and deserialised. An important part of the
ARCache is to keep fully inflated entries in memory, to speed up the
process of retrieving these. Real world use shows this can have orders
of magnitude of impact on performance by just avoiding this
deserialisation step, but also that we avoid IO to disk.

The entry set is now able to be checked. If the IDL was
[Indexed]{.title-ref} no extra work is required, and we can just return
the values. But in all other cases we must apply the filter test. The
filter test is where the terms of the filter are checked against each
entry to determine if they match and are part of the set.

This is where the partial threshold is important - that the act of
processing the remaining indexes may be more expensive than applying the
filter assertions to the subset of entries in memory. It\'s also why
filter optimisation matters. If a query can be below the threshold
sooner, than we can apply the filter test earlier and we reduce the
number of indexes we must load and keep cached. This helps performance
and cache behaviour.

The [filter
test](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/entry.rs#L1663)
applies the terms of the filter to the entry, using the same rules as
the indexing process to ensure consistent results. This gives us a
true/false result, which lets us know if the entry really does match and
should become part of the final candidate set.

    fn search(...) {
        ...
        IDL::Partial(_) => lperf_segment!(au, "be::search<entry::ftest::partial>", || {
            entries
                .into_iter()
                .filter(|e| e.entry_match_no_index(&filt))
                .collect()
        }),
        ...
    }

    fn entry_match_no_index_inner(&self, filter: &FilterResolved) -> bool {
        match filter {
            FilterResolved::Eq(attr, value, _) => self.attribute_equality(attr.as_str(), value),
            FilterResolved::Sub(attr, subvalue, _) => {
                self.attribute_substring(attr.as_str(), subvalue)
            }
            ...
        }
    }

It is now at this point that we finally have the fully resolved set of
entries, in memory as a result set from the backend. These are returned
to the query server\'s [search]{.title-ref} function.

## Access Controls

Now the process of
[applying](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/server.rs#L168)
access controls begins. There are two layers of access controls as
applied in kanidm. The first is *which entries are you allowed to see*.
The second is *within an entry, what attributes may you see*. There is a
reason for this seperation. The seperation exists so that when an
internal search is performed on behalf of the user, we retrieve the set
of entries you can see, but the server internally then performs the
operation on your behalf and itself has access to see all attributes. If
you wish to see this in action, it\'s a critical part of how
[modify](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/server.rs#L1290)
and
[delete](https://github.com/kanidm/kanidm/blob/dbfe87e675beac7fd931a445fd80cf439c2c6e61/kanidmd/src/lib/server.rs#L988)
both function, where you can only change or delete within your visible
entry scope.

The first stage is
[search_filter_entries](https://github.com/kanidm/kanidm/blob/master/kanidmd/src/lib/access.rs#L376).
This is the function that checks what entries you *may* see. This checks
that you have the rights to see specific attributes (ie can you see
name?), which then affects, \"could you possibly have queried for
this?\".

Imagine for example, that we search for \"password = X\" (which kanidm
disallows but anyway \...). Even if you could not read password, the act
of testing the equality, if an entry was returned you would know now
about the value or association to a user since the equality condition
held true. This is a security risk for information disclosure.

The first stage of access controls is [what rules apply to your
authenticated
user](https://github.com/kanidm/kanidm/blob/master/kanidmd/src/lib/access.rs#L397).
There may be thousands of access controls in the system, but only some
may related to your account.

    let related_acp: Vec<&AccessControlSearch> =
        lperf_segment!(audit, "access::search_filter_entries<related_acp>", || {
            search_state
                .iter()
                .filter(|acs| {
                    let f_val = acs.acp.receiver.clone();
                    match f_val.resolve(&se.event, None) {
                        Ok(f_res) => rec_entry.entry_match_no_index(&f_res),
                        Err(e) => {
                            ...
                        }
                    }
                })
                .collect()
        });

The next stage is to determine [what attributes did you request to
filter
on](https://github.com/kanidm/kanidm/blob/master/kanidmd/src/lib/access.rs#L440).
This is why [filter_orig]{.title-ref} is stored in the event. We must
test against the filter as intended by the caller, not the filter as
executed. This is because the filter as executed may have been
transformed by the server, using terms the user does not have access to.

    let requested_attrs: BTreeSet<&str> = se.filter_orig.get_attr_set();

Then for each entry, the set of allowed attributes is determined. If the
user related access control also holds rights oven the entry in the
result set, the set of attributes it grants read access over is appended
to the \"allowed\" set. This repeats until the set of related access
controls is exhausted.

    let allowed_entries: Vec<Entry<EntrySealed, EntryCommitted>> =
        entries
            .into_iter()
            .filter(|e| {

                let allowed_attrs: BTreeSet<&str> = related_acp.iter()
                    .filter_map(|acs| {
                        ...
                        if e.entry_match_no_index(&f_res) {
                            // add search_attrs to allowed.
                            Some(acs.attrs.iter().map(|s| s.as_str()))
                        } else {
                            None
                        }
                        ...
                    })
                    .collect();

                let decision = requested_attrs.is_subset(&allowed_attrs);
                lsecurity_access!(audit, "search attr decision --> {:?}", decision);
                decision
            })

This now has created a set of \"attributes this person can see\" on this
entry based on all related rules. The requested attributes are compared
to the attributes you may see, and if requested is a subset or equal,
then the entry is allowed to be returned to the user.

If there is even a single attribute in the query you do not have the
rights to see, then the entry is disallowed from the result set. This is
because if you can not see that attribute, you must not be able to apply
a filter test to it.

To give a worked example, consider the entry from before. We also have
three access controls:

    applies to: all users
    over: pres class
    read attr: class

    applies to: memberof admins
    over: entries where class = account
    read attr: name, displayname

    applies to: memberof radius_servers
    over: entries where class = account
    read attr: radius secret

Our current authenticated user (let\'s assume it\'s also
\"name=william\"), would only have the first two rules apply. As we
search through the candidate entries, the \"all users\" rule would match
our entry, which means class is added to the allowed set. Then since
william is memberof admins, they also have read to name, and
displayname. Since the target entry is class=account then name and
displayname are also added to the allowed set. But since william is
*not* a member of radius_servers, we don\'t get to read radius secrets.

At this point the entry set is reduced to the set of entries the user
was *able* to have applied filter tests too, and is returned.

The query server then unwinds to [search_ext]{.title-ref} where the
second stage of access controls is now checked. This calls
[search_filter_entry_attributes](https://github.com/kanidm/kanidm/blob/master/kanidmd/src/lib/access.rs#L524)
which is responsible for changing an entry in memory to remove content
that the user may not see. A key difference is this line:

Again, the set of related access controls is generated, and then applied
to each entry to determine if they are in scope. This builds a set of
\"attributes the user can see, per entry\". This is then applied to the
entry to reduction function, which removes any attribute *not* in the
allowed set.

    e.reduce_attributes(&allowed_attrs)

A clear example is when you attempt to view yourself vs when you view
another persons account as there are permissions over self that exist,
which do not apply to others. You may view your own legalname field, but
not the legalname of another person.

The entry set is finally returned and turned into a JSON entry for
transmission to the client. Hooray!

## Conclusion

There is a lot that goes into a query being processed in a database. But
like all things in computing since it was created by a person, any other
person must be able to understand it. It\'s always amazing that this
whole process can be achieved in fractions of a second, in parallel, and
so reliably.

There is so much more involved in this process too. The way that a write
operation is performed to extract correct index values, the way that the
database reloads the access control cache based on changes, and even how
the schema is loaded and constructed. Ontop of all this, a complete
identity management stack is built that can allow authentication through
wireless, machines, ssh keys and more.

If you are interested more in databases and
[Kanidm](https://github.com/kanidm/kanidm) please get in contact!

