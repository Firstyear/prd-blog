+++
title = "Where to start with linux authentication?"
date = 2022-08-24
slug = "2022-08-24-where_to_start_with_linux_authentication"
# This is relative to the root!
aliases = [ "2022/08/24/where_to_start_with_linux_authentication.html" ]
+++
# Where to start with linux authentication?

Recently I was asked about where someone could learn how linux
authentication works as a \"big picture\" and how all the parts
communicate. There aren\'t too many great resources on this sadly, so
I\'ve decided to write this up.

## Who \... are you?

The first component in linux identity is NSS or nsswitch (not to be
confused with NSS the cryptography library \... ). nsswitch (name
service switch) is exposed by glibc as a method to resolve uid/gid
numbers and names and to then access details of the account. nsswitch
can have \"modules\" that are stacked, where the first module with an
answer, provides the response.

An example of nsswitch.conf is:

    passwd: compat sss
    group:  compat sss
    shadow: compat sss

    hosts:      files mdns dns
    networks:   files dns

    services:   files usrfiles
    protocols:  files usrfiles
    rpc:        files usrfiles
    ethers:     files
    netmasks:   files
    netgroup:   files nis
    publickey:  files

    bootparams: files
    automount:  files nis
    aliases:    files

This is of the format \"service: module module \...\". An example here
is when a program does \"gethostbyname\" (a dns lookup) it accesses the
\"host\" service, then resolves via files (/etc/hosts) then mdns (aka
avahi, bonjour), and then dns.

The three lines that matter for identities though, are passwd, group,
and shadow. Most commonly you will use the [files]{.title-ref} module
which uses [/etc/passwd]{.title-ref} and [/etc/shadow]{.title-ref} to
satisfy requests. The [compat]{.title-ref} module is identical but with
some extra syntaxes allowed for NIS compatibility. Another common module
in nsswitch is [sss]{.title-ref} which accesses System Services Security
Daemon (SSSD). For my own IDM projects we use the [kanidm]{.title-ref}
nsswitch module.

You can test these with calls to [getent]{.title-ref} to see how
nsswitch is resolving some identity, for example:

    # getent passwd william
    william:x:654401105:654401105:William:/home/william:/bin/zsh
    # getent passwd 654401105
    william:x:654401105:654401105:William:/home/william:/bin/zsh

    # getent group william
    william:x:654401105:william
    # getent group 654401105
    william:x:654401105:william

Notice that both the uid (name) and uidnumber work to resolve the
identity.

These modules are dynamic libraries, and you can find them with:

    # ls -al /usr/lib[64]/libnss_*

When a process wishes to resole something with nsswitch, the calling
process (for example apache) calls to glibc which then loads these
dylibs at runtime, and they are executed and called. This is often why
the addition of new nsswitch modules in a distro is guarded and audited
because these modules can end up in *every* processes memory space! This
also has impacts on security as every module, and by inheritence every
process, may need access [/etc/passwd]{.title-ref} or the network to do
resolution of identities. Some modules improve this situation like sss,
and we will give that it\'s own section of this blog.

## Prove yourself!

If nsswitch answers \"who are you\", then pam (pluggable authentication
modules) is \"prove yourself\". It\'s what actually checks if your
credentials are valid and can login or not. Pam works by having
\"services\" that contact (you guessed it) modules. Most linux distros
have a folder (/etc/pam.d/) which contains all the service definitions
(there is a subtely different syntax in /etc/pam.conf which is not often
used in linux). So lets consider when you ssh to a machine. ssh contacts
pam and says \"I am the ssh service, can you please authorise this
identity for me\".

Because this is the \"ssh service\" pam will open the named config,
/etc/pam.d/SERVICE_NAME, in this case /etc/pam.d/ssh. This example is
taken from Fedora, because Fedora and RHEL are very common
distributions. Every distribution has their own \"tweaks\" and variants
to these files, which certainly helps to make the landscape even more
confusing.

    # cat /etc/pam.d/ssh
    #%PAM-1.0
    auth       include      system-auth
    account    include      system-auth
    password   include      system-auth
    session    optional     pam_keyinit.so revoke
    session    required     pam_limits.so
    session    include      system-auth

