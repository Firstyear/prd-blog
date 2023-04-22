+++
title = "Time safety and Rust"
date = 2017-07-12
slug = "2017-07-12-time_safety_and_rust"
# This is relative to the root!
aliases = [ "2017/07/12/time_safety_and_rust.html", "blog/html/2017/07/12/time_safety_and_rust.html" ]
+++
# Time safety and Rust

Recently I have had the great fortune to work on [this
ticket](https://pagure.io/389-ds-base/issue/49316) . This was an issue
that stemmed from an attempt to make clock performance faster.
Previously, a call to time or clock_gettime would involve a context
switch an a system call (think solaris etc). On linux we have VDSO
instead, so we can easily just swap to the use of raw time calls.

## The problem

So what was the problem? And how did the engineers of the past try and
solve it?

DS heavily relies on time. As a result, we call time() a *lot* in the
codebase. But this would mean context switches.

So a wrapper was made called \"current_time()\", which would cache a
recent output of time(), and then provide that to the caller instead of
making the costly context switch. So the code had the following:

    static time_t   currenttime;
    static int      currenttime_set = 0;

    time_t
    poll_current_time()
    {
        if ( !currenttime_set ) {
            currenttime_set = 1;
        }

        time( &currenttime );
        return( currenttime );
    }

    time_t
    current_time( void )
    {
        if ( currenttime_set ) {
            return( currenttime );
        } else {
            return( time( (time_t *)0 ));
        }
    }

In another thread, we would poll this every second to update the
currenttime value:

    void * 
    time_thread(void *nothing __attribute__((unused)))
    {
        PRIntervalTime    interval;

        interval = PR_SecondsToInterval(1);

        while(!time_shutdown) {
            poll_current_time();
            csngen_update_time ();
            DS_Sleep(interval);
        }

        /*NOTREACHED*/
        return(NULL);
    }

*So what is the problem here*

Besides the fact that we may not poll accurately (meaning we miss
seconds but always advance), this is not *thread safe*. The reason is
that CPU\'s have register and buffers that may cache both stores and
writes until a series of other operations (barriers + atomics) occur to
flush back out to cache. This means the time polling thread could update
the clock and unless the POLLING thread issues a lock or a
barrier+atomic, there is *no guarantee the new value of currenttime will
be seen in any other thread*. This means that the only way this worked
was by luck, and no one noticing that time would jump about or often
just be wrong.

Clearly this is a broken design, but this is C - we can do anything.

## What if this was Rust?

Rust touts mulithread safety high on it\'s list. So lets try and
recreate this in rust.

First, the exact same way:

    use std::time::{SystemTime, Duration};
    use std::thread;


    static mut currenttime: Option<SystemTime> = None;

    fn read_thread() {
        let interval = Duration::from_secs(1);

        for x in 0..10 {
            thread::sleep(interval);
            let c_time = currenttime.unwrap();
            println!("reading time {:?}", c_time);
        }
    }

    fn poll_thread() {
        let interval = Duration::from_secs(1);

        for x in 0..10 {
            currenttime = Some(SystemTime::now());
            println!("polling time");
            thread::sleep(interval);
        }
    }

    fn main() {
        let poll = thread::spawn(poll_thread);
        let read = thread::spawn(read_thread);
        read.join().unwrap();
        poll.join().unwrap();
    }

*Rust will not compile this code*.

    > rustc clock.rs
    error[E0133]: use of mutable static requires unsafe function or block
      --> clock.rs:13:22
       |
    13 |         let c_time = currenttime.unwrap();
       |                      ^^^^^^^^^^^ use of mutable static

    error[E0133]: use of mutable static requires unsafe function or block
      --> clock.rs:22:9
       |
    22 |         currenttime = Some(SystemTime::now());
       |         ^^^^^^^^^^^ use of mutable static

    error: aborting due to 2 previous errors

Rust has told us that this action is *unsafe*, and that we shouldn\'t be
modifying a global static like this.

This alone is a great reason and demonstration of why we need a language
like Rust instead of C - the compiler can tell us when actions are
dangerous at compile time, rather than being allowed to sit in
production code for years.

For bonus marks, because Rust is stricter about types than C, we don\'t
have issues like:

    int c_time = time();

Which is a 2038 problem in the making :)

