+++
title = "CPU atomics and orderings explained"
date = 2019-07-16
slug = "2019-07-16-cpu_atomics_and_orderings_explained"
# This is relative to the root!
aliases = [ "2019/07/16/cpu_atomics_and_orderings_explained.html" ]
+++
# CPU atomics and orderings explained

Sometimes the question comes up about how CPU memory orderings work, and
what they do. I hope this post explains it in a really accessible way.

## Short Version - I wanna code!

Summary - The memory model you commonly see is from C++ and it defines:

-   Relaxed
-   Acquire
-   Release
-   Acquire/Release (sometimes AcqRel)
-   SeqCst

There are memory orderings - every operation is \"atomic\", so will work
correctly, but there rules define how the memory and code *around* the
atomic are influenced.

If in doubt - use SeqCst - it\'s the strongest guarantee and prevents
all re-ordering of operations and will do the right thing.

The summary is:

-   Relaxed - no ordering guarantees, just execute the atomic as is.
-   Acquire - all code after this atomic, will be executed after the
    atomic.
-   Release - all code before this atomic, will be executed before the
    atomic.
-   Acquire/Release - both Acquire and Release - ie code stays before
    and after.
-   SeqCst - Stronger consistency of Acquire/Release.

## Long Version \... let\'s begin \...

So why do we have memory and operation orderings at all? Let\'s look at
some code to explain:

    let mut x = 0;
    let mut y = 0;
    x = x + 3;
    y = y + 7;
    x = x + 4;
    x = y + x;

Really trivial example - now to us as a human, we read this and see a
set of operations that are linear by time. That means, they execute from
top to bottom, in order.

However, this is not how computers work. First, compilers will optimise
your code, and optimisation means re-ordering of the operations to
achieve better results. A compiler may optimise this to:

    let mut x = 0;
    let mut y = 0;
    // Note removal of the x + 3 and x + 4, folded to a single operation.
    x = x + 7
    y = y + 7;
    x = y + x;

Now there is a second element. Your CPU presents the illusion of running
as a linear system, but it\'s actually an asynchronous, out-of-order
task execution engine. That means a CPU will reorder your instructions,
and may even run them concurrently and asynchronously.

For example, your CPU will have both x + 7 and y + 7 in the pipeline,
even though neither operation has completed - they are effectively
running at the \"same time\" (concurrently).

When you write a single thread program, you generally won\'t notice this
behaviour. This is because a lot of smart people write compilers and
CPU\'s to give the illusion of linear ordering, even though both of them
are operating very differently.

Now we want to write a multithreaded application. Suddenly this is the
challenge:

*We write a concurrent program, in a linear language, executed on a
concurrent asynchronous machine.*

This means there is a challenge is the translation between our mind
(thinking about the concurrent problem), the program (which we have to
express as a linear set of operations), which then runs on our CPU (an
async concurrent device).

Phew. How do computers even work in this scenario?!

## Why are CPU\'s async?

CPU\'s have to be async to be fast - remember spectre and meltdown?
These are attacks based on measuring the side effects of CPU\'s
asynchronous behaviour. While computers are \"fast\" these attacks will
always be possible, because to make a CPU synchronous is *slow* - and
asynchronous behaviour will always have measurable side effects. Every
modern CPU\'s performance is an illusion of async forbidden magic.

A large portion of the async behaviour comes from the interaction of the
CPU, cache, and memory.

In order to provide the \"illusion\" of a coherent synchronous memory
interface there is no seperation of your programs cache and memory. When
the cpu wants to access \"memory\" the CPU cache is utilised
transparently and will handle the request, and only on a cache miss,
will we retrieve the values from RAM.

(Aside: in almost all cases more CPU cache, not frequency will make your
system perform better, because a cache miss will mean your task stalls
waiting on RAM. Ohh no!)

    CPU -> Cache -> RAM

When you have multiple CPU\'s, each CPU has it\'s own L1 cache:

    CPU1 -> L1 Cache -> |              |
    CPU2 -> L1 Cache -> | Shared L2/L3 | -> RAM
    CPU3 -> L1 Cache -> |              |
    CPU4 -> L1 Cache -> |              |

Ahhh! Suddenly we can see where problems can occur - each CPU has an L1
cache, which is transparent to memory but *unique* to the CPU. This
means that each CPU can make a change to the same piece of memory in
their L1 cache *without the other CPU knowing*. To help explain, let\'s
show a demo.

## CPU just trash my variables

We\'ll assume we now have two threads - my code is in rust again, and
there is a good reason for the unsafes - this code really is unsafe!

    // assume global x: usize = 0; y: usize = 0;

    THREAD 1                        THREAD 2

    if unsafe { *x == 1 } {          unsafe {
        unsafe { *y += 1 }              *y = 10;
    }                                   *x = 1;
                                    }

At the end of execution, what state will X and Y be in? The answer is
\"it depends\":

-   What order did the threads run?
-   The state of the L1 cache of each CPU
-   The possible interleavings of the operations.
-   Compiler re-ordering

In the end the result of x will always be 1 - because x is only mutated
in one thread, the caches will \"eventually\" (explained soon) become
consistent.

The real question is y. y could be:

-   10
-   11
-   1