Note the \"include\" line that is repeated four times for auth, account,
password and session. These include system-auth, so lets look at that.

    # cat /etc/pam.d/system-auth

    auth        required                                     pam_env.so
    auth        required                                     pam_faildelay.so delay=2000000
    auth        [default=1 ignore=ignore success=ok]         pam_usertype.so isregular
    auth        [default=1 ignore=ignore success=ok]         pam_localuser.so
    auth        sufficient                                   pam_unix.so nullok
    auth        [default=1 ignore=ignore success=ok]         pam_usertype.so isregular
    auth        sufficient                                   pam_sss.so forward_pass
    auth        required                                     pam_deny.so

    account     required                                     pam_unix.so
    account     sufficient                                   pam_localuser.so
    account     sufficient                                   pam_usertype.so issystem
    account     [default=bad success=ok user_unknown=ignore] pam_sss.so
    account     required                                     pam_permit.so

    session     optional                                     pam_keyinit.so revoke
    session     required                                     pam_limits.so
    -session    optional                                     pam_systemd.so
    session     [success=1 default=ignore]                   pam_succeed_if.so service in crond quiet use_uid
    session     required                                     pam_unix.so
    session     optional                                     pam_sss.so

    password    requisite                                    pam_pwquality.so local_users_only
    password    sufficient                                   pam_unix.so yescrypt shadow nullok use_authtok
    password    sufficient                                   pam_sss.so use_authtok
    password    required                                     pam_deny.so

So, first we are in the \"auth phase\". This is where pam will check the
auth modules for your username and password (or other forms of
authentication) until a success is returned. We start at
[pam_env.so]{.title-ref}, that \"passes but isn\'t finished\" so we go
to faildelay etc. Each of these modules is consulted in turn, with the
result of the module, and the \"rule\" (required, sufficient or custom)
being smooshed together to create \"success and we are complete\",
\"success but keep going\", \"fail but keep going\" or \"fail and we are
complete\". In this example, the only modules that can actually
authenticate a user are [pam_unix.so]{.title-ref} and
[pam_sss.so]{.title-ref}, and if neither of them provide a \"success and
complete\", then [pam_deny.so]{.title-ref} is hit which always yields a
\"fail and complete\". This phase however has only verified your
*credentials*.

The second phase is the \"account phase\" which really should be
\"authorisation\". The modules are checked once again, to determine if
the module will allow or deny access to your user account to access this
system. Similar rules apply where each modules result and the rules of
the config combine to create a success/fail and continue/complete
result.

The third phase is the \"session phase\". Each pam module can influence
and setup things into the newly spawned session of the user. An example
here is you can see [pam_limits.so]{.title-ref} which is what applies
cpu/memory/filedescriptor limits to the created shell session.

The fourth module is \"password\". This isn\'t actually used in the
authentication process - this stack is called when you issue the
\"passwd\" command to update the users password. Each module is
consulted in turn for knowledge of the account, and if they are able to
alter the credentials. If this fails you will recieve a generic
\"authentication token manipulation error\", which really just means
\"some module in the stack failed, but we wont tell you which\".

Again, these modules are all dylibs and can be found commonly in
[/usr/lib64/security/]{.title-ref}. Just like nsswitch, applications
that use pam are linked to [libpam.so]{.title-ref}, which inturn with
load modules from [/usr/lib64/security/]{.title-ref} at runtime. Given
that [/etc/shadow]{.title-ref} is root-read-only, and anything that
wants to verify passwords needs to \... read this file, this generally
means that any pam module is effectively running in root memory space on
any system. Once again, this is why distributions carefully audit and
control what packages can supply a pam module given the high level of
access these require. Once again, because of how pam modules work this
also generally means that the process will need network access to call
out to external identity services depending on the pam modules in use.

## What about that network auth?

Now that we\'ve covered the foundations of how processes and daemons
will find details of a user and verify their credentials, lets look at
SSSD which is a specific implementation of an identity resolving daemon.

As mentioned, both nsswitch and pam have the limitation that the dylibs
run in the context of the calling application, which often meant in the
past with modules like [pam_ldap.so]{.title-ref} would be running in the
process space of root applications, requiring network access and having
to parse asn.1 (a library commonly used for remote code execution that
sometimes has the side effect of encoding and decoding binary
structures).

    ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐                        
      root: uid 0             │                  
    │                   │                        
                              │                  
    │  ┌─────────────┐  │         ┌─────────────┐
       │             │        │   │             │
    │  │             │  │         │             │
       │             │        │   │             │
    │  │    SSHD     │──┼────────▶│    LDAP     │
       │             │        │   │             │
    │  │             │  │         │             │
       │             │        │   │             │
    │  └─────────────┘  │         └─────────────┘
                              │                  
    │                   │ Network                
                              │                  
    └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘                        

SSSD changes this by having a daemon running locally which can be
accessed by a unix socket. This allows the pam and nsswitch modules to
be thin veneers with minimal functionality and surface area, who then
contact an isolated daemon that does the majority of the work. This has
a ton of security benefits not limited to reducing the need for the root
process to decode untrusted input from the network.

    ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐      ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐                         
      root: uid 0                sssd: uid 123            │                  
    │                   │      │                   │                         
                                                          │                  
    │  ┌─────────────┐  │      │  ┌─────────────┐  │          ┌─────────────┐
       │             │            │             │         │   │             │
    │  │             │  │      │  │             │  │          │             │
       │             │            │             │         │   │             │
    │  │    SSHD     │──┼──────┼─▶│    SSSD     │──┼─────────▶│    LDAP     │
       │             │            │             │         │   │             │
    │  │             │  │      │  │             │  │          │             │
       │             │            │             │         │   │             │
    │  └─────────────┘  │      │  └─────────────┘  │          └─────────────┘
                                                          │                  
    │                   │      │                   │  Network                
                                                          │                  
    └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘      └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘                         

