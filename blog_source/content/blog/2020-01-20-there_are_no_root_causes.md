+++
title = "There are no root causes"
date = 2020-01-20
slug = "2020-01-20-there_are_no_root_causes"
# This is relative to the root!
aliases = [ "2020/01/20/there_are_no_root_causes.html", "blog/html/2020/01/20/there_are_no_root_causes.html" ]
+++
# There are no root causes

At Gold Coast LCA2020 I gave a [lightning talk on swiss
cheese](https://www.youtube.com/watch?v=eqQUepwTHjA&t=25m47s). Well,
maybe not really swiss cheese. But it was about the [swiss cheese
failure model](https://en.wikipedia.org/wiki/Swiss_cheese_model) which
was proposed at the university of manchester.

Please note this will cover some of the same topics as the talk, but in
more detail, and with less jokes.

## An example problem

So we\'ll discuss the current issues behind modern CPU isolation attacks
IE spectre. Spectre is an attack that uses timing of a CPU\'s
speculative execution unit to retrieve information from another running
process on the same physical system.

Modern computers rely on hardware features in their CPU to isolate
programs from each other. This could be isolating your web-browser from
your slack client, or your sibling\'s login from yours.

This isolation however has been compromised by attacks like Spectre, and
it looks unlikely that it can be resolved.

## What is speculative execution?

In order to be \"fast\" modern CPU\'s are far more complex than most of
us have been taught. Often we believe that a CPU thread/core is
executing \"one instruction/operation\" at a time. However this isn\'t
how most CPU\'s work. Most work by having a pipeline of instructions
that are in various stages of execution. You could imagine it like this:

    let mut x = 0
    let mut y = 0
    x = 15 * some_input;
    y = 10 * other_input;
    if x > y {
        return true;
    } else {
        return false;
    }

This is some made up code, but in a CPU, every part of this could be in
the \"pipeline\" at once.

    let mut x = 0                   <<-- at the head of the queue and "further" along completion
    let mut y = 0                   <<-- it's executed part way, but not to completion
    x = 15 * some_input;
    y = 10 * other_input;           <<-- all of these are in pipeline, and partially complete
    if x > y {                      <<-- what happens here?
        return true;
    } else {
        return false;
    }

So how does this \"pipeline\" handle the if statement? If the pipeline
is looking ahead, how can we handle a choice like an if? Can we really
predict the future?

## Speculative execution

At the if statement, the CPU uses past measurements to make a
*prediction* about which branch *might* be taken, and it then begins to
execute that path, even though \'x \> y\' has not been executed or
completed yet! At this point x or y may not have even finished *being
computed* yet!

Let\'s assume for now our branch predictor thinks that \'x \> y\' is
false, so we\'ll start to execute the \"return false\" or any other
content in that branch.

Now the instructions ahead catch up, and we resolve \"did we really
predict correctly?\". If we did, great! We have been able to advance the
program state *asynchronously* even without knowing the answer until we
get there.

If not, ohh nooo. We have to unwind what we were doing, clear some of
the pipeline and try to do the correct branch.

Of course this has an impact on *timing* of the program. Some people
found you could write a program to manipulate this predictor and using
specific addresses and content, they could use these timing variations
to \"access memory\" they are not allowed to by letting the specualative
executor contribute to code they are not allowed to access before the
unroll occurs. They could time this, and retrieve the memory contents
from areas they are not allowed to access, breaking isolation.

## Owwww my brain

Yes. Mine too.

## Community Reactions

Since this has been found, a large amount of the community reaction has
been about the \"root cause\". \'Clearly\' the root cause is \"Intel are
bad at making CPU\'s\" and so everyone should buy AMD instead because
they \"weren\'t affected quite as badly\" (Narrators voice: [They were
absolutely just as
bad](https://www.zdnet.com/article/amd-processors-from-2011-to-2019-vulnerable-to-two-new-attacks/)).
We\'ve had some intel CPU updates and kernel/program fixes so all good
right? We addressed the root cause.

## Or \... did we?

Our computers are still asynchronous, and contain many out-of-order
parts. It\'s hard to believe we have \"found\" every method of
exploiting this. Indeed in the last year many more ways to bypass
hardware isolation due to our systems async nature have been found.

Maybe the \"root cause\" wasn\'t addressed. Maybe \... there are no
\....

## History

To understand how we got to this situation we need to look at how CPU\'s
have evolved. This is not a complete history.

The PDP11 was a system owned at bell labs, where the C programing
language was developed. Back then CPU\'s were very simple - A CPU and
memory, executing one instruction at a time.

The C programming language gained a lot of popularity as it was able to
be \"quickly\" ported to other CPU models to allow software to be
compiled on other platforms. This led to many systems being developed in
C.

Intel introduced the 8086, and many C programs were ported to run on it.
Intel then released the 80486 in 1989, which had the first pipeline and
cache to improve performance. In order to continue to support C, this
meant the memory model could not change from the PDP11 - the cache had
to be transparent, and the pipeline could not expose state.

This has of course led to computers being more important in our lives
and businesses, so we expected further performance, leading to increased
frequencies and async behaviours.

The limits of frequencies were really hit in the Pentium 4 era, when
about 4GHz was shown to be a barrier of stability for those systems.
They had very deep pipelines to improve performance, but that also had
issues when branch prediction failed causing pipeline stalls. Systems
had to improve their async behaviours *futher* to squeeze every single
piece of performance possible out.

Compiler developers also wanted more performance so they started to
develop ways to transform C in ways that \"took advantage\" of x86_64
tricks, by manipulating the environment so the CPU is \"hinted\" into
states we \"hope\" it gets into.

Many businesses also started to run servers to provide to consumers, and
in order to keep costs low they would put many users onto single pieces
of hardware so they could share or overcommit resources.

This has created a series of positive reinforcement loops - C is \'abi
stable\' so we keep developing it due to it\'s universal nature. C code
can\'t be changed without breaking every existing system. We can\'t
change the CPU memory model without breaking C, which is hugely
prevalent. We improve the CPU to make C faster, transparently so that
users/businesses can run more C programs and users. And then we improve
compilers to make C faster given quirks of the current CPU models that
exist \...

## Swiss cheese model

It\'s hard to look at the current state of systems security and simply
say \"it\'s the cpu vendors fault\". There are many layers that have
come together to cause this situation.

This is called the \"swiss cheese model\". Imagine you take a stack of
swiss cheese and rotate and rearrange the slices. You will not be able
to see through it. but as you continue to rotate and rearrange,
eventually you may see a tunnel through the cheese where all the holes
line up.

This is what has happened here - we developed many layers socially and
technically that all seemed reasonable over time, and only after enough
time and re-arrangements of the layers, have we now arrived at a
situation where a failure has occured that permeates all of computer
hardware.

To address it, we need to look beyond just \"blaming hardware makers\"
or \"software patches\". We need to help developers move away from C to
other languages that can be brought onto new memory models that have
manual or other cache strategies. We need hardware vendors to implement
different async models. We need to educate businesses on risk analysis
and how hardware works to provide proper decision making capability. We
need developers to alter there behaviour to work in environments with
higher performance constraints. And probably much much more.

## There are no root causes

It is a very pervasive attitude in IT that every issue has a root cause.
However, looking above we can see it\'s never quite so simple.

Saying an issue has a root cause, prevents us from examining the social,
political, economic and human factors that all become contributing
factors to failure. Because we are unable to examine them, we are unable
to address the various layers that have contributed to our failures.

There are no root causes. Only contributing factors.

