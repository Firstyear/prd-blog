Implementing Webauthn - a series of complexities ...
====================================================

I have recently started to work on a rust webauthn library, to allow servers to be implemented.
However, in this process I have noticed a few complexities to an API that should have so much
promise for improving the state of authentication. So far I can say I have not found any
cryptographic issues, but the design of the standard does raise questions about the ability
for people to correctly implement Webauthn servers.

Odd structure decisions
-----------------------

Webauth is made up of multiple encoding standards. There is a good reason for this, which is that
the json parts are for the webbrowser, and the cbor parts are for ctap and the authenticator
device.

However, I quickly noticed an issue in the Attestation Object, as described here https://w3c.github.io/webauthn/#sctn-attestation .
Can you see the problem?

The problem is that the Authenticator Data relies on hand-parsing bytes, and has two structures that
are concatenated with no length. This means:

* You have to hand parse bytes 0 -> 36
* You then have to CBOR deserialise the Attested Cred Data (if present)
* You then need to serialise the ACD back to bytes and record that length (if your library doesn't tell you how long the amount of data is parsed was).
* Then you need to CBOR deserialise the Extensions.

What's more insulting about this situation is that the Authenticator Data literally is part of
the AttestationObject which is already provided as CBOR! There seems to be no obvious reason for
this to require hand-parsing, as the Authenticator Data which will be signature checked, has it's
byte form checked, so you could have the AttestationObject store authDataBytes, then you can
CBOR decode the nested structure (allowing the hashing of the bytes later).

There are many risks here because now you have requirements to length check all the parameters
which people could get wrong - when CBOR would handle this correctly for you you and provides
a good level of correctness that the structure is altered. I also trust the CBOR parser authors
to do proper length checks too compared to my crappy byte parsing code!

Confusing Naming Conventions and Layout
---------------------------------------

The entire standard is full of various names and structures, which are complex, arbitrarily nested
and hard to see why they are designed this way. Perhaps it's a legacy compatability issue? More likely
I think it's object-oriented programming leaking into the specification, which is a paradigm that
is not universally applicable.

Regardless, it would be good if the structures were flatter, and named better. There are many
confusing structure names throughout the standard, and it can sometimes be hard to identify what
you require and don't require.

Additionally, naming of fields and their use, uses abbrivations to save bandwidth, but makes it
hard to follow. I did honestly get confused about the difference between rp (the relying party
name) and rp_id, where the challenge provides rp, and the browser response use rp_id.

It can be easy to point fingers and say "ohh William, you're just not reading it properly and are
stupid". Am I? Or is it that humans find it really hard to parse data like this, and our brains
are better suited to other tasks? Human factors are important to consider in specification design
both in naming of values, consistency of their use, and appropriate communication as to how
they are used properly. I'm finding this to be a barrier to correct implementation now
(especially as the signature verification section is very fragmented and hard to follow ...).

Crypto Steps seem complex or too static
----------------------------------------

There are a lot of possible choices here - there are 6 attestation formats and 5 attestation
types. As some formats only do some types, there are then 11 verification paths you need to
implement for all possible authenticators. I think this level of complexity will lead to
mistakes over a large number of possible code branch paths, or lacking support for some device
types which people may not have access to.

I think it may have been better to limit the attestation format to one, well defined format,
and within that to limit the attestation types available to suit a more broad range of uses.

It feels a lot like these choice are part of some internal Google/MS/Other internal decisions for
high security devices, or custom deviges, which will be internally used. It's leaked into the spec
and it raises questions about the ability for people to meaningfully implement the full specification
for all possible devices, let alone correctly.

Some parts even omit details in a cryptographic operation, such as `here <https://w3c.github.io/webauthn/#fido-u2f-attestation>`_ in  verification step 2,
it doesn't even list what format the bytes are. (Hint: it's DER x509).


What would I change?
--------------------

* Be more specific

There should be no assumptions about format types, what is in bytes. Be verbose, detailed and without
ambiguity.

* Use type safe, length checked structures.

I would probably make the entire thing a single CBOR structure which contains other nested structures
as required. We should never have to hand-parse bytes in 2019, especially when there is a great
deal of evidence to show the risks of expecting people to do this.

* Don't assume object orientation

I think simpler, flatter structures in the json/cbor would have helped, and been clearer to
implement, rather than the really complex maze of types currently involved.

Summary
-------

Despite these concerns, I still think webauthn is a really good standard, and I really do think
it will become the future of authentication. I'm hoping to help make that a reality in opensource
and I hope that in the future I can contribute to further development and promotion of webauthn.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