Another major benefit of this is that SSSD can cache responses from the
network in a secure way, allowing the client to resolve identities when
offline. This even includes caching passwords!

As a result this is why SSSD ends up taking on so much surface area of
authentication on many distros today. With a thicc local daemon which
does the more complicated tasks and work to actually identify and
resolve users, and the ability to use a variety of authentication
backends it is becoming widely deployed and will displace pam_ldap and
pam_krb5 in the majority of network based authentication scenarioes.

## Inside the beast

SSSD is internally built from a combination of parts that coordinate.
It\'s useful to know how to debug these if something goes wrong:

    # /etc/sssd/sssd.conf

    //change the log level of communication between the pam module and the sssd daemon
    [pam]
    debug_level = ...

    // change the log level of communication between the nsswitch module and the sssd daemon
    [nss]
    debug_level = ...

    // change the log level of processing the operations that relate to this authentication provider domain ```
    [domain/AD]
    debug_level = ...

Now we\'ve just introduced a new concept - a SSSD domain. This is
different to a \"domain\" per Active Directory. A SSSD domain is just
\"an authentication provider\". A single instance of SSSD can consume
identities from multiple domains at the same time. In a majority of
configurations however, a single domain is configured.

In the majority of cases if you have an issue with SSSD it is likely to
be in the domain section so this is always the first place to look for
debugging.

Each domain can configure different providers of the \"identity\",
\"authentication\", \"access\" and \"chpass\". For example a
configuration in [/etc/sssd/sssd.conf]{.title-ref}

    [domain/default]
    id_provider = ldap
    auth_provider = ldap
    access_provider = ldap
    chpass_provider = ldap

The [id_provider]{.title-ref} is the backend of the domain that resolves
names and uid/gid numbers to identities.

The [auth_provider]{.title-ref} is the backend that validates the
password of an identity.

The [access_provider]{.title-ref} is the backend that describes if an
identity is allowed to access this system or not.

The [chpass_provider]{.title-ref} is the backend that password changes
and updates are sent to.

As you can see there is a lot of flexibility in this design. For example
you could use krb5 as the auth provider, but send password changes via
ldap.

Because of this design SSSD links to and consumes identity management
libraries from many other sources such as samba (ad), ldap and kerberos.
This means in some limited cases you may need to apply debugging
knowledge from the relevant backend to solve an issue in SSSD.

## Common Issues

### Performance

In some cases SSSD can be very slow to resolve a user/group on first
login, but then becomes \"faster\" after the login completes. In
addition sometimes you may see excessive or high query load on an LDAP
server during authentication as well. This is due to an issue with how
groups and users are resolved where to resolve a user, you need to
resolve it\'s group memberships. Then each group is resolved, but for
unix-tools to display a group you need to resolve it\'s members. Of
course it\'s members are users and these need resolving \... I hope you
can see this is recursive. In some worst cases this can lead to a
situation where when a single user logs on, the full LDAP/AD directory
is enumerated, which can take minutes in some cases.

To prevent this set:

    ignore_group_members = False

This prevents groups resolving their members. As a results groups appear
to have no members, but users will always display the groups they are
member-of. Since almost all applications work using this \"member-of\"
pattern, there are very few negative outcomes from this.

### Cache Clearing

SSSD has a local cache of responses from network services. It ships with
a cache management tool [sss_cache]{.title-ref}. This allows records to
be marked as [invalid]{.title-ref} so that a reload from the network
occurs as soon as possible.

There are two flaws here. In some cases this appears to have \"no
effect\" where invalid records continue to be served. In addition, the
[sss_cache]{.title-ref} tool when called with [-E]{.title-ref} for
everything, does not always actually invalidate everything.

A common source of advice in these cases is to stop sssd, remove all the
content under [/var/lib/sss/db]{.title-ref} (but not the folder itself)
and then start sssd.

### Debugging Kerberos

Kerberos can be notoriously hard to debug. This is because it doesn\'t
have a real verbose/debug mode, at least not obviously. To get debug
output you need to set an environment variable.

    KRB5_TRACE=/dev/stderr kinit user@domain

This works on *any* proccess that links to kerberos, so it works on
389-ds, sssd, and many other applications so you can use this to trace
what\'s going wrong.

## Conclusion

That\'s all for now, I\'ll probably keep updating this post over time :)

