Exploring Webauthn Use Cases
============================

Webauthn is viewed by many people and companies as the future of authentication on the internet
and within our workplaces. It has the support of many device manufacturers, browser vendors and
authentication providers.

But for Webauthn's lofty goals and promises, as a standard it has many fractured parts.
Many of the features it claims at best don't work, at worst, present possible security risks.
The standard itself is quite confusing, uses dense and obtuse language, and laid out in a very piecemeal
way. This makes it hard to see the full picture to construct a proper security and use cases analysis.

As the author of both a relying party ( `Kanidm <https://github.com/kanidm/kanidm>`_ ) and the
`Webauthn Library for Rust <https://github.com/kanidm/webauthn-rs>`_ I want to describe these problems.

To understand the issues, we first need to explore how Webauthn works, and then the potential use cases.
While not an exhaustive list of all the ways Webauthn could be used, I am trying to cover
the ways that I have seen in the wild, and how people have requested we want to use these.

Generally, I will try to use *accessible* language versions of terms, rather than the Webauthn
standard terms, as the language in the standard is confusing / misleading - even if you have read
the standard multiple times.

Use Cases
---------

To understand the limitations of Webauthn, we need to examine how Webauthn would be used by an
identity provider. The identity provider takes the pieces from Webauthn and their own elements
and creates a work flow for the user to interact with. We will turn these into use cases.

Remember, the goal of webauthn is to enable all people, from various cultural, social and educational backgrounds to authenticate
securely, so it's critical these processes are clear, accessible, and transparent.

For the extremely detailed versions of these use cases, see the end of this post.

A really important part of these use cases is attestation. Attestation is the same as the little gold
star sticker that you found on Nintendo game boxes. It's a "certificate of authenticity". Without attestation,
the authenticator that we are communicating with could be anything. It could be a yubikey, Apple's touchid,
a custom-rolled software token, or even a private key you calculated on pen and paper. Attestation
is a cryptograhic "certificate of authenticity" which tells us exactly whom produced that device and
if it can be trusted.

This is really important, because within Webauthn many things are done on the authenticator such as
user-verification. Rather than just touching the token, you may have to enter a PIN or use a fingerprint. But
the server never sees that PIN or fingerprint - the authenticator just sends us a true/false flag if
the verification occured and was valid. So for us to trust this flag (and many others), we need to
know that the token is made by someone we trust, so that we know that flag *means* something.

Without this attestation, all we know is that "there is some kind of cryptograhic key that the user
can access" and we have no other information about where it might be stored, or how it works. With
attestation we can make stronger informed assertions about the properties of the authenticators
our users are using.

Security Token (Public)
^^^^^^^^^^^^^^^^^^^^^^^

In this use case, we want our authenticator to be a single factor to compliment an existing password. This
is the "classic" security key use case, that was originally spawned by U2F.
Instead of an authenticator, a TOTP scheme could alternately be used where either the TOTP or authenticator
plus the password is sufficient to grant access.

Generally in this use case, most identity providers do not care about attestation of the authenticator,
what is more important is that some kind of non-password authentication exists and is present.

Security Token (Corporate)
^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the same as the public use case, except that in many corporations we may want to define a list
of trusted providers of tokens. It's important to us here that these tokens have a vetted or audited
supply chain, and we have an understanding of "where" the cryptographic material may reside.

For this example, we likely want attestation, as well as the ability to ensure these credentials are
not recoverable or transferable between authenticators. Resident Key may or may not be required
in these cases.

Since these are guided by policy, we likely want to have our user interfaces guide our users to register
or use the correct keys since we have a stricter list of what is accepted. For example, there is no
point in the UI showing a prompt for caBLE (phone authenticator) when we know that only a USB key
is accepted!

PassKey (Public)
^^^^^^^^^^^^^^^^

A passkey is the "Apple terminology" for a cryptographic credential that can exist between multiple
devices, and potentially even between multiple Apple accounts. This are intended to be a "single
factor" replacement to passwords. They can be airdropped and moved between devices, and at the least
in their usage with iOS devices, they *can* perform user verification, but it may not be required
for the identity provider to verify this. This is because even as a single factor, these credentials *do* resolve
many of the weaknesses of passwords even if user verification did not occur (and even if it did occur
it can not be verified, for reasons we will explore in this post).

It is likely we will see Google and Microsoft develop similar. 1Password is already progressing to
allow webauthn in their wallets.

