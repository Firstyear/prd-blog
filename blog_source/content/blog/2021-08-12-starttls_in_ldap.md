+++
title = "StartTLS in LDAP"
date = 2021-08-12
slug = "2021-08-12-starttls_in_ldap"
# This is relative to the root!
aliases = [ "2021/08/12/starttls_in_ldap.html" ]
+++
# StartTLS in LDAP

LDAP as a protocol is a binary protocol which uses ASN.1 BER encoded
structures to communicate between a client and server, to query
directory information (ie users, groups, locations, etc).

When this was created there was little consideration to security with
regard to person-in-the-middle attacks (aka mitm: meddler in the middle,
interception). As LDAP has become used not just as a directory service
for accessing information, but now as an authentication and
authorisation system it\'s important that the content of these
communications is secure from tampering or observation.

There have been a number of introduced methods to try and assist with
this situation. These are:

-   StartTLS
-   SASL with encryption layers
-   LDAPS (LDAP over TLS)

Other protocols of a similar age also have used StartTLS such as SMTP
and IMAP. However recent [research](https://nostarttls.secvuln.info/)
has (again) shown issues with correct StartTLS handling, and recommends
using SMTPS or IMAPS.

Today the same is true of LDAP - the only secure method of communication
to an LDAP server is LDAPS. In this blog, I\'ll be exploring the issues
that exist with StartTLS (I will not cover SASL or GSSAPI).

## How does StartTLS work?

StartTLS works by starting a plaintext (unencrypted) connection to the
LDAP server, and then by upgrading that connection to begin TLS within
the existing connection.

    ┌───────────┐                            ┌───────────┐
    │           │                            │           │
    │           │─────────open tcp 389──────▶│           │
    │           │◀────────────ok─────────────│           │
    │           │                            │           │
    │           │                            │           │
    │           │────────ldap starttls──────▶│           │
    │           │◀──────────success──────────│           │
    │           │                            │           │
    │  Client   │                            │  Server   │
    │           │──────tls client hello─────▶│           │
    │           │◀─────tls server hello──────│           │
    │           │────────tls key xchg───────▶│           │
    │           │◀────────tls finish─────────│           │
    │           │                            │           │
    │           │──────TLS(ldap bind)───────▶│           │
    │           │                            │           │
    │           │                            │           │
    └───────────┘                            └───────────┘

As we can see in LDAP StartTLS we establish a valid plaintext tcp
connection, and then we send and LDAP message containing a StartTLS
extended operation. If successful, we begin a TLS handshake over the
connection, and when complete, our traffic is now encrypted.

This is contrast to LDAPS where TLS must be successfully established
before the first LDAP message is exchanged.

It\'s a good time to note that this is inefficent as it takes an extra
round-trip to establish StartTLS like this contrast to LDAPS which
increases latency for all communications. LDAP clients tend to open and
close many connections, so this adds up quickly.

## Security Issues

### Client Misconfiguration

LDAP servers at the start of a connection will only accept two LDAP
messages. Bind (authenticate) and StartTLS. Since StartTLS starts with a
plaintext connection, if a client is misconfigured it is trivial for it
to operate without StartTLS.

For example, consider the following commands.

    # ldapwhoami -H ldap://172.17.0.3:389 -x -D 'cn=Directory Manager' -W
    Enter LDAP Password:
    dn: cn=directory manager
    # ldapwhoami -H ldap://172.17.0.3:389 -x -Z -D 'cn=Directory Manager' -W
    Enter LDAP Password:
    dn: cn=directory manager

Notice that in both, the command succeeds and we authenticate. However,
only in the second command are we using StartTLS. This means we
trivially leaked our password. Forcing LDAPS to be the only protocol
prevents this as every byte of the connection is always encrypted.

    # ldapwhoami -H ldaps://172.17.0.3:636 -x -D 'cn=Directory Manager' -W
    Enter LDAP Password:
    dn: cn=directory manager

Simply put this means that if you forget to add the command line flag
for StartTLS, forget the checkbox in an admin console, or any other kind
of possible human error (which happen!), then LDAP will silently
continue without enforcing that StartTLS is present.

For a system to be secure we must prevent human error from being a
factor by removing elements of risk in our systems.

### MinSSF

A response to the above is to enforce MinSSF, or \"Minimum Security
Strength Factor\". This is an option on both OpenLDAP and 389-ds and is
related to the integration of SASL. It represents that the bind method
used must have \"X number of bits\" of security (however X is very
arbitrary and not really representative of true security).

In the context of StartTLS or TLS, the provided SSF becomes the number
of bits in the symmetric encryption used in the connection. Generally
this is 128 due to the use of AES128.

Let us assume we have configured MinSSF=128 and we attempt to bind to
our server.

    ┌───────────┐                            ┌───────────┐
    │           │                            │           │
    │           │─────────open tcp 389──────▶│           │
    │           │◀────────────ok─────────────│           │
    │  Client   │                            │  Server   │
    │           │                            │           │
    │           │──────────ldap bind────────▶│           │
    │           │◀───────error - minssf──────│           │
    │           │                            │           │
    └───────────┘                            └───────────┘

The issue here is the minssf isn\'t enforced until the bind message is
sent. If we look at the LDAP rfc we see:

    BindRequest ::= [APPLICATION 0] SEQUENCE {
         version                 INTEGER (1 ..  127),
         name                    LDAPDN,
         authentication          AuthenticationChoice }

    AuthenticationChoice ::= CHOICE {
         simple                  [0] OCTET STRING,
                                 -- 1 and 2 reserved
         sasl                    [3] SaslCredentials,
         ...  }

    SaslCredentials ::= SEQUENCE {
         mechanism               LDAPString,
         credentials             OCTET STRING OPTIONAL }

