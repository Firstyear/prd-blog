+++
title = "Against Packaging Rust Crates"
date = 2021-02-16
slug = "2021-02-16-against_packaging_rust_crates"
# This is relative to the root!
aliases = [ "2021/02/16/against_packaging_rust_crates.html" ]
+++
# Against Packaging Rust Crates

Recently the discussion has once again come up around the notion of
packaging Rust crates as libraries in distributions. For example, taking
a library like [serde]{.title-ref} and packaging it to an RPM. While I
use RPM as the examples here it applies equally to other formats.

Proponents of crate packaging want all Rust applications to use the
\"distributions\" versions of a crate. This is to prevent \"vendoring\"
or \"bundling\". This is where an application (such as 389 Directory
Server) ships all of it\'s sources, as well as the sources of it\'s Rust
dependencies in a single archive. These sources may differ in version
from the bundled sources of other applications.

## \"Packaging crates is not reinventing Cargo\"

This is a common claim by advocates of crate packaging. However it is
easily disproved:

*If packaging is not reinventing cargo, I am free to use all of Cargo\'s
features without conflicts to distribution packaging.*

The reality is that packaging crates *is* reinventing Cargo - but
without all it\'s features. Common limitations are that Cargo\'s exact
version/less than requirements can not be used safely, or Cargo\'s
ability to apply patches or uses sources from specific git revisions can
not be used at all.

As a result, this hinders upstreams from using all the rich features
within Cargo to comply with distribution packaging limitations, or it
will cause the package to hit exceptions in policy and necesitate
vendoring anyway.

## \"You can vendor only in these exceptional cases \...\"

As noted, since packaging is reinventing Cargo, if you use features of
Cargo that are unsupported then you may be allowed to vendor depending
on the distributions policy. However, this raises some interesting
issues itself.

Assume I have been using distribution crates for a period of time - then
the upstream adds an exact version or git revision requirement to a
project or a dependency in my project. I now need to change my spec file
and tooling to use vendoring and all of the benefits of distribution
crates no longer exists (because you can not have any dependency in your
tree that has an exact version rule).

If the upstream \'un-does\' that change, then I need to roll back to
distribution crates since the project would no longer be covered by the
exemption.

This will create review delays and large amounts of administrative
overhead. It means pointless effort to swap between vendored and
distribution crates based on small upstream changes. This may cause
packagers to avoid certain versions or updates so that they do not need
to swap between distribution methods.

It\'s very likely that these \"exceptional\" cases will be very common,
meaning that vendoring will be occuring. This necesitates supporting
vendored applications in distribution packages.

## \"You don\'t need to package the universe\"

Many proponents say that they have \"already packaged most things\". For
example in 389 Directory Server of our 60 dependencies, only 2 were
missing in Fedora (2021-02). However this overlooks the fact that I do
not want to package those 2 other crates just to move forward. I want to
support 389 Directory Server the *application* not all of it\'s
dependencies in a distribution.

This is also before we come to larger rust projects, such as Kanidm that
has nearly 400 dependencies. The likelihood that many of them are
missing is high.

So you will need to package the universe. Maybe not all of it. But still
a lot of it. It\'s already hard enough to contribute packages to a
distribution. It becomes even harder when I need to submit 3, 10, or 100
more packages. It could be months before enough approvals were in place.
It\'s a staggering amount of administration and work, which will
discourage many contributors.

People have already contacted me to say that if they had to package
crates to distribution packages to contribute, they would give up and
walk away. We\'ve already lost future contributors.

Further to this Ruby, Python and many other languages today all
recommend language native tools such as rvm or virtualenv to avoid using
distribution packaged libraries.

Packages in distributions should exist as a vehicle to ship bundled
applications that are created from their language native tools.

## \"We will update your dependencies for you\"

A supposed benefit is that versions of crates in distributions will be
updated in the background according to semver rules.

If we had an exact version requirement (that was satisfiable), a silent
background update will cause this to no longer work - and will break the
application from building. This would necesitate one of:

-   A change to the Cargo.toml to remove the equality requirement - a
    requirement that may exist for good reason.
-   It will force the application to temporarily swap to vendoring
    instead.
-   The application will remain broken and unable to be updated until
    upstream resolves the need for the equality requirement.

Background updates also ignore the state of your Cargo.lock file by
removing it. A Cargo.lock file is recommended to be checked in with
binary applications in Rust, as evidence that shows \"here is an exact
set of dependencies that upstream has tested and verified as building
and working\".

To remove and ignore this file, means to remove the guarantees of
quality from an upstream.

It is unlikely that packagers will run the entire test suite of an
application to regain this confidence. They will \"apply the patch and
pray\" method - as they already do with other languages.

We can already see how background updates can have significant negative
consequences on application stability. FreeIPA has hundreds of
dependencies, and it\'s common that if any of them changes in small
ways, it can cause FreeIPA to fall over. This is not the fault of
FreeIPA - it\'s the fault of relying on so many small moving parts that
can change underneath your feet without warning. FreeIPA would strongly
benefit from vendoring to improve it\'s stability and quality.