In this scenario, all we care about is having some kind of credential that is stronger than a password.
It's a single factor, and we don't know anything about the make or model of the device. User verification
might be performed, but we don't intend to verify if it is.

Nothing is really stopping a U2F style token like a yubikey being a passkey, but that relies on the
identity provider to allow multiple devices and to have work flows to enrol them across different
devices. It's also unclear how this will work from an identity provider when someone has say a
Microsoft Surface and an Apple iPhone.

Passwordless MFA (Public)
^^^^^^^^^^^^^^^^^^^^^^^^^

In this example, rather than having our authenticator as a single factor, we want it to be truly
multifactor. This allows the user to login with nothing but their authenticator, and we have
a secure multifactor work flow. This is a stronger level of authentication, where we are verifying
not just possession of the private key, but also the identity of who is using it.

As a result, we need to strictly verify that the authenticator did a valid user verification.

Given that the authenticator is now the "sole" authenticator (even if multi-factor) we are more
likely to want attestation here using privacy features granted through indirect attestation. That way
we can have a broad list of known good security token providers that we accept. Without attestation
we are unable to know if the user verification provided can be trusted.

Passwordless MFA (Corporate)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Again, this is similar to above. We narrow and focus this use case with a stricter attestation list
of what is valid. We also again want to strictly control and prevent cryptographic material being
moved, so we want to ensure these are not transferrable. We may want resident keys to be used here
too since we have a higher level of trust in our devices now too. Again, we also will want to be able to
strictly guide UI's due to our knowledge of exactly what devices we accept.

Usernameless
^^^^^^^^^^^^

Usernameless is similar to passwordless but *requires* resident keys as the username of the account
is bound to the key and discovered by the client. Otherwise many of the features of passwordless apply.

It's worth noting that due to the complexity and limitations of resident key management *it is not feasible*
for any public service provider to currently use usernameless credentials on a broad scale without
significant risk of credential loss. As a result, we limit our use case to corporate only, as they are
the only entities in the position to effectively manage these issues.

Due to the implementation of passkeys and passwordless in the broader world, the line is blurred between
these, so we will assume that passkeys and passwordless may sometimes attempt to be used in a usernameless
workflow (for example conditional UI)

Summary
^^^^^^^

Let's assemble a score card now. We'll define the use cases, the features, and what they require
and if webauthn can provide them.

.. csv-table:: Webauthn Score Card
    :header: "", "Security Token", "Sec Tok (Corp)", "PassKey", "Passwordless", "PwLess (Corp)"

    "**User Verification**", "no / ???", "no / ???", "no / ???", "required / ???", "required / ???"
    "**UV Policy**", "no / ???", "no / ???", "no / ???", "no / ???", "maybe / ???"
    "**Attestation**", "no / ???", "required / ???", "no / ???", "required / ???", "required / ???"
    "**Bound to Device / HW**", "no / ???", "required / ???", "no / ???", "required / ???", "required / ???"
    "**Resident Key**", "no / ???", "maybe / ???", "no / ???", "maybe / ???", "maybe / ???"
    "**UI Selection**", "maybe / ???", "maybe / ???", "no / ???", "maybe / ???", "required / ???"
    "**Update PII**", "no / ???", "no / ???", "maybe / ???", "maybe / ???", "maybe / ???"
    "**Result**", "???", "???", "???", "???", "???"

Now, I already know some of the answers to these, so lets fill in what we DO know.

.. csv-table:: Webauthn Score Card
    :header: "", "Security Token", "Sec Tok (Corp)", "PassKey", "Passwordless", "PwLess (Corp)"

    "**User Verification**", "no / ???", "no / ???", "no / ???", "required / ???", "required / ???"
    "**UV Policy**", "no / ???", "no / ???", "no / ???", "no / ???", "maybe / ???"
    "**Attestation**", "no / ✅", "required / ???", "no / ???", "required / ???", "required / ???"
    "**Bound to Device / HW**", "no / ✅", "required / ???", "no / ✅", "required / ???", "required / ???"
    "**Resident Key**", "no / ✅", "maybe / ???", "no / ✅", "no / ✅", "maybe / ???"
    "**Authenticator Selection**", "maybe / ???", "maybe / ???", "no / ???", "maybe / ???", "required / ???"
    "**Update PII**", "no / ✅", "no / ✅", "maybe / ???", "maybe / ???", "maybe / ???"
    "**Result**", "???", "???", "???", "???", "???"

