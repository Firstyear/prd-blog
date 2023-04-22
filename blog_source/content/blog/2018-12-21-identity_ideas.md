+++
title = "Identity ideas ..."
date = 2018-12-21
slug = "2018-12-21-identity_ideas"
# This is relative to the root!
aliases = [ "2018/12/21/identity_ideas.html" ]
+++
# Identity ideas \...

I\'ve been meaning to write this post for a long time. Taking half a
year away from the 389-ds team, and exploring a lot of ideas from other
projects has led me to come up with some really interesting ideas about
what we do well, and what we don\'t. I feel like this blog could be
divisive, as I really think that for our services to stay relevant we
need to make changes that really change our own identity - so that we
can better represent yours.

So strap in, this is going to be long \...

## What\'s currently on the market

Right now the market for identity has two extremes. At one end we have
the legacy \"create your own\" systems, that are build on technologies
like LDAP and Kerberos. I\'m thinking about things like 389 Directory
Server, OpenLDAP, Active Directory, FreeIPA and more. These all happen
to be constrained heavily by complexity, fragility, and administrative
workload. You need to spend months to learn these and even still, you
will make mistakes and there will be problems.

At the other end we have hosted \"Identity as a Service\" options like
Azure AD and Auth0. These have very intelligently, unbound themself from
legacy, and tend to offer HTTP apis, 2fa and other features that \"just
work\". But they are all in the cloud, and outside your control.

But there is nothing in the middle. There is no option that \"just
works\", supports modern standards, and is unhindered by legacy that you
can self deploy with minimal administrative fuss - or years of
experience.

## What do I like from 389?

-   Replication

The replication system is extremely robust, and has passed many complex
tests for cases of eventual consistency correctness. It\'s very rare to
hear of any kind of data corruption or loss within our replication
system, and that\'s testament to the great work of people who spent
years looking at the topic.

-   Performance

We aren\'t as fast as OpenLDAP is 1 vs 1 server, but our replication
scalability is much higher, where in any size of MMR or read-only
replica topology, we have higher horizontal scaling, nearly linear based
on server additions. If you want to run a cloud scale replicated
database, we scale to it (and people already do this!).

-   Stability

Our server stability is well known with administrators, and honestly is
a huge selling point. We see servers that only go down when
administrators are performing upgrades. Our work with sanitising tools
and the careful eyes of the team has ensured our code base is reliable
and solid. Having extensive tests and amazing dedicated quality
engineers also goes a long way.

-   Feature rich

There are a lot of features I really like, and are really useful as an
admin deploying this service. Things like memberof (which is actually a
group resolution cache when you think about it \...), automember, online
backup, unique attribute enforcement, dereferencing, and more.

-   The team

We have a wonderful team of really smart people, all of whom are caring
and want to advance the state of identity management. Not only do they
want to keep up with technical changes and excellence, they are
listening to and want to improve our social awareness of identity
management.

## Pain Points

-   C

Because DS is written in C, it\'s risky and difficult to make changes.
People constantly make mistakes that introduce unsafety (even myself),
and worse. No amount of tooling or intelligence can take away the fact
that C is just hard to use, and people need to be perfect (people are
not perfect!) and today we have better tools. We can not spend our time
chasing our tails on pointless issues that C creates, when we should be
doing better things.

-   Everything about dynamic admin, config, and plugins is hard and
    can\'t scale

Because we need to maintain consistency through operations from start to
end but we also allow changing config, plugins, and more during the
servers operation the current locking design just doesn\'t scale. It\'s
also not 100% safe either as the values are changed by atomics, not
managed by transactions. We could use copy-on-write for this, but why?
Config should be managed by tools like ansible, but today our dynamic
config and plugins is both a performance over head and an admin overhead
because we exclude best practice tools and have to spend a large amount
of time to maintain consistent data when we shouldn\'t need to. Less
features is less support overhead on us, and simpler to test and assert
quality and correct behaviour.

-   Plugins to address shortfalls, but a bit odd.

We have all these features to address issues, but they all do it \...
kind of the odd way. Managed Entries creates user private groups on
object creation. But the problem is \"unix requires a private group\"
and \"ldap schema doesn\'t allow a user to be a group and user at the
same time\". So the answer is actually to create a new objectClass that
let\'s a user ALSO be it\'s own UPG, not \"create an object that links
to the user\". (Or have a client generate the group from user attributes
but we shouldn\'t shift responsibility to the client.)

Distributed Numeric Assignment is based on the AD rid model, but it\'s
all about \"how can we assign a value to a user that\'s unique?\". We
already have a way to do this, in the UUID, so why not derive the
UID/GID from the UUID. This means there is no complex inter-server
communication, pooling, just simple isolated functionality.

We have lots of features that just are a bit complex, and could have
been made simpler, that now we have to support, and can\'t change to
make them better. If we rolled a new \"fixed\" version, we would then
have to support both because projects like FreeIPA aren\'t going to just
change over.

-   client tools are controlled by others and complex (sssd, openldap)

Every tool for dealing with ldap is really confusing and arcane. They
all have wild (unhelpful) defaults, and generally this scares people
off. I took months of work to get a working ldap server in the past.
Why? It\'s 2018, things need to \"just work\". Our tools should \"just
work\". Why should I need to hand edit pam? Why do I need to set weird
options in SSSD.conf? All of this makes the whole experience poor.

