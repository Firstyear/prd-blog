+++
title = "Compiler Bootstrapping - Can We Trust Rust?"
date = 2021-05-12
slug = "2021-05-12-compiler_bootstrapping_can_we_trust_rust"
# This is relative to the root!
aliases = [ "2021/05/12/compiler_bootstrapping_can_we_trust_rust.html", "blog/html/2021/05/12/compiler_bootstrapping_can_we_trust_rust.html" ]
+++
# Compiler Bootstrapping - Can We Trust Rust?

Recently I have been doing a lot of work for SUSE with how we package
the Rust compiler. This process has been really interesting and
challenging, but like anything it\'s certainly provided a lot of time
for thought while [waiting](https://xkcd.com/303/) for my packages to
build.

The Rust package in OpenSUSE has two methods of building the compiler
internally in it\'s spec file.

-   1.  Use our previously packaged version of rustc from packages

-   2.  Bootstrap using the signed and prebuilt binaries provided by the
        rust project

## Bootstrapping

There are many advocates of bootstrapping and then self sustaining a
chain of compilers within a distribution. The roots of this come from
Ken Thompsons Turing Award speech known as [Reflections on trusting
trust](https://www.ece.cmu.edu/~ganger/712.fall02/papers/p761-thompson.pdf)
. This details the process in which a compiler can be backdoored, to
produce future backdoored compilers. This has been replicated by Manish
G. detailed in their [blog, Reflections on Rusting
Trust](https://manishearth.github.io/blog/2016/12/02/reflections-on-rusting-trust/)
where they successfully create a self-hosting backdoored rust compiler.

The process can be visualised as:

    ┌──────────────┐              ┌──────────────┐                             
    │  Backdoored  │              │   Trusted    │                             
    │   Sources    │──────┐       │   Sources    │──────┐                      
    │              │      │       │              │      │                      
    └──────────────┘      │       └──────────────┘      │                      
                          │                             │                      
    ┌──────────────┐      │       ┌──────────────┐      │      ┌──────────────┐
    │   Trusted    │      ▼       │  Backdoored  │      ▼      │  Backdoored  │
    │ Interpreter  │──Produces───▶│    Binary    ├──Produces──▶│    Binary    │
    │              │              │              │             │              │
    └──────────────┘              └──────────────┘             └──────────────┘

We can see that in this attack, even with a set of trusted compiler
sources, we can continue to produce a chain of backdoored binaries.

This has led to many people, and even groups such as
[Bootstrappable](https://www.bootstrappable.org/) promoting work to be
able to produce trusted chains from trusted sources, so that we can
assert a level of trust in our produced compiler binaries.

    ┌──────────────┐              ┌──────────────┐                             
    │   Trusted    │              │   Trusted    │                             
    │   Sources    │──────┐       │   Sources    │──────┐                      
    │              │      │       │              │      │                      
    └──────────────┘      │       └──────────────┘      │                      
                          │                             │                      
    ┌──────────────┐      │       ┌──────────────┐      │      ┌──────────────┐
    │   Trusted    │      ▼       │              │      ▼      │              │
    │ Interpreter  │──Produces───▶│Trusted Binary├──Produces──▶│Trusted Binary│
    │              │              │              │             │              │
    └──────────────┘              └──────────────┘             └──────────────┘

This process would continue forever to the right, where each trusted
binary is the result of trusted sources. This then ties into topics like
[reproducible builds](https://reproducible-builds.org/) which assert
that you can separately rebuild the sources and attain the same binary,
showing the process can not have been tampered with.

## But does it really work like that?

Outside of thought exercises, there is little evidence of these attacks
being carried out in reality.

Last year in 2020 we saw supply chain attacks such as the [Solarwinds
supply chain
attacks](https://en.wikipedia.org/wiki/SolarWinds#2019%E2%80%932020_supply_chain_attacks)
which was reported by
[Fireeye](https://www.fireeye.com/blog/products-and-services/2020/12/global-intrusion-campaign-leverages-software-supply-chain-compromise.html)
as *\"Inserting malicious code into legitimate software updates for the
Orion software that allow an attacker remote access into the victim's
environment\"*. What\'s really interesting here was that no compiler was
compromised in the process like our theoretical attack, but code was
simply inserted and then subsequently was released.

Tavis Ormandy in his blog [You don\'t need reproducible
builds](https://blog.cmpxchg8b.com/2020/07/you-dont-need-reproducible-builds.html)
covers supply chain security, and examines why reproducible builds are
not effective in the promises and claims they present. Importantly,
Tavis discusses how trivial it is to insert \"bugdoors\", or pieces of
code that are malicious and will not be found, and can potentially be
waved off as human error.

Today, we don\'t even need bugdoors, with Microsoft Security Response
Centre reporting that [70% of vulnerabilities are memory safety
issues](https://msrc-blog.microsoft.com/2019/07/16/a-proactive-approach-to-more-secure-code/).

No amount of reproducible builds or compiler bootstrapping chain can
shield us from the reality that attackers today will target the softest
area, and today that is security issues in our languages, and insecure
configuration of supply chain infrastructure.

We don\'t need backdoored compilers when we know that a security
critical piece of software written in C is still exposed to the network.

## But lets assume \...

Okay, so lets assume that backdoored compilers are a real risk for a
moment. We need to establish a few things first to create our secure
bootstrapping environment, and these requirements generally are
extremely difficult to meet.

We will need:

-   Trusted Interpreter
-   Trusted Sources

This is the foundation, having these two trusted entities that we can
use to begin the process. But what is \"trusted\"? How can we define
that these items are truly trusted?

One method could be to check the cryptographic signatures of the
released source code, to validate that it is \"what was released\", but
this does not mean that the source code is free from backdoors/bugdoors
which are the very thing we are attempting to shield ourselves from.

What would be truly required here is a detailed and complete audit of
all of the source code to these compilers, which would be a monumental
task in and of itself. So today instead, we do not perform source code
audits, and we *blindly trust* the providers of the source code as
legitimate and having provided us tamper-free source code. We assert
that blind trust through the validation of those cryptographic
signatures. We blindly trust that they have vetted every commit and line
of code, and they have not had their own source code supply chain
compromised in some way to provide us this \"trusted source\". This
gives us a relationship with the producers of that source, that they are
trustworthy and have performed vetting of code and their members with
privileges, that they will \"do the right thing\"™.

The second challenge is asserting trust in the interpreter. Where did
this binary come from? How was it built? Were it\'s sources trusted? As
one can imagine, this becomes a very deep rabbit hole when we want to
chase it, but in reality the approach taken by todays linux
distributions is that \"well we haven\'t been compromised to this point,
so I guess this one is okay\" and we yolo build with it. We then create
a root of trust in that one point in time, which then creates our
bootstrapping chain of trust for future builds of subsequent trusted
sources.

## So what about Rust?

Rust is interesting compared to something like C (clang/gcc), as the
rust project not only provides signed sources, they also provide signed
static binaries of their compiler. This is because unlike clang/gcc
which have very long release lifecycles, rust is released every six
weeks and to build version N of the compiler, requires version N or
N - 1. This allows people who have missed a version to easily skip ahead
without needing to build every intermediate version of the compiler.

A frequent complaint is the difficulty to package rust because any time
releases are missed, you must compile every intermediate version to
adhere to the bootstrappable guidelines and principles to created a more
\"trusted\" compiler.

But just like any other humans, in order to save time, when we miss a
version, we can use the rust language\'s provided signed binaries to
reset the chain, allowing us to miss versions of rust, or to re-package
older versions in some cases.

    ┌──────────────┐             ┌──────────────┐              
    │      │   Trusted    │             │   Trusted    │              
    Missed    │   Sources    │──────┐      │   Sources    │──────┐       
    Version!   │              │      │      │              │      │       
    │      └──────────────┘      │      └──────────────┘      │       
    │                            │                            │        
    ┌──────────────┐ │      ┌──────────────┐      │      ┌──────────────┐      │       
    │              │ │      │Trusted Binary│      ▼      │              │      ▼       
    │Trusted Binary│ │      │ (from rust)  ├──Produces──▶│Trusted Binary│──Produces───▶ ...
    │              │ │      │              │             │              │              
    └──────────────┘ │      └──────────────┘             └──────────────┘              

This process here is interesting because:

-   Using the signed binary from rust-lang is actually *faster* since we
    can skip one compiler rebuild cycle due to being the same version as
    the sources
-   It shows that the \"bootstrappable\" trust chain, does not actually
    matter since we frequently move our trust root to the released
    binary from rust, rather than building all intermediates

Given this process, we must ask, what value do we have from trying to
adhere to the bootstrappable principles with rust? We already root our
trust in the rust project, meaning that because we blindly trust the
sources *and* the static compiler, why would our resultant compiler be
any more \"trustworthy\" just because we were the ones who compiled it?

Beyond this the binaries that are issued by the rust project are used by
thousands of people every day through tools like rustup. In reality,
these have been proven time and time again that they are trusted to be
able to run on mass deployments, and that the rust project has the
ability and capability to respond to issues in their source code as well
as the binaries they provide. They certainly have earned the trust of
many people through this!

So why do we keep assuming both that we are somehow more trustworthy
than the rust project, but simultaneously they are fully trusted in the
artefacts they provide to us?

## Contradictions

It is this contradiction that has made me rethink the process that we
take to packaging rust in SUSE. I think we should bootstrap from
upstream rust every release because the rust project are in a far better
position to perform audits and respond to trust threats than part time
package maintainers that are commonly part of Linux distributions.

    │ ┌──────────────┐                              │ ┌──────────────┐                             
    │ │   Trusted    │                              │ │   Trusted    │                             
    │ │   Sources    │──────┐                       │ │   Sources    │──────┐                      
    │ │              │      │                       │ │              │      │                      
    │ └──────────────┘      │                       │ └──────────────┘      │                      
    │                       │                       │                       │                      
    │ ┌──────────────┐      │      ┌──────────────┐ │ ┌──────────────┐      │      ┌──────────────┐
    │ │Trusted Binary│      ▼      │              │ │ │Trusted Binary│      ▼      │              │
    │ │ (from rust)  ├──Produces──▶│Trusted Binary│ │ │ (from rust)  ├──Produces──▶│Trusted Binary│
    │ │              │             │              │ │ │              │             │              │
    │ └──────────────┘             └──────────────┘ │ └──────────────┘             └──────────────┘

We already fully trust the sources they release, and we already fully
trust their binary compiler releases. We can simplify our build process
(and speed it up!) by acknowledging this trust relationship exists,
rather than trying to continue to convince ourselves that we are somehow
\"more trusted\" than the rust project.

Also we must consider the reality of threats in the wild. Does all of
this work and discussions of who is more trusted really pay off and
defend us in reality? Or are we focused on these topics because they are
something that we can control and have opinions over, rather than
acknowledging the true complexity and dirtiness of security threats as
they truly exist today?