The Problems
------------

Now lets examine the series of issues that exist within Webauthn, and how they impact our ability
to successfully implement the above.

Authenticator Selection
^^^^^^^^^^^^^^^^^^^^^^^

Today, there is no features in Webauthn that allow an identity provider at registration to pre-indicate
what transports are known to be valid for authenticators that are registering. This is contrast to
authentication, where a complete list of valid transports can be provided to help the browser select
the correct device to use in the authentication.

As a result, the only toggle you have is "platform" vs "cross-platform". Consider we have company issued
yubikeys. We know these can only work via USB because that is the model we have chosen.

However, during a registration because we can only indicate "cross-platform" it is completely valid
for a user to *attempt* to register say their iPhone via caBLE, or use another key via NFC. The user
may then become "confused" why their other keys didn't work for registration - the UI said they were
allowed to use it! This is a lack of constraint.

This process could be easily streamlined by allowing transports to be specified in registration, but
there is resistance to this `from the working group. <https://github.com/w3c/webauthn/issues/1716>`_

A real world example of this has already occurred, where the email provider `FastMail <https://www.fastmail.com/>`_
used specific language around "Security Tokens" including graphics of usb security keys in their documentation.
Because of this lack of ability to specify transports in the registration process, once caBLE was released
this means that FastMail now has to "rush" to respond to update their UI/Docs to work out how to communicate
this to users. They don't have a choice in temporarily excluding this either which may lead to user
confusion.

User Verification Inconsistent / Confusing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For our security key work flows we would like to construct a situation where the authenticator
is a single factor, and the users password or something else is the other factor. This means the
authenticator should only require interaction to touch it, and no PIN or biometric is needed.

There are some major barriers here sadly. Remember, we want to create a *consistent* user experience
so that people can become confident in the process they are using.

The problem is CTAP2.1 - this changes the behaviour of user verification 'discouraged' so that even
when you are registering a credential, you always need to enter a PIN or biometrics. However, when
authenticating, you never need the PIN or biometric.

There is *no communication* of the fact that the verification is only needed due to it being registration.

Surveying users showed about 60% expect when you need to enter your PIN/biometric at registration that
it will be *required* during future authentication. When it is not present during future authentications
this confuses people, and trains them that the PIN/biometrics is an inconsistent and untrustworthy
dialog. Sometimes it is there - sometimes it is not.

When you combine this with the fact that UV=preferred on most RP's is not validating the UV status,
we now have effectively trained all our users that user verification can appear and disappear and
not to worry about it, it's fine, it's just *inconsistent* so they never will consider it a threat.

It also means that when we try to adopt passwordless it will be *harder* to convince users this is
safe since they may believe that this inconsistent usage of user verification on their authenticators
is something that can be easily bypassed.

How can you trust that the PIN/biometric means something, when it is sometimes there and sometimes not?

This forces us even in our security key work flows to force UV=preferred, and to *go beyond the standard* to
enforce user verification checks are consistent based on their application at registration. This means
any CTAP2.1 device, even though it does NOT need a PIN as a single factor authenticator, will require
one as a security key to create a consistent user experience and so we can build trust in our user base.

At this point since we are effectively forcing UV to always occur, why not just transition to Passwordless?

It is worth noting that for *almost all identity providers* today, that the use of UV=preferred is
bypassable, as the user verification is not checked and there is no guidance in the specification
to check this. This has affected Microsoft Azure, Nextcloud, and others

As a result, the only trustworthy UV policies are required, or preferred with checks that go beyond
the standard. As far as I am aware, only Webauthn-RS providers these stricter requirement checks.

Discouraged could be used here, but needs user guidance and training to support it due to the inconsistent
dialogs with CTAP2.1.

User Verification Policy
^^^^^^^^^^^^^^^^^^^^^^^^

Especially in our passwordless scenarios, as an identity provider we may wish to define policy
about what user verification methods we allow from users. For example we may wish for PIN only
rather than allowing biometrics. We may also wish to express the policy on the length of the PIN as
well.

However, nothing in the response an authenticator provides you with this information about
what user verification method was used. Instead webauthn defines the `User Verification Method extension <https://www.w3.org/TR/webauthn-3/#sctn-uvm-extension>`_
which can allow an identity provider to request the device to provide what UVM was provided.

