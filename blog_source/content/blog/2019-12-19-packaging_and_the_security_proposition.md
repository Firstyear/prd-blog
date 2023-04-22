+++
title = "Packaging and the Security Proposition"
date = 2019-12-19
slug = "2019-12-19-packaging_and_the_security_proposition"
# This is relative to the root!
aliases = [ "2019/12/19/packaging_and_the_security_proposition.html", "blog/html/2019/12/19/packaging_and_the_security_proposition.html" ]
+++
# Packaging and the Security Proposition

As a follow up to my post on distribution packaging, it was commented by
Fraser Tweedale (@hackuador) that traditionally the \"security\" aspects
of distribution packaging was a compelling reason to use distribution
packages over \"upstreams\". I want to dig into this further.

## Why does C need \"securing\"

C as a language is *unsafe* in every meaning of the word. The best C
programmers on the planet are incapable of writing a secure program.
This is because to code in C you have to express a concurrent problem,
into a language that is linearised, which is compiled relying on
undefined behaviour, to be executed on an asynchronous concurrent out of
order CPU. What could possibly go wrong?!

There is a lot you need to hold in mind to make C work. I can tell you
now that I spend a majority of my development time thinking about the
code to change rather than writing C because of this!

This has led to C based applications having just about every security
issue known to man.

## How is C \"secured\"

So as C is security swiss cheese, this means we have developed processes
around the language to soften this issue - for example advice like patch
and update continually as new changes are continually released to
resolve issues.

Distribution packages have always been the \"source\" of updates for
these libraries and applications. These packages are maintained by
humans who need to update these packages. This means when a C project
releases a fix, these maintainers would apply the patch to various
versions, and then release the updates. These library updates due to
C\'s dynamic nature means when the machine is next rebooted (yes
rebooted, not application restarted) that these fixes apply to all
consumers who have linked to that library - change one, fix everything.
Great!

But there are some (glaring) weaknesses to this model. C historically
has little to poor application testing so many of these patches and
their effects can\'t be reproduced. Which also subsequently means that
consuming applications also aren\'t re-tested adequately. It can also
have impacts where a change to a shared library can impact a consuming
application in a way that was unforseen as the library changed.

## The Dirty Secret

The dirty secret of many of these things is that \"thoughts and
prayers\" is often the testing strategy of choice when patches are
applied. It\'s only because humans carefully think about and write tiny
amounts of C that we have any reliability in our applications. And we
already established that it\'s nearly impossible for humans to write
correct C \...

## Why Are We Doing This?

Because C linking and interfaces are so fragile, and due to the huge
scope in which C can go wrong due to being a memory unsafe language,
distributions and consumers have learnt to fear *version changes*. So
instead we patch ancient C code stacks, barely test them, and hope that
our castles of sand don\'t fall over, all so we can keep \"the same
version\" of a program to avoid changing it as much as possible.
Ironically this makes those stacks even worse because we\'ve developed
infinite numbers of bespoke barely tested packages that people rely on
daily.

To add more insult to this, most of this process is manual - humans
monitor mailing lists, and have to know what code needs what patch, and
when in what release streams. It\'s a monumental amount of human time
and labour involved to keep the sand castles standing. This manual
involvement is what leads to information overload, and maintainers
potentially missing security updates or releases that causes many
distribution packages to be outdated, missing patches, or vulnerable
more often than not. In other cases packages continue to be shipped that
are unmaintained or have no upstream, so any issues that may exist are
unknown or unresolved.

## Distribution Security

This means all of platform and distribution security comes to one
factor.

*A lot of manual human labour.*

It\'s is only because distributions have so many volunteers or paid
staff, that this entire system continues to progress to give the
illusion of security and reliability. When it fails, it fails silently.

Heartbleed really [dragged the poor state of C security into the
open](https://en.wikipedia.org/wiki/Heartbleed#Root_causes,_possible_lessons,_and_reactions)
, and it\'s still not been addressed.

When people say \"how can we secure docker/flatpak/Rust\" like we do
with distributions, I say: \"Do we really secure distributions at
all?\". We only have a veneer of best effort masquerading as a secure
supply chain.

## A Different Model \...

So let\'s look briefly at Rust and how you package it today (against
distribution maintainer advice).

Because it\'s staticly linked, each application must be rebuilt if a
library changes. Because the code comes from a central upstream, there
are automated tools to find security issues (like cargo audit). The
updates are pulled from the library as a whole working tested unit, and
then built into our application to to recieve further testing and
verification of the application as a whole singular functional unit.

These dependencies once can then be vendored to a tar (allowing offline
builds and some aspects of reproducability). This vendor.tar.gz is
placed into the source rpm along with the application source, and then
built.

