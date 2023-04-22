+++
title = "Webauthn UserVerificationPolicy Curiosities"
date = 2020-11-21
slug = "2020-11-21-webauthn_userverificationpolicy_curiosities"
# This is relative to the root!
aliases = [ "2020/11/21/webauthn_userverificationpolicy_curiosities.html", "blog/html/2020/11/21/webauthn_userverificationpolicy_curiosities.html" ]
+++
# Webauthn UserVerificationPolicy Curiosities

Recently I received a
[pair](https://github.com/kanidm/webauthn-rs/issues/32)
[of](https://github.com/kanidm/webauthn-rs/issues/34) interesting bugs
in [Webauthn RS](https://github.com/kanidm/webauthn-rs/) where certain
types of authenticators would not work in Firefox, but did work in
Chromium. This confused me, and I couldn\'t reproduce the behaviour. So
like any obsessed person I ordered myself one of the affected devices
and waited for Australia Post to lose it, find it, lose it again, and
then finally deliver the device 2 months later.

In the meantime I swapped browsers from Firefox to Edge and started to
notice some odd behaviour when logging into my corporate account - my
yubikey began to ask me for my pin on every authentication, even though
the key was registered to the corp servers *without* a pin. Yet the key
kept working on Edge with a pin - and confusingly *without* a pin on
Firefox.

## Some background on Webauthn

Before we dive into the issue, we need to understand some details about
Webauthn. [Webauthn](https://www.w3.org/TR/webauthn/) is a standard that
allows a client (commonly a web browser) to cryptographically
authenticate to a server (commonly a web site). Webauthn defines how
different types of hardware cryptographic authenticators may communicate
between the client and the server.

An example of some types of authenticator devices are U2F tokens
(yubikeys), TouchID (Apple Mac, iPhone, iPad), Trusted Platform Modules
(Windows Hello) and many more. Webauthn has to account for differences
in these hardware classes and how they communicate, but in the end each
device performs a set of [asymmetric
cryptographic](https://en.wikipedia.org/wiki/Public-key_cryptography)
(public/private key) operations.

Webauthn defines the structures of how a client and server communicate
to both register new authenticators and subsequently authenticate with
those authenticators.

For the first step of registration, the server provides a registration
challenge to the client. The structure of this (which is important for
later) looks like:

    dictionary PublicKeyCredentialCreationOptions {
        required PublicKeyCredentialRpEntity         rp;
        required PublicKeyCredentialUserEntity       user;

        required BufferSource                             challenge;
        required sequence<PublicKeyCredentialParameters>  pubKeyCredParams;

        unsigned long                                timeout;
        sequence<PublicKeyCredentialDescriptor>      excludeCredentials = [];
        AuthenticatorSelectionCriteria               authenticatorSelection = {
            AuthenticatorAttachment      authenticatorAttachment;
            boolean                      requireResidentKey = false;
            UserVerificationRequirement  userVerification = "preferred";
        };
        AttestationConveyancePreference              attestation = "none";
        AuthenticationExtensionsClientInputs         extensions;
    };

The client then takes this structure, and creates a number of hashes
from it which the authenticator then signs. This signed data and options
are returned to the server as a
[PublicKeyCredential](https://w3c.github.io/webauthn/#iface-pkcredential)
containing an [Authenticator Attestation
Response](https://www.w3.org/TR/webauthn/#iface-authenticatorattestationresponse).

Next is authentication. The server sends a challenge to the client which
has the structure:

    dictionary PublicKeyCredentialRequestOptions {
        required BufferSource                challenge;
        unsigned long                        timeout;
        USVString                            rpId;
        sequence<PublicKeyCredentialDescriptor> allowCredentials = [];
        UserVerificationRequirement          userVerification = "preferred";
        AuthenticationExtensionsClientInputs extensions;
    };

Again, the client takes this structure, takes a number of hashes and the
authenticator signs this to prove it is the holder of the private key.
The signed response is sent to the server as a PublicKeyCredential
containing an [Authenticator Assertion
Response](https://www.w3.org/TR/webauthn/#iface-authenticatorassertionresponse).

Key to this discussion is the following field:

    UserVerificationRequirement          userVerification = "preferred";

This is present in both PublicKeyCredentialRequestOptions and
PublicKeyCredentialCreationOptions. This informs what level of
interaction assurance should be provided during the signing process.
These are discussed in [NIST SP800-64b (5.1.7,
5.1.9)](https://pages.nist.gov/800-63-3/sp800-63b.html) (which is just
an excellent document anyway, so read it).

One aspect of these authenticators is that they must provide tamper
proof evidence that a person is physically present and interacting with
the device for the signature to proceed. This is important as it means
that if someone is able to gain remote code execution on your system,
they are unable to use your authenticator devices (even if it\'s part of
the device, like touch id) as they are not physically present at the
machine.

Some authenticators are able to go beyond to strengthen this assurance,
by verifying the identity of the person interacting with the
authenticator. This means that the interaction *also* requires say a PIN
(something you know), or a biometric (something you are). This allows
the authenticator to assert not just that *someone* is present but that
it is a specific person who is present.

All authenticators are capable of asserting user presence but only some
are capable of asserting user verification. This creates two classes of
authenticators as defined by NIST SP800-64b.

Single-Factor Cryptographic Devices (5.1.7) which only assert presence
(the device becomes something you have) and Multi-Factor Cryptographic
Devices (5.1.9) which assert the identity of the holder (something you
have + something you know/are).

Webauthn is able to request the use of a Single-Factor Device or
Multi-Factor Device through it\'s UserVerificationRequirement option.
The levels are:

-   Discouraged - Only use Single-Factor Devices
-   Required - Only use Multi-Factor Devices
-   Preferred - Request Multi-Factor if possible, but allow
    Single-Factor devices.

## Back to the mystery \...

When I initially saw these reports - of devices that did not work in
Firefox but did in Chromium, and of devices asking for PINs on some
browsers but not others -I was really confused. The breakthrough came as
I was developing [Webauthn Authenticator
RS](https://github.com/kanidm/webauthn-authenticator-rs). This is the
client half of Webauthn, so that I could have the
[Kanidm](https://github.com/kanidm/kanidm) CLI tools use Webauthn for
multi-factor authentication (MFA). In the process, I have been using the
[authenticator](https://crates.io/crates/authenticator) crate made by
Mozilla and used by Firefox.

The authenticator crate is what communicates to authenticators by NFC,
Bluetooth, or USB. Due to the different types of devices, there are
multiple different protocols involved. For U2F devices, the protocol is
CTAP over USB. There are two versions of the CTAP protocol - CTAP1, and
CTAP2.

In the authenticator crate, only CTAP1 is supported. CTAP1 devices are
unable to accept a PIN, so user verification must be performed
internally to the device (such as a fingerprint reader built into the
U2F device).

Chromium, however, is able to use CTAP2 - CTAP2 *does* allow a PIN to be
provided from the host machine to the device as a user verification
method.

## Why would devices fail in Firefox?

Once I had learnt this about CTAP1/CTAP2, I realised that my example
code in Webauthn RS was hardcoding Required as the user verification
level. Since Firefox can only use CTAP1, it was unable to use PINs to
U2F devices, so they would not respond to the challenge. But on Chromium
with CTAP2 they *are* able to have PINs so Required can be satisfied and
the devices work.

## Okay but the corp account?

This one is subtle. The corp identity system uses user verification of
\'Preferred\'. That meant that on Firefox, no PIN was requested since
CTAP1 can\'t provide them, but on Edge/Chromium a PIN *can* be provided
as they use CTAP2.

What\'s more curious is that the same authenticator device is flipping
between Single Factor and Multi Factor, with the same Private/Public Key
pair just based on what protocol is used! So even though the
\'Preferred\' request can be satisfied on Chromium/Edge, it\'s not on
Firefox. To further extend my confusion, the device was originally
registered to the corp identity system in Firefox so it would have *not*
had user verification available, but now that I use Edge it has *gained*
this requirement during authentication.

## That seems \... wrong.

I agree. But Webauthn fully allows this. This is because user
verification is a property of the *request/response* flow, not a
property of the *device*.

This creates some interesting side effects that become an opportunity
for user confusion. (*I* was confused about what the behaviour was and I
write a webauthn server and client library - imagine how other people
feel \...).

## Devices change behaviour

This means that during registration one policy can be requested (i.e.
Required) but subsequently it may not be used (Preferred + Firefox +
U2F, or Discouraged). Another example of a change in behaviour occurs
when a device is used on Chromium with Preferred user verification is
required, but when used on Firefox the device may *not* require
verification. It also means that a site that implements Required can
have devices that simply don\'t work in other browsers.

Because this is changing behaviour it can confuse users. For examples:

-   Why do I need a PIN now but not before?
-   Why did I need a PIN before but not now?
-   Why does my authenticator work on this computer but not on another?

## Preferred becomes Discouraged

This opens up a security risk where since Preferred \"attempts\"
verification but allows it to not be present, a U2F device can be
\"downgraded\" from Multi-Factor to Single-Factor by using it with CTAP1
instead of CTAP2. Since it\'s also per *request/response*, a compromised
client could also tamper with the communication to the authenticator
removing the requested userverification parameter silently and the
server would allow it.

This means that in reality, Preferred is policy and security wise
equivalent to Discouraged, but with a more annoying UI/UX for users who
have to conduct a verification that doesn\'t actually help identify
them.

Remember - if unspecified, \'Preferred\' is the default user
verification policy in Webauthn!

## Lock Out / Abuse Vectors

There is also a potential abuse vector here. Many devices such as U2F
tokens perform a \"trust on first use\" for their PIN setup. This means
that the first time a user verification is requested you configure the
pin at that point in time.

A potential abuse vector here is a token that is always used on Firefox,
a malicious person could connect the device to Chromium, and setup the
PIN without the knowledge of the owner. The owner could continue to use
the device, and when Firefox eventually supports CTAP2, or they swap
computer or browser, they would *not* know the PIN, and their token
would effectively be unusable at that point. They would need to reset
it, potentially causing them to be locked out from accounts, but more
likely causing them to need to conduct a *lot* of password/credential
resets.

## Unable to implement Authenticator Policy

One of the greatest issues here though is that because user verification
is part of the *request/response* flow and not *per device* attributes,
authenticator policy, and mixed credentials are unable to exist in the
current implementation of Webauthn.

Consider a user who has enrolled say their laptop\'s U2F device +
password, and their iPhone\'s touchID to a server. Both of these are
Multi Factor credentials. The U2F is a Single Factor Device and becomes
Multi-Factor in combination with the password. The iPhone touchID is a
Multi-Factor Device on it\'s due to the biometric verification it is
capable of.

We *should* be able to have a website request webauthn and based on the
device used we can flow to the next required step. If the device was the
iPhone, we would be authenticated as we have authenticated a Multi
Factor credentials. If we saw the U2F device we would then move to
request the password since we have only received a Single Factor.
However Webauthn is unable to express this authentication flow.

If we requested Required, we would exclude the U2F device.

If we requested Discouraged, we would exclude the iPhone.

If we request Preferred, the U2F device could be used on a different
browser with CTAP2, either:

-   bypassing the password, since the device is now a self contained
    Multi-Factor; or
-   the U2F device could prompt for the PIN needlessly and we progress
    to setting a password

The request to an iPhone could be tampered with, preventing the
verification occurring and turning it into a single factor device
(presence only).

Today, these mixed device scenarios can not exist in Webauthn. We are
unable to create the policy around Single-Factor and Multi-Factor
devices as defined by NIST because these require us to assert the
verification requirements per credential, but Webauthn can not satisfy
this.

We would need to pre-ask the user *how* they want to authenticate on
that device and then only send a Webauthn challenge that can satisfy the
authentication policy we have decided on for those credentials.

## How to fix this

The solution here is to change PublicKeyCredentialDescriptor in the
Webauthn standard to contain an optional UserVerificationRequirement
field. This would allow a \"global\" default set by the server and then
per-credential requirements to be defined. This would allow the user
verification properties during registration to be associated to that
credential, which can then be enforced by the server to guarantee the
behaviour of a webauthn device. It would also allow the \'Preferred\'
option to have a valid and useful meaning during registration, where
devices capable of verification can provide that or not, and then that
verification boolean can be then transformed to a Discouraged or
Required setting for that credential for future authentications.

The second change would be to disallow \'Preferred\' as a valid value in
the \"global\" default during authentications. The new \"default\"
global value should be \'Discouraged\' and then only credentials that
registered with verification would indicate that in their
PublicKeyCredentialDescriptor.

This would resolve the issues above by:

-   Making the use of an authenticator consistent after registration.
    For example, authenticators registered with CTAP1 would stay
    \'Discouraged\' even when used with CTAP2
-   If PIN/Verification abuse occurred, the credentials registered on
    CTAP1 without verification would continue to be \'presence only\'
    preventing the lockout
-   Allowing the server to proceed with the authentication flow based on
    which credential authenticated and provide logic about further
    factors if needed.
-   Allowing true Single Factor and Multi Factor device policies to be
    expressed in line with NIST SP800-63b, so users can have a mix of
    Single and Multi Factor devices associated with a single account.

I have since opened [this
issue](https://github.com/w3c/webauthn/issues/1510) with the webauthn
specification about this, but early comments seem to be highly focused
on the current expression of the standard rather than the issues around
the user experience and ability for identity systems to accurately
express credential policy.

In the meantime, I am going to make changes to Webauthn RS to help avoid
some of these issues:

-   Preferred will be renamed to Preferred_Is_Equivalent_To_Discouraged
    (it will still emit \'Preferred\' in the JSON, this only changes the
    Rust API enum)
-   Credential structures persisted by applications will contain the
    boolean of user-verification if it occurred during registration
-   During an authentication, if the set of credentials contains
    inconsistent user-verification booleans, an error will be raised
-   Authentication User Verification Policy is derived from the set of
    credentials having a consistent user-verification boolean

While not perfect, it will mean that it\'s \"hard to hold it wrong\"
with Webauthn RS.

## Acknowledgements

Thanks to both \@Charcol0x89 and \@JuxhinDB for reviewing this post.