Which means that in a simple bind (password) in the very first message
we send our plaintext password. MinSSF only tells us *after* we already
made the mistake, so this is not a suitable defence.

### StartTLS can be disregarded

An interesting aspect of how StartTLS works with LDAP is that it\'s
possible to prevent it from being installed successfully. If we look at
the [RFC](https://datatracker.ietf.org/doc/html/rfc4511#section-4.14.2):

    If the server is otherwise unwilling or unable to perform this
    operation, the server is to return an appropriate result code
    indicating the nature of the problem.  For example, if the TLS
    subsystem is not presently available, the server may indicate this by
    returning with the resultCode set to unavailable.  In cases where a
    non-success result code is returned, the LDAP session is left without
    a TLS layer.

What this means is it is up to the client and how they respond to this
error to enforce a correct behaviour. An example of a client that
disregards this error may proceed such as:

    ┌───────────┐                            ┌───────────┐
    │           │                            │           │
    │           │─────────open tcp 389──────▶│           │
    │           │◀────────────ok─────────────│           │
    │           │                            │           │
    │  Client   │                            │  Server   │
    │           │────────ldap starttls──────▶│           │
    │           │◀───────starttls error──────│           │
    │           │                            │           │
    │           │─────────ldap bind─────────▶│           │
    │           │                            │           │
    └───────────┘                            └───────────┘

In this example, the ldap bind proceeds even though TLS is not active,
again leaking our password in plaintext. A classic example of this is
OpenLDAP\'s own cli tools which in almost all examples of StartTLS
online use the option \'-Z\' to enable this.

    # ldapwhoami -Z -H ldap://127.0.0.1:12345 -D 'cn=Directory Manager' -w password
    ldap_start_tls: Protocol error (2)
    dn: cn=Directory Manager

The quirk is that \'-Z\' here only means to *try* StartTLS. If you want
to fail when it\'s not available you need \'-ZZ\'. This is a pretty easy
mistake for any administrator to make when typing a command. There is no
way to configure in ldap.conf that you always want StartTLS enforced
either leaving it again to human error. Given the primary users of the
ldap cli are directory admins, this makes it a high value credential
open to potential human input error.

Within client applications a similar risk exists that the developers
need to correctly enforce this behaviour. Thankfully for us, the all
client applications that I tested handle this correctly:

-   SSSD
-   nslcd
-   ldapvi
-   python-ldap

However, I am sure there are many others that should be tested to ensure
that they correctly handle errors during StartTLS.

### Referral Injection

Referral\'s are a feature of LDAP that allow responses to include extra
locations where a client may look for the data they requested, or to
extend the data they requested. Due to the design of LDAP and it\'s
response codes, referrals are valid in all response messages.

LDAP StartTLS does allow a referral as a valid response for the client
to then follow - this may be due to the requested server being
undermaintenance or similar.

Depending on the client implementation, this may allow an mitm to
proceed. There are two possible scenarioes.

Assuming the client *does* do certificate validation, but is poorly
coded, the following may occur:

    ┌───────────┐                            ┌───────────┐
    │           │                            │           │
    │           │─────────open tcp 389──────▶│           │
    │           │◀────────────ok─────────────│           │
    │           │                            │  Server   │
    │           │                            │           │
    │           │────────ldap starttls──────▶│           │
    │           │◀──────────referral─────────│           │
    │           │                            │           │
    │           │                            └───────────┘
    │  Client   │
    │           │                            ┌───────────┐
    │           │─────────ldap bind─────────▶│           │
    │           │                            │           │
    │           │                            │           │
    │           │                            │ Malicious │
    │           │                            │  Server   │
    │           │                            │           │
    │           │                            │           │
    │           │                            │           │
    └───────────┘                            └───────────┘

In this example our server sent a referral as a response to the StartTLS
extended operation, which the client then followed - however the client
did *not* attempt to install StartTLS again when contacting the
malicious server. This would allow a bypass of certification validation
by simply never letting TLS begin at all. Thankfully the clients I
tested did not exhibt this behaviour, but it is possible.

If the client has configured certificate validation to never
(tls_reqcert = never, which is a surprisingly common setting \...) then
the following is possible.

    ┌───────────┐                            ┌───────────┐
    │           │                            │           │
    │           │─────────open tcp 389──────▶│           │
    │           │◀────────────ok─────────────│           │
    │           │                            │  Server   │
    │           │                            │           │
    │           │────────ldap starttls──────▶│           │
    │           │◀──────────referral─────────│           │
    │           │                            │           │
    │           │                            └───────────┘
    │  Client   │
    │           │                            ┌───────────┐
    │           │────────ldap starttls──────▶│           │
    │           │◀──────────success──────────│           │
    │           │                            │           │
    │           │◀──────TLS installed───────▶│ Malicious │
    │           │                            │  Server   │
    │           │───────TLS(ldap bind)──────▶│           │
    │           │                            │           │
    │           │                            │           │
    └───────────┘                            └───────────┘

In this example the client follows the referral and then attempts to
install StartTLS again. The malicious server may present any certificate
it wishes and can then intercept traffic.

In my testing I found that this affected both SSSD and nslcd, however
both of these when redirected to the malicous server would attempt to
install StartTLS over an existing StartTLS channel, which caused the
server to return an error condition. Potentially a modified malicious
server in this case would be able to install two layers of TLS, or a
response that would successfully trick these clients to divulging
further information. I have not yet spent time to research this further.

## Conclusion

While not as significant as the results found on \"No Start TLS\", LDAP
still is potentially exposed to risks related to StartTLS usage. To
mitigate these LDAP server providers should disable plaintext LDAP ports
and exclusively use LDAPS, with tls_reqcert set to \"demand\".

