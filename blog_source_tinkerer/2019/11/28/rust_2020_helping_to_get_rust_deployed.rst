Rust 2020 - helping to get rust deployed
========================================

This is my contribution to Rust 2020, where community members put forward ideas on what they
thing Rust should aim to achieve in 2020.

In my view, Rust has had an amazing adoption by developers, and is great if you are in a position
to deploy it in your own infrastructure, but we have yet to really see Rust make it to broad
low-level components (IE in a linux distro or other infrastructure).

As someone who works on "enterprise" software (389-ds) and my own IDM project (kanidm), there
is a need to have software packaged and distributed. We can not ask our consumers to build
and compile these tools. One could view it as a chain, where I develop software in a language,
it's packaged for a company (like SUSE), and then consumed by a customer (could be anyone!) who
provides a service to others (indirect users).

Rust however has always been modeled that there is no "middle" section. You have either a developer
who's intent is to develop for other developers. This is where Rust ideas like crates.io becomes
involved. Alternately, you have a larger example in firefox, where developers build a project
and can "bundle" everything into a whole unit that is then distributed directly to customers.

The major difference is that in the intermediate distribution case, we have to take on different
responsibilities such as security auditing, building, ensuring dependencies exist etc.

So this leads me to:

1: Cargo Vendor Needs Some Love
-------------------------------

Cargo vendor today is quite confusing in some scenarios, and it's not clear how to have it work
for projects that require offline builds. I have raised issues about this, but largely they have
been un-acted upon.

2: Cargo is Difficult to Use in Mixed Language Projects
-------------------------------------------------------

A large value proposition of Rust is the ability to use it with FFI and C. This is great if you
say have cargo compile your C code for you.

But most major existing projects don't. They use autotools, cmake, or maybe even meson or more
esoteric, waf (looking at you samba). Cargo's extreme opinionation in this area makes it extremely
difficult to integrate Rust into an existing build system reliably. It's hard to point to one
fault, as much as a broader "lack of concern" in the space, and I think cargo needs to evolve
improvements to help allow Rust to be used from other build tools.

3: Rust Moves Too Fast
----------------------

A lot of "slower" enterprise companies want to move slowly, including compiler versions. Admittedly,
this conservative behaviour is because of the historical instability of gcc versions and how it can
change or affect your code between releases. Rust doesn't suffer this, but people are still wary
of fast version changes. This means Rustc + Cargo will get pinned to some version that may be 6 months
old.

However crate authors don't consider this - they will use the latest and greatest features from
stable (and sometimes still nightly ... grrr) in releases. Multiple times I have found that
on my development environment even with a 3 month old compiler, dependencies won't build.

Compounding this, crates.io doesn't distinguish a security release from a feature one. Crates also
encourages continuall version bumping, rather than maintenence of versioned branches. IE version
0.4.3 of a crate with a security fix will become 0.4.4, but then a feature update to include try_from
may go to 0.4.5 as it "adds" to the api, or they use it internally as a cleanup.

Part of this issue is that Rust applications need to be treated closer to docker, as static whole
units where only the resulting binary is supported rather than the toolchain that built it. But
that only works on pure Rust applications - any mixed C + Rust application will hit this issue
due to the difference between a system Rust version and what crate dependencies publish.

So I think that from this it leads to:

3.1: Crates need to indicate a minimum supported compiler version
-----------------------------------------------------------------

Rust has "toyed" with the idea of editions, but within 2018 we've seen new features like maybeuninit
and try_from land, which within an "edition" caused crates to stop worked on older compilers.

As a result, editions I think is "too broad" and people will fear incrementing it, and Rust will
add features without changing edition anyway. Instead
Rust needs to consider following up on the minimum supported rust version flag RFC. Rust has made
it pretty clear the only "edition" flag that matters is the rust compiler version based on crate
developers and what they are releasing.

3.2: Rust Needs to Think "What's Our End Goal"
----------------------------------------------

Rust is still moving incredibly fast, and I think in a way we need to ask ... when will Rust be
finished? When will it as a language go from continually rapid growth to stable and known feature
sets? The idea of Rust editions acts as though this has happened (saying we change only every few years)
when this is clearly not the case. Rust is evolving release-on-release, every 6 weeks.

4: Zero Cost Needs to Factor in Human Cost
------------------------------------------

My final wish for Rust is that sometimes we are so obsessed with the technical desire for zero cost
abstraction, that we forget the high human cost and barriers that can exist as a result making
feature adoption challenging. Rust has had a great community that treats people very well, and I
think sometimes we need to extend that into feature development, to really consider the human
cognitive cost of a feature.

Summarised - what's the benefit of a zero cost abstraction if people can not work out how to use it?


Summary
-------

I want to see Rust become a major part of operating systems and how we build computer systems, but
I think that we need to pace ourselves, improve our tooling, and have some better ideas around
what Rust should look like.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
