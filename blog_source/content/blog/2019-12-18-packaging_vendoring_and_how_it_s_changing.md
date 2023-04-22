+++
title = "Packaging, Vendoring, and How It's Changing"
date = 2019-12-18
slug = "2019-12-18-packaging_vendoring_and_how_it_s_changing"
# This is relative to the root!
aliases = [ "2019/12/18/packaging_vendoring_and_how_it_s_changing.html", "blog/html/2019/12/18/packaging_vendoring_and_how_it_s_changing.html" ]
+++
# Packaging, Vendoring, and How It\'s Changing

In today\'s thoughts, I was considering packaging for platforms like
opensuse or other distributions and how that interacts with language
based packaging tools. This is a complex and \... difficult topic, so
I\'ll start with my summary:

Today, distributions should focus on supporting and distributing
*applications* and work with native language supply chains to enable
this.

## Distribution Packaging

Let\'s start by clarifying what distribution packaging is. This is your
linux or platforms method of distributing it\'s programs libraries. For
our discussion we really only care about linux so say suse or fedora
here. How macOS or FreeBSD deal with this is quite different.

Now these distribution packages are built to support certain workflows
and end goals. Many open source C projects release their source code in
varying states, perhaps also patches to improve or fix issues. These
code are then put into packages, dependencies between them established
due to dynamic linking, they are signed for verification purposes and
then shipped.

This process is really optimised for C applications. C has been the
\"system language\" for many decades now, and so we can really see these
features designed to promote - and fill in gaps - for these
applications.

For example, C applications are dynamically linked. Because of this it
encourages package maintainers to \"split\" applications into smaller
units that can have shared elements. An example that I know is openldap
which may be a single source tree, but often is packaged to multiple
parts such as the libldap.so, lmdb, openldap-client applications, it\'s
server binary, and probably others. The package maintainer is used to
taking their scalpels and carefully slicing sources into elegant
packages that can minimise how many things are installed to what is
\"just needed\".

We also see other behaviours where C shared objects have \"versions\",
which means you can install multiple versions of them at once and
programs declare in their headers which library versions they want to
consume. This means a distribution package can have many versions of the
same thing installed!

This in mind, the linking is simplistic and naive. If a shared object
symbol doesn\'t exist, or you don\'t give it the \"right arguments\" via
a weak-compile time contract, it\'s likely bad things (tm) will happen.
So for this, distribution packaging provides the stronger assertions
about \"this program requires that library version\".

As well, in the past the internet was a more \... wild place, where TLS
wasn\'t really widely used. This meant that to gain strong assertions
about the source of a package *and* that it had not been tampered, tools
like GPG were used.

## What about Ruby or Python?

Ruby and Python are very different languages compared to C though. They
don\'t have information in their programs about what versions of
software they require, and how they mesh together. Both languages are
interpreted, and simply \"import library\" by name, searching a
filesystem path for a library matching *regardless of it\'s version*.
Python then just loads in that library as source straight to the running
vm.

It\'s already apparent how we\'ll run into issues here. What if we have
a library \"foo\" that has a different function interface between
version 1 and version 2? Python applications only request access to
\"foo\", not the version, so what happens if the wrong version is found?
What if it\'s not found?

Some features here are pretty useful from the \"distribution package\"
though. Allowing these dynamic tools to have their dependencies
requested from the \"package\", and having the package integrity checked
for them.

But overtime, conflicts started, and issues arose. A real turning point
was ruby in debian/ubuntu where debian package maintainers (who are used
to C) brought out the scalpel and attempted to slice ruby down to
\"parts\" that could be reused form a C mindset. This led to a
combinations of packages that didn\'t make sense (rubygems minus TLS,
but rubygems requires https), which really disrupted the communities.

Another issue was these languages as they grew in popularity had
different projects requiring *different* versions of libraries - which
as before we mentioned isn\'t possible beside library search path
manipulations which is frankly user hostile.

These issues (and more) eventually caused these communities as a whole
to *stop recommending* distribution packages.

So put this history in context. We have Ruby (1995) and Python (1990),
which both decided to avoid distribution packages with their own tools
aka rubygems (2004) and pip (2011), as well as tools to manage multiple
parallel environments (rvm, virtualenv) that were per-application.

## New kids on the block

Since then I would say three languages have risen to importance and
learnt from the experiences of Ruby - This is Javascript (npm/node), Go
and Rust.

Rust went further than Ruby and Python and embedded distribution of
libraries into it\'s build tools from an early date with Cargo. As Rust
is staticly linked (libraries are build into the final binary, rather
than being dynamicly loaded), this moves all dependency management to
build time - which prevents runtime library conflict. And because Cargo
is involved and controls all the paths, it can do things such as having
multiple versions available in a single build for different components
and coordinating all these elements.

Now to hop back to npm/js. This ecosystem introduced a new concept -
micro-dependencies. This happened because javascript doesn\'t have dead
code elimination. So if given a large utility library, and you call one
function out of 100, you still have to ship all 99 unused ones. This
means they needed a way to manage and distribute hundreds, if not
thousands of tiny libraries, each that did \"one thing\" so that you
pulled in \"exactly\" the minimum required (that\'s not how it turned
out \... but it was the intent).

