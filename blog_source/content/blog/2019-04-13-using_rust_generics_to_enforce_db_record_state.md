+++
title = "Using Rust Generics to Enforce DB Record State"
date = 2019-04-13
slug = "2019-04-13-using_rust_generics_to_enforce_db_record_state"
# This is relative to the root!
aliases = [ "2019/04/13/using_rust_generics_to_enforce_db_record_state.html" ]
+++
# Using Rust Generics to Enforce DB Record State

In a database, entries go through a lifecycle which represents what
attributes they have have, db record keys, and if they have conformed to
schema checking.

I\'m currently working on a (private in 2019, public in july 2019)
project which is a NoSQL database writting in Rust. To help us manage
the correctness and lifecycle of database entries, I have been using
advice from the [Rust Embedded Group\'s
Book.](https://docs.rust-embedded.org/book/static-guarantees/state-machines.html)

As I have mentioned in the past, state machines are a great way to
design code, so let\'s plot out the state machine we have for Entries:

## Entry State Machine

The lifecyle is:

-   A new entry is submitted by the user for creation
-   We schema check that entry
-   If it passes schema, we commit it and assign internal ID\'s
-   When we search the entry, we retrieve it by internal ID\'s
-   When we modify the entry, we need to recheck it\'s schema before we
    commit it back
-   When we delete, we just remove the entry.

This leads to a state machine of:

    |
    (create operation)
    |
    v
    [ New + Invalid ] -(schema check)-> [ New + Valid ]
                                      |
                               (send to backend)
                                      |
                                      v    v-------------\
    [Commited + Invalid] <-(modify operation)- [ Commited + Valid ]          |
    |                                          ^   \       (write to backend)
    \--------------(schema check)-------------/     ---------------/

This is a bit rough - The version on my whiteboard was better :)

The main observation is that we are focused only on the commitability
and validty of entries - not about where they are or if the commit was a
success.

## Entry Structs

So to make these states work we have the following structs:

    struct EntryNew;
    struct EntryCommited;

    struct EntryValid;
    struct EntryInvalid;

    struct Entry<STATE, VALID> {
        state: STATE,
        valid: VALID,
        // Other db junk goes here :)
    }

We can then use these to establish the lifecycle with functions
(similar) to this:

    impl Entry<EntryNew, EntryInvalid> {
        fn new() -> Self {
            Entry {
                state: EntryNew,
                valid: EntryInvalid,
                ...
            }
        }

    }

    impl<STATE> Entry<STATE, EntryInvalid> {
        fn validate(self, schema: Schema) -> Result<Entry<STATE, EntryValid>, ()> {
            if schema.check(self) {
                Ok(Entry {
                    state: self.state,
                    valid: EntryValid,
                    ...
                })
            } else {
                Err(())
            }
        }

        fn modify(&mut self, ...) {
            // Perform any modifications on the entry you like, only works
            // on invalidated entries.
        }
    }

    impl<STATE> Entry<STATE, EntryValid> {
        fn seal(self) -> Entry<EntryCommitted, EntryValid> {
            // Assign internal id's etc
            Entry {
                state: EntryCommited,
                valid: EntryValid,
            }
        }

        fn compare(&self, other: Entry<STATE, EntryValid>) -> ... {
            // Only allow compares on schema validated/normalised
            // entries, so that checks don't have to be schema aware
            // as the entries are already in a comparable state.
        }
    }

    impl Entry<EntryCommited, EntryValid> {
        fn invalidate(self) -> Entry<EntryCommited, EntryInvalid> {
            // Invalidate an entry, to allow modifications to be performed
            // note that modifications can only be applied once an entry is created!
            Entry {
                state: self.state,
                valid: EntryInvalid,
            }
        }
    }

What this allows us to do importantly is to control when we apply search
terms, send entries to the backend for storage and more. Benefit is this
is compile time checked, so you can never send an entry to a backend
that is *not* schema checked, or run comparisons or searches on entries
that aren\'t schema checked, and you can even only modify or delete
something once it\'s created. For example other parts of the code now
have:

    impl BackendStorage {
        // Can only create if no db id's are assigned, IE it must be new.
        fn create(&self, ..., entry: Entry<EntryNew, EntryValid>) -> Result<...> {
        }

        // Can only modify IF it has been created, and is validated.
        fn modify(&self, ..., entry: Entry<EntryCommited, EntryValid>) -> Result<...> {
        }

        // Can only delete IF it has been created and committed.
        fn delete(&self, ..., entry: Entry<EntryCommited, EntryValid>) -> Result<...> {
        }
    }

    impl Filter<STATE> {
        // Can only apply filters (searches) if the entry is schema checked. This has an
        // important behaviour, where we can schema normalise. Consider a case-insensitive
        // type, we can schema-normalise this on the entry, then our compare can simply
        // be a string.compare, because we assert both entries *must* have been through
        // the normalisation routines!
        fn apply_filter(&self, ..., entry: &Entry<STATE, EntryValid>) -> Result<bool, ...> {
        }
    }

## Using this with Serde?

I have noticed that when we serialise the entry, that this causes the
valid/state field to *not* be compiled away - because they *have* to be
serialised, regardless of the empty content meaning the compiler can\'t
eliminate them.

A future cleanup will be to have a serialised DBEntry form such as the
following:

    struct DBEV1 {
        // entry data here
    }

    enum DBEntryVersion {
        V1(DBEV1)
    }

    struct DBEntry {
        data: DBEntryVersion
    }

    impl From<Entry<EntryNew, EntryValid>> for DBEntry {
        fn from(e: Entry<EntryNew, EntryValid>) -> Self {
            // assign db id's, and return a serialisable entry.
        }
    }

    impl From<Entry<EntryCommited, EntryValid>> for DBEntry {
        fn from(e: Entry<EntryCommited, EntryValid>) -> Self {
            // Just translate the entry to a serialisable form
        }
    }

This way we still have the zero-cost state on Entry, but we are able to
move to a versioned seralised structure, and we minimise the run time
cost.

## Testing the Entry

To help with testing, I needed to be able to shortcut and move between
anystate of the entry so I could quickly make fake entries, so I added
some unsafe methods:

    #[cfg(test)]
    unsafe fn to_new_valid(self, Entry<EntryNew, EntryInvalid>) -> {
        Entry {
            state: EntryNew,
            valid: EntryValid
        }
    }

These allow me to setup and create small unit tests where I may not have
a full backend or schema infrastructure, so I can test specific aspects
of the entries and their lifecycle. It\'s limited to test runs only, and
marked unsafe. It\'s not \"technically\" memory unsafe, but it\'s unsafe
from the view of \"it could absolutely mess up your database consistency
guarantees\" so you have to really want it.

## Summary

Using statemachines like this, really helped me to clean up my code,
make stronger assertions about the correctness of what I was doing for
entry lifecycles, and means that I have more faith when I and
future-contributors will work on the code base that we\'ll have compile
time checks to ensure we are doing the right thing - to prevent data
corruption and inconsistency.