Sadly, nothing supports it in the wild. Experience with Webauthn-RS shows that it is never honoured
or provided when requested. This is true of most extensions in Webauthn. For bonus marks did you know
all extensions only are answered when you request attestation (this is not mentioned anywhere in the specification!)

As a corporate environment, we can kind-of control this through strict attestation lists, but as a public
identity provider with attestation it is potentially not possible to know or enforce this due
to extensions being widely unsupported and not implemented.

The reason this is "kind-of" is that yubikeys support PIN and some models also support biometrics, but
there is no distinction in their attestation. This means if we only wanted PIN auth, we could not use
yubikeys since there is no way to distinguish these. Additionally, things like minimum PIN length can't
be specified since we don't know what manufacturers support this extension. Devices like yubikeys have
an inbuilt minimum length of 8, but again we don't know if they'll use PIN given the availability of
biometrics.

Resident Keys can't be verified
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Resident Keys is where we know that the key material lives *only* within the cryptographic processor
of the authenticator. For example, a yubikey by default produces a key wrapped key, where the CredentialID
is itself the encrypted private key, and only that yubikey can decrypt that CredentialID to use it as the
private key. In very strict security environments, this may present a risk because an attacker *could*
bruteforce the CredentialID to decrypt the private key, allowing the attacker to then use the credential.
(It would take millions of years, but you know, some people have to factor that into their risk models).

To avoid this, you can request the device create a resident key - a private key that never leaves the
device. The CredentialID is just a "reference" to allow the device to look up the Credential but it
does not contain the private key itself.

The problem is that there is no *signal* in the attestation or response that indicates if a resident key
was created by the device.

You can request to find out if this was created with the
`Credential Properties <https://www.w3.org/TR/webauthn-3/#sctn-authenticator-credential-properties-extension>`_
extension.

The devil however, is in the details. Notably:

*"This client registration extension facilitates reporting certain credential properties known by the client"*

A client extension means that this extension is processed by the web browser, and exists in a section
of the response that is unsigned, and can not be verified. This means it is open to client side JS
tampering and forgery. This means we *can not* trust the output of this property.

As a result, there is *no simple way to verify a resident key was created*.

To make this better, the request to create the resident key *is not signed and can be stripped by client side javascript*.

So any compromised javascript (which Webauthn assumes is trusted) can strip a registration request
for a resident key, cause a key-wrapped-key to be created, and then "assert" pretty promise I swear
it's resident by faking the response to the extension.

The only way to guarantee you have a resident key, is to validate attestation from an authenticator
that *exclusively* makes resident keys (e.g. Apple iOS). Anything else, you can not assert is a true resident
key. Even if you subsequently attempt client side discovery of credentials, that is not the same
property as the key being resident. This is a trap that many identity providers may not know they are
exposed to.

Resident Keys can't be administered
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To compound the inability to verify creation of a resident key, the behaviour of resident keys (RK)
for most major devices is undefined. For example a Yubikey has limited storage for RKs
but I have been unable to find documenation about:

* How many RKs can exist on an authenticator.
* If the maximum number is created and we attempt to create more, does it act like a ring buffer and remove the oldest, or simply fail to create more?
* If it is possible to update usernames or other personal information related to the RKs in this device?
* Any API's or tooling to list, audit, delete or manage RK's on the device.

These are *basic* things that are critical for users and administrators, and they simply do not exist.
This complete absence of tooling makes RK's effectively useless to most users and deployments since
we have no method to manage, audit, modify or delete RK's.

Bound to Device / Hardware
^^^^^^^^^^^^^^^^^^^^^^^^^^

For the years leading up to 2022, Webauthn and it's design generally assumed a one to one relationship
between the hardware of an authenticator, and the public keys it produced. However, that has now changed
with the introduction of Apple Passkeys.

What is meant by "bound to device" is that given a public key, only a single hardware authenticator
exists that has access to the private key to sign something. This generally means that the cryptographic
operations, and the private key itself, are only ever known to the secure enclave of the account.

Apple's Passkeys change this, allowing a private key to be distributed between multiple devices of
an Apple account, but also the ability to transfer the private key to other nearby devices via airdrop. This
means the private key is no longer bound to a single physical device.

When we design a security policy this kind of detail matters, where some identity providers can accept
the benefits of a cryptographic authentication even if the private key is not hardware backed, but other
identity providers must require that private keys are securely stored in hardware.

The major issue in Webauthn is that the specification does not really have the necessary parts in place
to manage these effectively.

