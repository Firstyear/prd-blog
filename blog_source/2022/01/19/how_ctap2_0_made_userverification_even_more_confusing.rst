How CTAP2.0 made UserVerification even more confusing
=====================================================

I have previously written about how
`Webauthn introduces a false sense of security <../../../2020/11/21/webauthn_userverificationpolicy_curiosities.html>`_
with how it manages UserVerification (UV) by default. To summarise, when you request "preferred" which
means "perform UV if possible", it can be bypassed since relying parties's (RP) do *not* check if
UV was actually performed, and Webauthn makes no recommendations on how to store credentials
in a manner that allows future checking to ensure UV is requested or validated correctly.

From this, in Webauthn-RS we made the recommendation that you use either "required" to enforce
all credentials have performed UV, or "discouraged" to request that *no* UV is performed by
credentials during authentication or registration.

At the same time, in the Webauthn-RS project we begun to store two important pieces of credential
metadata beyond the Webauthn specification - the result of UV from registration, and
the policy that was requested at the time of registration. We did this because we had noticed
there were classes of credentials, that even in "discouraged" would always verify themself at
registration and authentication. Because of this property, we would enforce that since UV was performed
at registration, we could continue to enforce UV on a per credential basis to detect possible
credential compromise, and to further strengthen the security of credentials used with Webauthn-RS.

This created 3 workflows:

* Required - At registration and authentication UV is always required
* Discouraged + no UV - At registration and authentication UV is never required
* Discouraged + always UV - At registration and authentication UV is always required

A bug report ...
----------------

We recieved a bug that an authenticator was failing to work with Webauthn-RS, because at registration
it would always force UV, but during authentication it would *never* request UV. This was triggering
our inconsistent credential detection, indicating the credential was possibly compromised.

In this situation, the authenticator used an open-source firmware, so I was able to look at the source
and identify the programming issue. During registration UV is *always* required, but during "discouraged"
in authentication it's *never* required matching the reported bug.

The author of the library then directed me to the fact that
in `CTAP2.0 <https://fidoalliance.org/specs/fido-v2.0-ps-20190130/fido-client-to-authenticator-protocol-v2.0-ps-20190130.html#authenticatorMakeCredential>`_
this behaviour is *enshrined in the specification*.

Why is this behaviour bad?
--------------------------

I performed a quick poll on twitter, and asked about 5 non-technical friends about this. The question
I asked was:

*You go to a website, and you’re asked to setup a yubikey. When you register the key you’re asked for a pin. Do you now expect the pin to be required when you authenticate to that website with that yubikey now?*

From the 31 votes on twitter, the result was 60% (21 / 30) that "yes" this PIN will always be required. From
the people I asked directly, they all responded "yes". (This is in no way an official survey or
significant numbers, but it's an initial indication)

Humans expect things to behave in a *consistent* manner. When you take
an action one time, something will always continue to behave in that way. The issue we are presented with
in this situation is that CTAP2.0 fundamentally breaks this association by changing the behaviour between
registration and authentication. It also is not communicated that the different is registration
vs authentication, or even *why* this behaviour is changed.

As a result, this confuses users ("Why is my pin not always required?!") and this can at worst cause
users to be apathetic about the UV check, where it could be downgraded from "required/preferred" to
"discouraged" and the user would not notice or care about "why is this different?". Because RP's that
strictly follow the Webauthn specification are open to UV bypass, CTAP2.0 in this case has helped
to open the door for users to be tricked into this.

The other issue is that for a library like Webauthn-RS we lose the ability to detect credential compromise
or attempts to bypass UV when in discouraged, since now UV is not consistently enforced across all
classes of authenticators.

Can it be fixed?
----------------

No. There are changes in CTAP2.1 that can set the token to be "always verified" and for extensions
to be sent that always enforce UV of that credential, but none of these assist the CTAP2.0 case
where none of these elements exist.

As an RP library author we have to assume and work out ways to interact with credentials that are CTAP2.0_pre,
CTAP2.0, CTAP2.1, vendor developed and more. We have to find a way to use the elements at hand to create
a consistent user interface, that also embed security elements that can not be bypassed or downgraded.

I spent a lot of time thinking about how to resolve this, but I can only conclude that CTAP2.0 has
made "discouraged" less meaningful by adding in this confusing behaviour.

Is this the end of the world?
-----------------------------

Not at all. But it does undermine users trust in the systems we are building, where people may
end up believing that UV is pointless and never checked. There are a lot of smart bad-people out
there and they may utilise this in attacks (especially when combined with the
fact that RP's who strictly follow the Webauthn standard are already open to UV bypass in many cases).

If the goal we have is to move to a passwordless world, we need people to trust their devices behave
in a manner that is predictable and that they understand. By making UV sometimes there, sometimes not,
it will be a much higher barrier to convince people they can trust these devices as a self contained
multifactor authenticator.

I use an authentication provider, what can I do?
------------------------------------------------

If possible, setup your authentication provider to have UV required. This will cause some credentials
to no longer work in your environment, but it will ensure that every authenticator has a consistent
experience. In most cases, your authentication provider is likely to be standards compliant, and will
not perform the extended verification discussed below meaning that "preferred" is bypassable, and
"discouraged" can have inconsistent UV requests from users.

What can an RP do?
------------------

Because of this change, there are really only three workflows now that are actually consistent for
users where we can enforce UV properties are observed correctly.

* Required - At registration and authentication UV is always required
* Preferred + with UV - At registration and authentication UV is always required
* Preferred + no UV - At registration and authentication UV should not be required

The way that this is achieved is an extension to the Webauthn specification. When you register a credential
you *must* store the state of the UV boolean at registration, and you *must* store the policy
that was requested at registration. During authentication the following is checked in place of the webauthn
defined UV check:

::

    if credential.registration_policy == required OR authentication.policy == required {
        assert(authentication.uv == true)
    } else if credential.registration_policy == preferred AND credential.registration_uv == true {
        // We either sent authentication.policy preferred or discouraged, but the user registered
        // with UV so we enforce that behaviour.
        assert(authentication.uv == true)
    } else {
        // Do not check uv.
    }

There is a single edge case in this work flow - since we now send "preferred" it's possible that a credential
that registered without UV (IE via Firefox which doesn't support CTAP2.0_pre or greater) will be moved
to using a platform that does support CTAP2.0_pre or greater, and it will begin to request UV. It is however
possible in this scenario that once the credential begins to provide UV we can then store the credential.uv as
true and enforce that for future authentications. 

The primary issue with this is that we will begin to ask for the user's PIN more often with credentials
which may lead to frustration. Biometrics this is less of a concern as the "touch" action is always
required anyway. However I think this is acceptable since it's more important for a consistent set
of behaviours to exist.

Previously I have stated that "preferred" should not be used since it is bypassable, but with the
extensions to Webauthn above where policy and uv at registration are stored and validated, preferred
gains a proper meaning and can be checked and enforced.

Conclusion
----------

In the scenarioes where "discouraged" and "preferred" may be used, UV is meaningless in the current
definition of the Webauthn specification when paired with the various versions of CTAP.
It's merely a confusing annoyance that we present to users seemingly at random, that is trivially
bypassed, adds little to no security value and at worst undermines user trust in the systems we are
trying to build.

When we are building authentication systems, we must always think about and consider
the humans who will be using these systems, and the security properties that we actually provide
in these systems.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