We are making client tools that can help (to an extent), but they are
really limited to system administration and they aren\'t \"generic\"
tools for every possible configuration that exists. So at some point
people will still find a limit where they have to touch ldap commands. A
common request is a simple to use web portal for password resets, which
today only really exists in FreeIPA, and that limits it\'s application
already.

-   hard to change legacy

It\'s really hard to make code changes because our surface area is so
broad and the many use cases means that we risk breakage every time we
do. I have even broken customer deployments like this. It\'s almost
impossible to get away from, and that holds us back because it means we
are scared to make changes because we have to support the 1 million
existing work flows. To add another is more support risk.

Many deployments use legacy schema elements that holds us back, ranging
from the inet types, schema that enforces a first/last name, schema that
won\'t express users + groups in a simple away. It\'s hard to ask people
to just up and migrate their data, and even if we wanted too, ldap
allows too much freedom so we are more likely to break data, than
migrate it correctly if we tried.

This holds us back from technical changes, and social representation
changes. People are more likely to engage with a large migrational
change, than an incremental change that disturbs their current workflow
(IE moving from on prem to cloud, rather than invest in smaller
iterative changes to make their local solutions better).

-   ACI\'s are really complex

389\'s access controls are good because they are in the tree and
replicated, but bad because the syntax is awful, complex, and has lots
of traps and complexity. Even I need to look up how to write them when I
have to. This is not good for a project that has such deep security
concerns, where your ACI\'s can look correct but actually expose all
your data to risks.

-   LDAP as a protocol is like an 90\'s drug experience

LDAP may be the lingua franca of authentication, but it\'s complex, hard
to use and hard to write implementations for. That\'s why in opensource
we have a monoculture of using the openldap client libraries because *no
one can work out how to write a standalone library*. Layer on top the
complexity of the object and naming model, and we have a situation where
no one wants to interact with LDAP and rather keeps it at arm length.

It\'s going to be extremely hard to move forward here, because the
community is so fragmented and small, and the working groups dispersed
that the idea of LDAPv4 is a dream that no one should pursue, even
though it\'s desperately needed.

-   TLS

TLS is great. NSS databases and tools are not.

-   GSSAPI + SSO

GSSAPI and Kerberos are a piece of legacy that we just can\'t escape
from. They are a curse almost, and one we need to break away from as
it\'s completely unusable (even if it what it promises is amazing). We
need to do better.

That and SSO allows loads of attacks to proceed, where we actually want
isolated token auth with limited access scopes \...

## What could we offer

-   Web application as a first class consumer.

People want web portals for their clients, and they want to be able to
use web applications as the consumer of authentication. The HTTP
protocols must be the first class integration point for anything in
identity management today. This means using things like OAUTH/OIDC.

-   Systems security as a first class consumer.

Administrators still need to SSH to machines, and people still need
their systems to have identities running on them. Having pam/nsswitch
modules is a very major requirement, where those modules have to be
fast, simple, and work correctly. Users should \"imply\" a private
group, and UID/GID should by dynamic from UUID (or admins can override
it).

-   2FA/u2f/TOTP.

Multi-factor auth is here (not coming, here), and we are behind the
game. We already have Apple and MS pushing for webauthn in their
devices. We need to be there for these standards to work, and to support
the next authentication tool after that.

-   Good RADIUS integration.

RADIUS is not going away, and is important in education providers and
business networks, so RADIUS must \"just work\". Importantly, this means
mschapv2 which is the universal default for all clients to operate with,
which means nthash.

However, we can make the nthash unlinked from your normal password, so
you can then have wifi password and a seperate loging password. We could
even generate an NTHash containing the TOTP token for more high security
environments.

-   better data structure (flat, defined by object types).

The tree structure of LDAP is confusing, but a flatter structure is
easier to manage and understand. We can use ideas from kubernetes like
tags/labels which can be used to provide certain controls and filtering
capabilities for searches and access profiles to apply to.

-   structured logging, with in built performance profiling.

Being able to diagnose why an operation is slow is critical and having
structured logs with profiling information is key to allowing admins and
developers to resolve performance issues at scale. It\'s also critical
to have auditing of every single change made in the system, including
internal changes that occur during operations.

-   access profiles with auditing capability.

Access profiles that express what you can access, and how. Easier to
audit, generate, and should be tightly linked to group membership for
real RBAC style capabilities.

-   transactions by allowing batch operations.

LDAP wants to provide a transaction system over a set of operations, but
that may cause performance issues on write paths. Instead, why not allow
submission of batches of changes that all must occur \"at the same
time\" or \"none\". This is faster network wise, protocol wise, and
simpler for a server to implement.

## What\'s next then \...

Instead of fixing what we have, why not take the best of what we have,
and offer something new in parallel? Start a new front end that speaks
in an accessible way, that has modern structures, and has learnt from
the lessons of the past? We can build it to standalone, or proxy from
the robust core of 389 Directory Server allowing migration paths, but
eschew the pain of trying to bring people to the modern world. We can
offer something unique, an open source identity system that\'s easy to
use, fast, secure, that you can run on your terms, or in the cloud.

This parallel project seems like a good idea \... I wonder what to name
it \...