As an identity provider there is no way to currently indicate that you require a hardware bound
credential (or perhaps you want to require passkeys only!). Because of this lack of control, Apple's
implementation relies on another signal - a request for attestation.

If you do *not* request attestation, a passkey is created.

If you do request attestation (direct or indirect), a hardware bound key is created.

When the credential is created, there are a new set of "backup state" bits that can indicate if the
credential can be moved between devices. These are stored in the same set of bits that stores user verification
bits, meaning that to trust them, you need attestation (which Apple can't provide!). At the very least,
the attested Apple credentials that are hardware bound, do correctly show they are *not* backup capable
and are still resident keys.

Because of this, I expect to see that passkeys and related technology is treated in the manner as
initially described - a single-factor replacement to passwords. Where you need stronger MFA in the
style of a passwordless credential, it will not currently be possible to achieve this with Apple
Passkeys.

It's worth noting that it's unclear how other vendors will act here. Some may produce passkeys that
are attested, meaning that reliance on the backup state bits will become more important, but there
is also a risk that vendors will not implement this correctly.

Importantly some testing in pre-release versions showed that if passkeys are enabled, and you request
an attested credential, the registration fails blocking the bound credential creation. This will need retesting to
be sure of the behaviour in the final iOS 16 release, but this could be a show stopper for BYOD
users if not fixed. (20220614: We have confirmed that passkeys do block the creation of attested
device bound credentials).

Conclusion
----------

* ⚠️  - risks exist
* ✅ - works
* ❌ - broken/untrustworthy

.. csv-table:: Webauthn Score Card
    :header: "", "Security Token", "Sec Tok (Corp)", "PassKey", "Passwordless", "PwLess (Corp)"

    "**User Verification**", "no / ⚠️ ", "no / ⚠️ ", "no / ⚠️ ", "required / ✅", "required / ✅"
    "**UV Policy**", "no / ✅", "no / ✅", "no / ✅", "no / ✅", "maybe / ❌"
    "**Attestation**", "no / ✅", "required / ⚠️ ", "no / ✅", "required / ⚠️ ", "required / ⚠️ "
    "**Bound to Device / HW**", "no / ✅", "required / ⚠️ ", "no / ✅", "required / ⚠️ ", "required / ⚠️ "
    "**Resident Key**", "no / ✅", "maybe / ❌", "no / ✅", "no / ✅", "maybe / ❌"
    "**Authenticator Selection**", "maybe / ❌", "maybe / ❌", "no / ✅", "maybe / ❌", "required / ❌"
    "**Update PII**", "no / ✅", "no / ✅", "maybe / ❌", "maybe / ❌", "maybe / ❌"
    "**Result**", "⚠️  1, 2, 7", "⚠️  1, 2, 4, 5, 6, 7", "⚠️  1, 2, 8", "⚠️  4, 5, 7, 8", "⚠️  4, 5, 6, 7, 8"

1. User Verification in discouraged may incorrectly request UV, training users that UV prompts are "optional".
2. UV preferred, is bypassable in almost all implementations.
3. No method to request a UV policy including min PIN length or UV classes.
4. Existence of PassKeys on the device account, WILL prevent attested credentials from being created.
5. Currently relies on vendor specific attestation behaviour.
6. No way to validate a resident key is created without assumed vendor specific behaviours, or other out of band checks.
7. Unable to request constraints for authenticators that are used in the interaction.
8. Vendors often do not provide the ability to update PII on resident keys if used in these contexts

A very interesting take away from this however, is that "Passkeys" that Apple have created, are actually
identical to "Security Tokens" in how they operate and are validated, meaning that for all intents
and purposes they are the same scenario just with or without a password as the MFA element.

As we can see, from our use cases all of the scenarios have some kind of issues. They vary in severity
and whom the issue affects, but they generally are all subtle and may have implications on identity
providers. Generally the "trend" from these issues though, is that it feels like the Webauthn WG
have abandoned authenticators as "security tokens" and are pushing more toward Passkeys as Single Factor
or Passwordless scenarios. This is probably "a good thing", but it's not been communicated clearly
and there are still issues that exist in the Passkey and Passwordless scenarios.

Bonus - Other Skeletons
-----------------------

Javascript is considered trusted
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because Javascript is considered trusted, a large number of properties of Webauthn in its communication
are open to tampering which means that they infact, can not be trusted. Because we can't trust the
JS or the user not to tamper with their environment, we need to only trust properties that are from
the browser or authenticator, and then signed. As a result, regardless of whom we are, we need to
assume this in our threat models that anything on a webpage, can and will be altered. If the browser
or authenticator are compromised, we have different issues, and different defences.

Insecure Crypto
^^^^^^^^^^^^^^^

Windows Hello especially relies on TPM's that have their attestation signed with sha1. Sha1 is
considered broken, meaning that it could be possible to forge attestations trivially of these
credentials. Newer TPM's may not have this limitation.

Unclear what is / is not security property
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A large limitation of Webauthn is that it is unclear what *is* or *is not* a security property within
the registration and authentication messages. For now, we'll focus on the registration. This is presented
with all the options and structures expanded that are relevant. Imagine you are an identity provider
implementing a webauthn library and you see the following.

::

    PublicKeyCredentialCreationOptions {
        rp = "relying party identifier"
        user {
            id = "user id"
            displayName = "user display name"
        }
        challenge = [0xAB, 0xCD, ... ]
        PublicKeyCredentialParameters = [
            {
                type = "public-key";
                alg ="ECDSA w/ SHA-256" | ... | "RSASSA-PKCS1-v1_5 using SHA-1"
            }, ...
        ]
        timeout = 60000
        excludeCredentials = [
            {
                type = "public-key"
                id = [0x00, 0x01, ... ]
                transports = [ "usb" | "ble" | "internal" | "nfc", ... ]
            }
        ]
        authenticatorSelection = {
            authenticatorAttachment = "platform" | "cross-platform"
            userVerification = "discouraged" | default="preferred" | "required"
            requireResidentKey = boolean
        };
        attestation = default="none" | "indirect" | "direct" | "enterprise"
        extensions = ...
    };

Now, reading this structure, which elements do you think are security properties that you can rely upon
to be strictly enforced, and have cryptographic acknowledgement of that being enforced?

Well, only the following are signed cryptographically by the authenticator:

::

    PublicKeyCredentialCreationOptions {
        rp = "relying party identifier"
        challenge = [0xAB, 0xCD, ... ]
    }

We can assert the credential algorithm used by checking it (provided we are webauthn level 2 compliant
or greater). And we can only check if the userVerification happened or not through the returned attestation.
This means the following aren't signed (for the aware, extensions are something we'll cover seperately).