Inversely, it can cause hesitation to updating libraries - since there
is now a risk of breaking other applications that depend on them. We do
not want people to be afraid of updates.

## \"We can respond to security issues\"

On the surface this is a strong argument, but in reality it does not
hold up. The security issues that face Rust are significantly different
to that which affect C. In C it may be viable to patch and update a
dynamic library to fix an issue. It saves time because you only need to
update and change one library to fix everything.

Security issues are much rarer in Rust. When they occur, you will have
to update and re-build all applications depending on the affected
library.

Since this rebuilding work has to occur, where the security fix is
applied is irrelevant. This frees us to apply the fixes in a different
way to how we approach C.

It is better to apply the fixes in a consistent and universal manner.
There *will* be applications that are vendored due to vendoring
exceptions, there is now duplicated work and different processes to
respond to both distribution crates, and vendored applications.

Instead all applications could be vendored, and tooling exists that
would examine the Cargo.toml to check for insecure versions
(RustSec/cargo-audit does this for example). The Cargo.toml\'s can be
patched, and applications tested and re-vendored. Even better is these
changes could easily then be forwarded to upstreams, allowing every
distribution and platform to benefit from the work.

In the cases that the upstream can not fix the issue, then Cargo\'s
native patching tooling can be used to supply fixes directly into
vendored sources for rare situations requiring it.

## \"Patching 20 vulnerable crates doesn\'t scale, we need to patch in one place!\"

A common response to the previous section is that the above process
won\'t scale as we need to find and patch 20 locations compared to just
one. It will take \"more human effort\".

Today, when a security fix comes out, every distribution\'s security
teams will have to be made aware of this. That means - OpenSUSE, Fedora,
Debian, Ubuntu, Gentoo, Arch, and many more groups all have to become
aware and respond. Then each of these projects security teams will work
with their maintainers to build and update these libraries. In the case
of SUSE and Red Hat this means that multiple developers may be involved,
quality engineering will be engaged to test these changes. Consumers of
that library will re-test their applications in some cases to ensure
there are no faults of the components they rely upon. This is all before
we approach the fact that each of these distributions have many
supported and released versions they likely need to maintain so this
process may be repeated for patching and testing multiple versions in
parallel.

In this process there are a few things to note:

-   There is a huge amount of human effort today to keep on top of
    security issues in our distributions.
-   Distributions tend to be isolated and can\'t share the work to
    resolve these - the changes to the rpm specs in SUSE won\'t help
    Debian for example.
-   Human error occurs in all of these layers causing security issues to
    go un-fixed or breaking a released application.

To suggest that rust and vendoring somehow makes this harder or more
time consuming is discounting the huge amount of time, skill, and effort
already put in by people to keep our C based distributions functioning
today.

Vendored Rust won\'t make this process easier or harder - it just
changes the nature of the effort we have to apply as maintainers and
distributions. It shifts our focus from \"how do we ensure this library
is secure\" to \"how do we ensure this *application* made from many
libraries is secure\". It allows further collaboration with upstreams to
be involved in the security update process, which ends up benefiting
*all* distributions.

## \"It doesn\'t duplicate effort\"

It does. By the very nature of both distribution libraries and vendored
applications needing to exist in a distribution, there will become
duplicated but seperate processes and policies to manage these, inspect,
and update these. This will create a need for tooling and supporting
both methods, which consumes time for many people.

People have already done the work to package and release libraries to
crates.io. Tools already exist to provide our dependencies and include
them in our applications. Why do we need to duplicate these features and
behaviours in distribution packages when Cargo already does this
correctly, and in a way that is universal and supported.

## Don\'t support distribution crates

I can\'t be any clearer than that. They consume excessive amounts of
contributor time, for little to no benefit, it detracts from simpler
language-native solutions for managing dependencies, distracts from
better language integration tooling being developed, it can introduce
application instability and bugs, and it creates high barriers to entry
for new contributors to distributions.

It doesn\'t have to be like this.

We need to stop thinking that Rust is like C. We have to accept that
language native tools are the interface people will want to use to
manage their libraries and distribute whole applications. We must use
our time more effectively as distributions.

If we focus on supporting vendored Rust applications, and developing our
infrastructure and tooling to support this, we *will* attract new
contributors by lowering barriers to entry, but we will also have a
stronger ability to contribute back to upstreams, and we will simplify
our building and packaging processes.

Today, tools like docker, podman, flatpak, snapd and others have proven
how bundling/vendoring, and a focus an applications can advance the
state of our ecosystems. We need to adopt the same ideas into
distributions. Our package managers should become a method to ship
applications - not libraries.

We need to focus our energy to supporting *applications* as self
contained units - not supporting the libraries that make them up.

## Edits

-   Released: 2021-02-16
-   EDIT: 2021-02-22 - improve clarity on some points, thanks to
    ftweedal.
-   EDIT: 2021-02-23 - due to a lot of comments regarding security
    updates, added an extra section to address how this scales.