*10* - This can occur because in thread 2, x = 1 is re-ordered above y =
10, causing the thread 1 \"y += 1\" to execute, followed by thread 2
assign 10 directly to y. It can also occur because the check for x == 1
occurs first, so y += 1 is skipped, then thread 2 is run, causing y =
10. Two ways to achieve the same result!

*11* - This occurs in the \"normal\" execution path - all things
considered it\'s a miracle :)

*1* - This is the most complex one - The y = 10 in thread 2 is applied,
but the result is never sent to THREAD 1\'s cache, so x = 1 occurs and
*is* made available to THREAD 1 (yes, this is possible to have different
values made available to each cpu \...). Then thread 1 executes y (0) +=
1, which is then sent back trampling the value of y = 10 from thread 2.

If you want to know more about this and many other horrors of CPU
execution, Paul McKenny is an expert in this field and has many talks at
LCA and others on the topic. He can be found on
[twitter](https://twitter.com/paulmckrcu) and is super helpful if you
have questions.

## So how does a CPU work at all?

Obviously your system (likely a multicore system) works today - so it
must be possible to write correct concurrent software. Cache\'s are kept
in sync via a protocol called MESI. This is a state machine describing
the states of memory and cache, and how they can be synchronised. The
states are:

-   Modified
-   Exclusive
-   Shared
-   Invalid

What\'s interesting about MESI is that each cache line is maintaining
it\'s own state machine of the memory addresses - it\'s not a global
state machine. To coordinate CPU\'s asynchronously message each other.

A CPU can be messaged via IPC (Inter-Processor-Communication) to say
that another CPU wants to \"claim\" exclusive ownership of a memory
address, or to indicate that it has changed the content of a memory
address and you should discard your version. It\'s important to
understand these messages are *asynchronous*. When a CPU modifies an
address it does not immediately send the invalidation message to all
other CPU\'s - and when a CPU recieves the invalidation request it does
not immediately act upon that message.

If CPU\'s did \"synchronously\" act on all these messages, they would be
spending so much time handling IPC traffic, they would never get
anything done!

As a result, it must be possible to indicate to a CPU that it\'s time to
send or acknowledge these invalidations in the cache line. This is where
barriers, or the memory orderings come in.

-   Relaxed - No messages are sent or acknowledged.
-   Release - flush all pending invalidations to be sent to other CPUS
-   Acquire - Acknowledge and process all invalidation requests in my
    queue
-   Acquire/Release - flush all outgoing invalidations, and process my
    incomming queue
-   SeqCst - as AcqRel, but with some other guarantees around ordering
    that are beyond this discussion.

## Understand a Mutex

With this knowledge in place, we are finally in a position to understand
the operations of a Mutex

    // Assume mutex: Mutex<usize> = Mutex::new(0);

    THREAD 1                            THREAD 2

    {                                   {
        let guard = mutex.lock()            let guard = mutex.lock()
        *guard += 1;                        println!(*guard)
    }                                   }

We know very clearly that this will print 1 or 0 - it\'s safe, no weird
behaviours. Let\'s explain this case though:

    THREAD 1

    {
        let guard = mutex.lock()
        // Acquire here!
        // All invalidation handled, guard is 0.
        // Compiler is told "all following code must stay after .lock()".
        *guard += 1;
        // content of usize is changed, invalid req is queue
    }
    // Release here!
    // Guard goes out of scope, invalidation reqs sent to all CPU's
    // Compiler told all proceeding code must stay above this point.

                THREAD 2

                {
                    let guard = mutex.lock()
                    // Acquire here!
                    // All invalidations handled - previous cache of usize discarded
                    // and read from THREAD 1 cache into S state.
                    // Compiler is told "all following code must stay after .lock()".
                    println(*guard);
                }
                // Release here!
                // Guard goes out of scope, no invalidations sent due to
                // no modifications.
                // Compiler told all proceeding code must stay above this point.

And there we have it! How barriers allow us to define an ordering in
code and a CPU, to ensure our caches and compiler outputs are correct
and consistent.

## Benefits of Rust

A nice benefit of Rust, and knowing these MESI states now, we can see
that the best way to run a system is to minimise the number of
invalidations being sent and acknowledged as this always causes a delay
on CPU time. Rust variables are always mutable or immutable. These map
almost directly to the E and S states of MESI. A mutable value is always
exclusive to a single cache line, with no contention - and immutable
values can be placed into the Shared state allowing each CPU to maintain
a cache copy for higher performance.

This is one of the reasons for Rust\'s amazing concurrency story is that
the memory in your program map to cache states very clearly.

It\'s also why it\'s unsafe to mutate a pointer between two threads (a
global) - because the cache of the two cpus\' won\'t be coherent, and
you may not cause a crash, but one threads work will absolutely be lost!

Finally, it\'s important to see that this is why using the correct
concurrency primitives matter -it can highly influence your cache
behaviour in your program and how that affects cache line contention and
performance.

For comments and more, please feel free to [email
me!](mailto:william@blackhats.net.au)

## Shameless Plug

I\'m the author and maintainer of Conc Read - a concurrently readable
datastructure library for Rust. [Check it out on
crates.io!](https://crates.io/crates/concread)

## References

[What every programmer should know about memory
(pdf)](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)

[Rust-nomicon - memory
ordering](https://doc.rust-lang.org/nomicon/atomics.html)

[Microarchitectural inspection with Sushi
Roll](https://gamozolabs.github.io/metrology/2019/08/19/sushi_roll.html)

