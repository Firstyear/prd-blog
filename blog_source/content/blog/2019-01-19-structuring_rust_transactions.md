+++
title = "Structuring Rust Transactions"
date = 2019-01-19
slug = "2019-01-19-structuring_rust_transactions"
# This is relative to the root!
aliases = [ "2019/01/19/structuring_rust_transactions.html" ]
+++
# Structuring Rust Transactions

I\'ve been working on a database-related project in Rust recently, which
takes advantage of my [concurrently readable
datastructures.](https://crates.io/crates/concread) However I ran into a
problem of how to structure Read/Write transaction structures that
shared the reader code, and container multiple inner read/write types.

## Some Constraints

To be clear, there are some constraints. A \"parent\" write, will only
ever contain write transaction guards, and a read will only ever contain
read transaction guards. This means we aren\'t going to hit any
deadlocks in the code. Rust can\'t protect us from mis-ording locks. An
additional requirement is that readers and a single write must be able
to proceed simultaneously - but having a rwlock style writer or readers
behaviour would still work here.

## Some Background

To simplify this, imagine we have two concurrently readable
datastructures. We\'ll call them db_a and db_b.

    struct db_a { ... }

    struct db_b { ... }

Now, each of db_a and db_b has their own way to protect their inner
content, but they\'ll return a DBWriteGuard or DBReadGuard when we call
db_a.read()/write() respectively.

    impl db_a {
        pub fn read(&self) -> DBReadGuard {
            ...
        }

        pub fn write(&self) -> DBWriteGuard {
            ...
        }
    }

Now we make a \"parent\" wrapper transaction such as:

    struct server {
        a: db_a,
        b: db_b,
    }

    struct server_read {
        a: DBReadGuard,
        b: DBReadGuard,
    }

    struct server_write {
        a: DBWriteGuard,
        b: DBWriteGuard,
    }

    impl server {
        pub fn read(&self) -> server_read {
            server_read {
                self.a.read(),
                self.b.read(),
            }
        }

        pub fn write(&self) -> server_write {
            server_read {
                self.a.write(),
                self.b.write(),
            }
        }
    }

## The Problem

Now the problem is that on my server_read and server_write I want to
implement a function for \"search\" that uses the same code. Search or a
read or write should behave identically! I wanted to also avoid the use
of macros as the can hide issues while stepping in a debugger like
LLDB/GDB.

Often the answer with rust is \"traits\", to create an interface that
types adhere to. Rust also allows default trait implementations, which
sounds like it could be a solution here.

    pub trait server_read_trait {
        fn search(&self) -> SomeResult {
            let result_a = self.a.search(...);
            let result_b = self.b.search(...);
            SomeResult(result_a, result_b)
        }
    }

In this case, the issue is that &self in a trait is not aware of the
fields in the struct - traits don\'t define that fields *must* exist, so
the compiler can\'t assume they exist at all.

Second, the type of self.a/b is unknown to the trait - because in a read
it\'s a \"a: DBReadGuard\", and for a write it\'s \"a: DBWriteGuard\".

The first problem can be solved by using a get_field type in the trait.
Rust will also compile this out as an inline, so the *correct* thing for
the type system is also the *optimal* thing at run time. So we\'ll
update this to:

    pub trait server_read_trait {
        fn get_a(&self) -> ???;

        fn get_b(&self) -> ???;

        fn search(&self) -> SomeResult {
            let result_a = self.get_a().search(...); // note the change from self.a to self.get_a()
            let result_b = self.get_b().search(...);
            SomeResult(result_a, result_b)
        }
    }

    impl server_read_trait for server_read {
        fn get_a(&self) -> &DBReadGuard {
            &self.a
        }
        // get_b is similar, so ommitted
    }

    impl server_read_trait for server_write {
        fn get_a(&self) -> &DBWriteGuard {
            &self.a
        }
        // get_b is similar, so ommitted
    }

So now we have the second problem remaining: for the server_write we
have DBWriteGuard, and read we have a DBReadGuard. There was a much
longer experimentation process, but eventually the answer was simpler
than I was expecting. Rust allows traits to have Self types that enforce
trait bounds rather than a concrete type.

So provided that DBReadGuard and DBWriteGuard both implement
\"DBReadTrait\", then we can have the server_read_trait have a self type
that enforces this. It looks something like:

    pub trait DBReadTrait {
        fn search(&self) -> ...;
    }

    impl DBReadTrait for DBReadGuard {
        fn search(&self) -> ... { ... }
    }

    impl DBReadTrait for DBWriteGuard {
        fn search(&self) -> ... { ... }
    }

    pub trait server_read_trait {
        type GuardType: DBReadTrait; // Say that GuardType must implement DBReadTrait

        fn get_a(&self) -> &Self::GuardType; // implementors must return that type implementing the trait.

        fn get_b(&self) -> &Self::GuardType;

        fn search(&self) -> SomeResult {
            let result_a = self.get_a().search(...);
            let result_b = self.get_b().search(...);
            SomeResult(result_a, result_b)
        }
    }

    impl server_read_trait for server_read {
        fn get_a(&self) -> &DBReadGuard {
            &self.a
        }
        // get_b is similar, so ommitted
    }

    impl server_read_trait for server_write {
        fn get_a(&self) -> &DBWriteGuard {
            &self.a
        }
        // get_b is similar, so ommitted
    }

This works! We now have a way to write a single \"search\" type for our
server read and write types. In my case, the DBReadTrait also uses a
similar technique to define a search type shared between the DBReadGuard
and DBWriteGuard.