Rust also has inherited a similar culture - not to the same extreme as
npm because Rust DOES have dead code elimination, but still enough that
my concread library with 3 dependencies pulls in 32 dependencies, and
kanidm from it\'s 30 dependencies, pulls in 365 into it\'s graph.

But in a way this also doesn\'t matter - Rust enforces strong typing at
compile time, so changes in libraries are detected before a release (not
after like in C, or dynamic languages), and those versions at build are
used in production due to the static linking.

This has led to a great challenge is distribution packaging for Rust -
there are so many \"libraries\" that to package them all would be a
monumental piece of human effort, time, and work.

But once again, we see the distribution maintainers, scalpel in hand, a
shine in their eyes looking and thinking \"excellent, time to package
365 libraries \...\". In the name of a \"supply chain\" and adding
\"security\".

We have to ask though, is there really *value* of spending all this time
to package 365 libraries when Rust functions so differently?

## What are you getting at here?

To put it clearly - distribution packaging isn\'t a \"higher\" form of
distributing software. Distribution packages are not the one-true
solution to distribute software. It doesn\'t magically enable
\"security\". Distribution Packaging *is* the C language source and
binary distribution mechanism - and for that it works great!

Now that we can frame it like this we can see *why* there are so many
challenges when we attempt to package Rust, Python or friends in rpms.

Rust isn\'t C. We can\'t think about Rust like C. We can\'t secure Rust
like C.

Python isn\'t C. We can\'t think about Python like C. We can\'t secure
Python like C.

These languages all have their own quirks, behaviours, flaws, benefits,
and goals. They need to be distributed in unique ways appropriate to
those languages.

## An example of the mismatch

To help drive this home, I want to bring up FreeIPA. FreeIPA has a lot
of challenges in packaging due to it\'s *huge* number of C, Python and
Java dependencies. Recently on twitter it was annouced that \"FreeIPA
has been packaged for debian\" as the last barrier (being dogtag/java)
was overcome to package the hundreds of required dependencies.

The inevitable outcome of debian now packaging FreeIPA will be:

-   FreeIPA will break in some future event as one of the python or java
    libraries was changed in a way that was not expected by the
    developers or package maintainers.
-   Other applications may be \"held back\" from updating at risk/fear
    of breaking FreeIPA which stifles innovation in the java/python
    ecosystems surrounding.

It won\'t be the fault of FreeIPA. It won\'t be the fault of the debian
maintainers. It will be that we are shoving square applications through
round C shaped holes and hoping it works.

## So what does matter?

It doesn\'t matter if it\'s Kanidm, FreeIPA, or 389-ds. End users want
to consume *applications*. How that application is developed, built and
distributed is a secondary concern, and many people will go their whole
lives never knowing how this process works.

We need to stop focusing on packaging *libraries* and start to focus on
how we distribute *applications*.

This is why projects like docker and flatpak have surprised traditional
packaging advocates. These tools are about how we ship *applications*,
and their build and supply chains are separated from these.

This is why I have really started to advocate and say:

Today, distributions should focus on supporting and distributing
*applications* and work with native language supply chains to enable
this.

Only we accept this shift, we can start to find value in distributions
again as sources of trusted applications, and how we see the
distribution as an application platform rather than a collection of tiny
libraries.

The risk of not doing this is alienating communities (again) from being
involved in our platforms.

## Follow Up

There have been some major comments since:

First, there is now a C package manager named [conan](https://conan.io/)
. I have no experience with this tool, so at a distance I can only
assume it works well for what it does. However it was noted it\'s not
gained much popularity, likely due to the fact that distro packages are
the current C language distribution channels.

The second was about the security components of distribution packaging
and this - that topic is so long I\'ve written [another
post](../19/packaging_and_the_security_proposition.html) about the topic
instead, to try and keep this post focused on the topic.

Finally, The Fedora Modularity effort is trying to deal with some of
these issues - that modules, aka applications have different cadences
and requirements, and those modules can move more freely from the base
OS.

Some of the challenges have been [explored by
LWN](https://lwn.net/Articles/805180/) and it\'s worth reading. But I
think the underlying issue is that again we are approaching things in a
way that may not align with reality - people are looking at modules as
libraries, not applications which is causing things to go sideways. And
when those modules are installed, they aren\'t [isolated from each
other](https://lwn.net/ml/fedora-devel/4040208.GuUW4P68lE@marvin.jharris.pw/)
, meaning we are back to square one, with a system designed only for C.
People are [starting to see
that](https://lwn.net/ml/fedora-devel/CAB-QmhSdQ+Gwuf6gnLaiziMY+nxNgTSFaUyzRuJqO6sN7_6wzw@mail.gmail.com/)
but the key point is continually missed - that modularity should be
about *applications* and their isolation not about *multiple library
versions*.

