+++
title = "Meaningful 2fa on modern linux"
date = 2019-02-12
slug = "2019-02-12-meaningful_2fa_on_modern_linux"
# This is relative to the root!
aliases = [ "2019/02/12/meaningful_2fa_on_modern_linux.html" ]
+++
# Meaningful 2fa on modern linux

Recently I heard of someone asking the question:

\"I have an AD environment connected with \<product\> IDM. I want to
have 2fa/mfa to my linux machines for ssh, that works when the central
servers are offline. What\'s the best way to achieve this?\"

Today I\'m going to break this down - but the conclusion for the lazy
is:

*This is not realistically possible today: use ssh keys with ldap
distribution, and mfa on the workstations, with full disk encryption*.

## Background

So there are a few parts here. AD is for intents and purposes an LDAP
server. The \<product\> is also an LDAP server, that syncs to AD. We
don\'t care if that\'s 389-ds, freeipa or vendor solution. The results
are basically the same.

Now the linux auth stack is, and will always use pam for the
authentication, and nsswitch for user id lookups. Today, we assume that
most people run sssd, but pam modules for different options are
possible.

There are a stack of possible options, and they all have various flaws.

-   FreeIPA + 2fa
-   PAM TOTP modules
-   PAM radius to a TOTP server
-   Smartcards

## FreeIPA + 2fa

Now this is the one most IDM people would throw out. The issue here is
the person already has AD and a vendor product. They don\'t need a third
solution.

Next is the fact that FreeIPA stores the TOTP in the LDAP, which means
FreeIPA has to be online for it to work. So this is eliminated by the
\"central servers offline\" requirement.

## PAM radius to TOTP server

Same as above: An extra product, and you have a source of truth that can
go down.

## PAM TOTP module on hosts

Okay, even if you can get this to scale, you need to send the private
seed material of every TOTP device that could login to the machine, to
every machine. That means *any* compromise, compromises every TOTP token
on your network. Bad place to be in.

## Smartcards

Are notoriously difficult to have functional, let alone with SSH. Don\'t
bother. (Where the Smartcard does TLS auth to the SSH server this is.)

## Come on William, why are you so doom and gloom!

Lets back up for a second and think about what we we are trying to
prevent by having mfa at all. We want to prevent single factor
compromise from having a large impact *and* we want to prevent brute
force attacks. (There are probably more reasons, but these are the ones
I\'ll focus on).

So the best answer: Use mfa on the workstation (password + totp), then
use ssh keys to the hosts.

This means the target of the attack is small, and the workstation can be
protected by things like full disk encryption and group policy. To sudo
on the host you still need the password. This makes sudo MFA to root as
you need something know, and something you have.

If you are extra conscious you can put your ssh keys on smartcards. This
works on linux and osx workstations with yubikeys as I am aware.
Apparently you can have ssh keys in TPM, which would give you tighter
hardware binding, but I don\'t know how to achieve this (yet).

To make all this better, you can distributed your ssh public keys in
ldap, which means you gain the benefits of LDAP account
locking/revocation, you can remove the keys instantly if they are
breached, and you have very little admin overhead to configuration of
this service on the linux server side. Think about how easy onboarding
is if you only need to put your ssh key in one place and it works on
every server! Let alone shutting down a compromised account: lock it in
one place, and they are denied access to every server.

SSSD as the LDAP client on the server can also cache the passwords
(hashed) and the ssh public keys, which means a disconnected client will
still be able to be authenticated to.

At this point, because you have ssh key auth working, you could even
*deny* password auth as an option in ssh altogether, eliminating an
entire class of bruteforce vectors.

For bonus marks: You can use AD as the generic LDAP server that stores
your SSH keys. No additional vendor products needed, you already have
everything required today, for free. Everyone loves free.

## Conclusion

If you want strong, offline capable, distributed mfa on linux servers,
the only choice today is LDAP with SSH key distribution.

Want to know more? This blog contains how-tos on SSH key distribution
for AD, SSH keys on smartcards, and how to configure SSSD to use SSH
keys from LDAP.