::

    PublicKeyCredentialCreationOptions {
        user {
            id = "user id"
            displayName = "user display name"
        }
        timeout = 60000
        excludeCredentials = [
            {
                type = "public-key"
                id = [0x00, 0x01, ... ]
                transports = [ "usb" | "ble" | "internal" | "nfc", ... ]
            }
        ]
        authenticatorSelection = {
            authenticatorAttachment = "platform" | "cross-platform"
            requireResidentKey = boolean
        };
    };

This means that from our registration we can not know or assert:

* If an excluded credential was used or not
* If a resident key was really created
* If the created credential is platform or cross platform

Extensions
^^^^^^^^^^

Most extensions are not implemented at all in the wild, making them flat out useless.

Many others are client extensions, meaning they are run in your browser and are not signed, and can
be freely tampered with without verification as javascript is trusted.

Extremely Detailed Use Cases
----------------------------

The use cases we detail here are significantly richer and more detailed than the ones in the `specification <https://www.w3.org/TR/webauthn-3/#sctn-use-cases>`_
(2022-04-13).

Each workflow has two parts. A registration (on-boarding) and authentication. Most of the
parameters for webauthn revolve around the behaviour at registration, with authentication
being a much more similar work flow regardless of credential type.

Security Token (Public)
^^^^^^^^^^^^^^^^^^^^^^^

Registration:

1. The user indicates they wish to enroll a security token
2. The identity provider issues a challenge
3. The browser lists which authenticators attached to the device *could* be registered
4. The user interacts with the authenticator (*note* a pin should not be requested, but fingerprint is okay since it's "transparent")
5. The authenticator releases the signed public key
6. The authenticator is added to the users account

Authentication:

1. The user enters their username
2. The user provides their password and it is validated (*note* we could do this after webauthn)
3. The user indicates they wish to use a security token
4. The identity provider issues a webauthn challenge, limited by the list of authenticators and transports we know are valid for the authenticators associated.
5. The browser offers the list of authenticators that can proceed
6. The user interacts with the authenticator (*note* a pin should not be requested, but fingerprint is okay since it's "transparent")
7. The authenticator releases the signature

Security Token (Corporate)
^^^^^^^^^^^^^^^^^^^^^^^^^^

Registration:

1. The user indicates they wish to enroll a security token
2. The identity provider issues a challenge, with a list of what transports of *known* approved authenticators exist that could be used.
3. The browser lists which authenticators attached to the device *could* be registered, per the transport list
4. The user interacts with the authenticator (*note* a pin should not be requested, but fingerprint is okay since it's "transparent")
5. The authenticator releases the signed public key
6. The identity provider examines the attestation and asserts it is from a trusted manufacturer
7. The identity provider examines the enrollment, and asserts it is bound to the hardware (IE not a passkey/backup)
8. The authenticator is added to the users account

Authentication:

1. As per Security Token (public)

PassKey (Public)
^^^^^^^^^^^^^^^^

Registration:

1. The user indicates they wish to enroll a token
2. The identity provider issues a challenge
3. The browser lists which authenticators attached to the device *could* be registered
4. The user interacts with the authenticator (*note* a pin should not be requested, but fingerprint is okay since it's "transparent")
5. The authenticator releases the signed public key
6. The authenticator is added to the users account

Authentication:

1. The user enters their username
2. The identity provider issues a webauthn challenge, limited by the list of authenticators and transports we know are valid for the authenticators associated.
3. The browser offers the list of authenticators that can proceed
4. The user interacts with the authenticator (*note* a pin should not be requested, but fingerprint is okay since it's "transparent")
5. The authenticator releases the signature

Passwordless (Public)
^^^^^^^^^^^^^^^^^^^^^

Registration:

1. The user indicates they wish to enroll a security token
2. The identity provider issues a challenge
3. The browser lists which authenticators attached to the device *could* be registered
4. The user interacts with the authenticator - user verification MUST be provided i.e. pin or biometric.
5. The authenticator releases the signed public key
6. The identity provider asserts that user verification occured
7. (Optional) The identity provider examines the attestation and asserts it is from a trusted manufacturer
8. The authenticator is added to the users account

Authentication:

1. The user enters their username
2. The identity provider issues a webauthn challenge
3. The browser offers the list of authenticators that can proceed
4. The user interacts with the authenticator - user verification MUST be provided i.e. pin or biometric.
5. The authenticator releases the signature
6. The identity provider asserts that user verification occured

Passwordless (Corporate)
^^^^^^^^^^^^^^^^^^^^^^^^

Registration:

1. The user indicates they wish to enroll a security token
2. The identity provider issues a challenge, with a list of what transports of *known* approved authenticators exist that could be used.
3. The browser lists which authenticators attached to the device *could* be registered, per the transport list
4. The user interacts with the authenticator - user verification MUST be provided i.e. pin or biometric.
5. The authenticator releases the signed public key
6. The identity provider examines the attestation and asserts it is from a trusted manufacturer
7. (Optional) The identity provider asserts that a resident key was created
8. The identity provider examines the enrollment, and asserts it is bound to the hardware (IE not a passkey/backup)
9. The identity provider asserts that user verification occured
10. (Optional) The identity provider asserts the verification method complies to policy
11. The authenticator is added to the users account

Authentication:

1. As per Passwordless (public)

Usernameless
^^^^^^^^^^^^

Registration

1. The user indicates they wish to enroll a security token
2. The identity provider issues a challenge, with a list of what transports of *known* approved authenticators exist that could be used.
3. The browser lists which authenticators attached to the device *could* be registered, per the transport list
4. The user interacts with the authenticator - user verification MUST be provided i.e. pin or biometric.
5. The authenticator releases the signed public key
6. The identity provider examines the attestation and asserts it is from a trusted manufacturer
7. The identity provider asserts that a resident key was created
8. The identity provider examines the enrollment, and asserts it is bound to the hardware (IE not a passkey/backup)
9. The identity provider asserts that user verification occured
10. (Optional) The identity provider asserts the verification method complies to policy
11. The authenticator is added to the users account

Authentication:

1. The identity provider issues a webauthn challenge
2. The browser offers the list of authenticators that can proceed
3. The user interacts with the authenticator - user verification MUST be provided i.e. pin or biometric.
4. The authenticator releases the signature
5. The identity provider asserts that user verification occured
6. The identity provider extracts and uses the provided username that was supplied


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