There is a much stronger pipeline of assurances here! And to further aid
Rust\'s cause, because it is a memory *safe* language, it eliminates
most of the security issues that C is afflicted by, causing security
updates to be far fewer, and to often affect higher level or esoteric
situations. If you don\'t believe me, look at the low frequency, and low
severity [commits for the rust
advisory-db](https://github.com/RustSec/advisory-db/commits/master)

People have worried that because Rust is staticly linked we\'ll have to
rebuild it and update it continually to keep it secure - I\'d say
because it\'s Rust we\'ll have stronger guarantees at build that
security issues are less likely to exist and we won\'t have to ship
updates nearly as often as a C stack.

Another point to make is Rust libraries don\'t release patches - because
of Rust\'s stronger guarantees at compile time and through integrated
testing, people are less afraid of updates to versions. We are very
unlikely to see Rust releasing patches, rather than just shipping
\"updates\" to libraries and expecting you to update. Because these are
staticly linked, we don\'t have to worry about versions for other
libraries on the platform, we only need to assure the *application* is
currently working as intended. Because of the strong typing those
interfaces of those libraries has stronger compile time guarantees at
build time, meaning the issues around shared object versioning and
symbol/version mismatching simply don\'t exist - one of the key reasons
people became version change averse in the first place.

## So Why Not Package All The Things?

Many distribution packagers have been demanding a C-like model for Rust
and others ([remember, square peg, round
hole](../18/packaging_vendoring_and_how_it_s_changing.html)). This means
every single crate (library) is packaged, and then added to a set of
buildrequires for the application. When a crate updates, it triggers the
application to rebuild. When a security update for a library comes out,
it rebuilds etc.

This should sound familiar \... because it is. It\'s reinventing Cargo
in a clean-room.

RPM provides a way to manage dependencies. Cargo provides a way to
manage dependencies.

RPM provides a way to offline build sources. Cargo provides a way to
offline build sources.

RPM provides a way to patch sources. Cargo provides a way to update them
inplace - and patch if needed.

RPM provides a way to \... okay you get the point.

There is also a list of what we won\'t get from distribution packages -
remember distribution packages are the [C language packaging
system](../18/packaging_vendoring_and_how_it_s_changing.html)

We won\'t get the same level of attention to detail, innovation and
support as the upstream language tooling has. Simply put, users of the
language just won\'t use distribution packages (or toolchains, libraries
\...) in their workflows.

Distribution packages can\'t offer is the integration into tools like
cargo-audit for scanning for security issues - that needs still needs
Cargo, not RPM, meaning the RPM will need to emulate what Cargo does
exactly.

Using distribution packages means you have an untested pipeline that may
add more risks now. Developers won\'t use distribution packages -
they\'ll use cargo. Remember applications work best as they are tested
and developed - outside of that environment they are an unknown.

Finally, the distribution maintainers security proposition is to secure
our *libraries* - for distributions only. That\'s acting in self
interest. Cargo is offering a way to secure upstream so that everyone
benefits. That means less effort and less manual labour all around. And
secure libraries are not the full picture. Secure *applications* is what
matters.

The large concerning factor is the sheer amount of *human effort*. We
would spend hundreds if not thousands of hours to reinvent a functional
tool in a disengaged manner, just so that we can do things as they have
always been done in C - for the benefit of distributions individually
rather than languages upstream.

## What is the Point

Again - as a platform our role is to provide *applications* that people
can trust. The way we provide these applications is never going to be
one size fits all. Our objective isn\'t to secure \"this library\" or
\"that library\", it\'s to secure *applications* as a functional whole.
That means that companies shipping those applications, should hire
maintainers to work on those applications to secure their stacks.

Today I honestly think Rust has a better security and updating story
than C packages ever has, powered by automation and upstream
integration. Let\'s lean on that, contribute to it, and focus on
shipping applications instead of reinventing tools. We need to accept
our current model is focused on C, that developers have moved around
distribution packaging, and that we need to change our approach to
eliminate the large human risk factor that currently exists.

We can\'t keep looking to the models of the past, we need to start to
invest in new methods for the future.

Today, distributions should focus on supporting and distributing
*applications* and work with native language supply chains to enable
this.

Which is why I\'ll keep using cargo\'s tooling and auditing, and use
distribution packages as a delievery mechanism for those applications.

## What Could it Look Like?

We have a platform that updates as a whole (Fedora Atomic comes to mind
\...) with known snapshots that are tested and well known. This platform
has methods to run applications, and those applications are isolated
from each other, have their own libraries, and security audits.

And because there are now far fewer moving parts, quality is easier to
assert, understand, and security updates are far easier and faster, less
risky.

It certainly sounds a lot like what macOS and iOS have been doing with a
read-only base, and self-contained applications within that system.

