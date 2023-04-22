+++
title = "Windows Hello in Webauthn-rs"
date = 2020-08-24
slug = "2020-08-24-windows_hello_in_webauthn_rs"
# This is relative to the root!
aliases = [ "2020/08/24/windows_hello_in_webauthn_rs.html", "blog/html/2020/08/24/windows_hello_in_webauthn_rs.html" ]
+++
# Windows Hello in Webauthn-rs

Recently I\'ve been working again on
[webauthn-rs](https://crates.io/crates/webauthn-rs), as a member of the
community wants to start using it in production for a service. So far
the development of the library has been limited to the test devices that
I own, but now this pushes me toward implementing true fido compliance.

A really major part of this though was that a lot of their consumers use
windows, which means support windows hello.

## A background on webauthn

Webauthn itself is not a specification for the cryptographic operations
required for authentication using an authenticator device, but a
specification that wraps other techniques to allow a variety of
authenticators to be used exposing their \"native\" features.

The authentication side of webauthn is reasonably simple in this way.
The server stores a public key credential associated to a user. During
authentication the server provides a challenge which the authenticator
signs using it\'s private key. The server can then verify using it\'s
copy of the challenge, and the public key that the authentication must
have come from that credentials. Of course like anything there is a
little bit of magic in here around how the authenticators store
credentials that allows other properties to be asserted, but that\'s
beyond the scope of this post.

The majority of the webauthn specification is around the process of
registering credentials and requesting specific properties to exist in
the credentials. Some of these properties are optional hints (resident
keys, authenticator attachment) and some of these properties are
enforced (user verification so that the credential is a true MFA).
Beyond these there is also a process for the authenticator to provide
information about it\'s source and trust. This process is attestation
and has multiple different formats and details associated.

It\'s interesting to note that for most deployments of webauthn,
attestation is not required by the attestation conveyance preference,
and generally provides little value to these deployments. For many sites
you only need to know that a webauthn authenticator is in use. However
attestation allows environments with strict security requirements to
verify and attest the legitimacy of, and make and model of
authenticators in use. (An interesting part of webauthn is how much of
it seems to be Google and Microsoft internal requirements leaking into a
specification, just saying).

This leads to what is effectively, most of the code in webauthn-rs -
attestation.rs.

## Windows Hello

Windows Hello is Microsoft\'s equivalent to TouchID on iOS. Using a
Trusted Platform Module (TPM) as a tamper-resistant secure element, it
allows devices such as a Windows Surface to perform cryptographic
operations. As Microsoft is attempting to move to a passwordless future
(which honestly, I\'m on board for and want to support in Kanidm), this
means they want to support Webauthn on as many of their devices as
possible. Microsoft even defines in their hardware requirements for
Windows 10 Home, Pro, Education and Enterprise that [as of July 28,
2016, all new device models, lines or series \... a component which
implements the TPM 2.0 must be present and enabled by default from this
effective
date.](https://docs.microsoft.com/en-us/windows-hardware/design/minimum/minimum-hardware-requirements-overview).
This is pretty major as this means that slowly MS have been ensuring
that *all* consumer and enterprise devices are steadily moving to a
point where passwordless is a viable future. Microsoft state that they
use TPMv2 for many reasons, but a defining one is: [The TPM 1.2 spec
only allows for the use of RSA and the SHA-1 hashing
algorithm](https://docs.microsoft.com/en-us/windows/security/information-protection/tpm/tpm-recommendations)
which is now considered broken.

Of course, if you have noticed this means that TPM\'s are involved.
Webauthn supports a TPM attestation path, and that means I have to
implement it.

## Once more into the abyss

Reading the [Webauthn spec for TPM
attestation](https://www.w3.org/TR/webauthn/#tpm-attestation) it pointed
me to the TPMv2.0 specification part1, part2 and part3. I will spare you
from this as there is a sum total of 861 pages between these documents,
and the Webauthn spec while it only references a few parts, manages to
then create a set of expanding references within these documents. To
make it even more enjoyable, text search is mostly broken in these
documents, meaning that trying to determine the field contents and types
involves a lot of manual-eyeball work.

TPM\'s structures are packed C structs which means that they can be very
tricky to parse. They use u16 identifiers to switch on unions, and other
fun tricks that we love to see from C programs. These u16\'s often have
some defined constants which are valid choices, such as TPM_ALG_ID,
which allows switching on which cryptographic algorithms are in use.
Some stand out parts of this section were as follows.

Unabashed optimism:

`TPM_ALG_ERROR 0x0000 // Should not occur`

Broken Crypto

`TPM_ALG_SHA1 0x0004 // The SHA1 Algorithm`

Being the boomer equivalent of
[JWT](https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/)

`TPM_ALG_NULL 0x0010 // The NULL Algorithm`

And supporting the latest in modern cipher suites

`TPM_ALG_XOR 0x000A // TCG TPM 2.0 library specification - the XOR encryption algorithm.`

`ThE XOR eNcRyPtIoN aLgoRitHm.`

Some of the structures are even quite fun to implement, such as
TPMT_SIGNATURE, where a matrix of how to switch on it is present where
the first two bytes when interpreted as a u16, define a TPM_ALG_ID
where, if it the two bytes are not in a set of the TPM_ALG_ID then the
whole blob including leading two bytes is actually just a blob of hash.
It would certainly be unfortunate if in the interest of saving two bytes
that my hash accidentally emited data where the first two bytes were
accidentally a TPM_ALG_ID causing a parser to overflow.

I think the cherry on all of this though, is that despite Microsoft
requiring TPMv2.0 to move away from RSA and SHA-1, that when I checked
the attestation signatures for a Windows Hello device I had to implement
the following:

    COSEContentType::INSECURE_RS1 => {
        hash::hash(hash::MessageDigest::sha1(), input)
            .map(|dbytes| Vec::from(dbytes.as_ref()))
            .map_err(|e| WebauthnError::OpenSSLError(e))
    }

## Conclusion

Saying this, I\'m happy that Windows Hello is now in Webauthn-rs. The
actual Webauthn authentication flows DO use secure algorithms (RSA2048 +
SHA256 and better), it is only in the attestation path that some
components are signed by SHA1. So please use
[webauthn-rs](https://crates.io/crates/webauthn-rs), and do use Windows
Hello with it!

