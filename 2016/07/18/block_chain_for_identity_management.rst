Block Chain for Identity Management
===================================

On Sunday evening I was posed with a question and view of someone interesting in Block Chain.

*"What do you think of block chain for authentication"*

A very heated debate ensued. I want to discuss this topic at length.

When you roll X ...
===================

We've heard this. "When writing cryptography, don't. If you have to, hire a cryptographer".

*This statement is true for Authentication and Authorisation systems*

"When writing Authentication and Authorisation systems, don't. If you have to, hire an Authentication expert".

Guess what. Authentication and Authorisation are *hard*. Very hard. This is not something for the kids to play with; this is a security critical, business critical, sensitive, scrutinised and highly conservative area of technology.

Glossary
========

First, lets start with some terms. The most apparent thing is this discussion was a clear lack of understanding of Authentication systems and what is involved in them.

* Identity: The representation of "something or someone" in a system.
* Identifier: This maps a name or id to an identity.
* User: The Person or Device that needs to have it's identity asserted.
* Credential: The credential is the token, biometric, private key or other that proves the answer to a question of "Something I am. Something I have. Something I know". A *key* part of this is that an identity may have one or many credentials.
* Credential Validation: This is the process that asserts the requests to consider an authentication attempt valid. Generally this involves the verification of the credentials or *many* credentials in multi factor authentication systems.
* Authentication process: This takes an identifier, such as email, name, or other value, and asserts that the credentials once passing credential validation, belong with the identifier. We can then map to an identity, which by proxy, creates an authenticated user.
* Authorisation: The determination of resources that an authenticated identity is allowed to access.
* Security: Security is Confidentiality, Availability and Integrity.
* External Authentication System / Authentication Provider: Many modern systems, I.E. apps on phone (pokemon go) do *not* implement their own Authentication system. They use an external authentication system, and trust the result and behaviour of that. I.E. you allow the external system to conduct the authentication process and we *trust* the results.
* Authentication Consumer / Consumer: This is the application that consumes the result of the Authentication Provider, and trusts the result in some way.
* Trust Domain: The scope of trust that a set of External Authentication Systems extend to.
* Trust Root / Trusted Third Party: When we provide an identifier and credential we often do this to a system which can assert the validity of the authentication process, and we *trust* the result.

What is blockchain authentication
=================================

Blockchain authentication is essentially an extended form of Public / Private key cryptography. Instead of a centralised third part of trust, we have a decentralised chain of public keys. An application wishing to conduct the authentication process, will refer to the block chain when presented with the users credential and identifier. As we assert trust in the block chain, we then assert the that public key and identity mapping in the chain is valid, and we authenticate the user.

The reason presented by this user for usage of this system.

*"I don't want some third party to be able to add credentials to my account and impersonate me."*

Lets boil this down to its core.

*"I don't want to be impersonated online by a third party"*

This system can be modelled in two ways with blockchain:

System one is that the Blockchain is presented as the Authentication Process system. The Identity itself is stored with the credentials in the blockchain. In this system, a consumer of the Authentication Process that blockchain would provide must still provide Authorisation systems.

System two is that the Blockchain is presenting *only* an Credential Validation system. It is *not* an Authentication system nor an Authorisation system. Any consumers of this system still must implement proper Authentication process to map the validated credential to an identity, and they must implement authorisation systems.

Preventing impersonation
========================

In the first system, we have successfully prevented impersonation of the credential ONLY, despite being an identity storage system. This is dependant on the authentication consumer to implement that policy! There is *no guarantee* that the service cannot have a system which bypasses the blockchain authentication process. Given that these applications will merely call the blockchain as a library, they can easily bypass and inject a *separate* identity system that allows impersonation of the identity. Tricky, hey!

In the second system, we still need an identity mapping service. This will allow the addition of extra credentials to an account to allow impersonation of the identity on the service, at the application layer again.

::

    THIS IS AN UNAVOIDABLE REALITY OF AUTHENTICATION CONSUMER SYSTEMS.

Straight away, we have *already failed the test put upon this system*.

*"I don't want to be impersonated online by a third party"*

The consumer can *always* impersonate any identity on the system, even without credential compromise.

*This is not always a bad thing*

Consider a help desk, or revocation scenario. You *want* your identity to be disabled, or blocked from function via an out of band mechanism. If there is a problem with your account, it is a powerful tool for customer service to see what you see.

Validation of credentials
=========================

The credential validation process in the first and second system are built upon cryptography and the blockchain. It cannot be tampered with etc. I *will not* dispute this.

The issue with Blockchain as validation of credentials comes back to this definition

* Credential: The credential is the token, biometric, private key or other that proves the answer to a question of "Something I am. Something I have. Something I know". A *key* part of this is that an identity may have one or many credentials.

Block chain as an authentication system provides only "Something I have". A single factor of authentication, and is vulnerable to many of the same risks of passwords.

The leading experts of Authentication systems globally are moving towards multiple factor authentication. Being able to satisfy multiple assertions of "something I ...".

If we use Blockchain in the first system we are only able to have a single factor of authentication. This is unacceptable given leading researching into authentication.

If we use Blockchain in the second system, we allow the Authentication Process to have many credentials that *all* must be validated. This is a good thing! However, at this point we are using Blockchain as an over-complex form of public-private key crypto. We still must have the third party of trust able to assert the validity of our multiple credentials! This again leads to "someone can impersonate my account".

Before someone says it. Authentication against two or more block chains is not "multi factor authentication". This is a system where the multiple factors are the SAME. "Something I have", where the thing you have is in the *same location*. Compromise of one credential is equivalent to compromise of the second or further.

A key property of multi factor authentication is that you answer many of the "Something I ..." questions. A password AND a hardware token provides "Something I know" and "Something I have". Having multiple of the same questions can be acceptable provided they are different mediums. Consider phone sms and hardware token. This is still appropriate, as the compromise of one, does not lead to compromise of the other!

Putting a password on your private key is *not* multi factor authentication either. If you think it is, you should not be writing authentication and/or authorisation systems.

Revoking credentials
====================

The ability for an Authentication System to revoke credentials when they are compromised is a key corner stone of correct Authentication Services.

If we examine system one, blockchain as an auth process. Revocation of credentials is semi-possible, and not user friendly. To revoke you need:

* The original private credentials.
* A pre-generated revocation credential.

In *both* cases, we are only appending to the block chain that the public is not to be accepted. We are *not* removing it.

This fails in many ways.

* It violates the right to be forgotten as an identity. Once created, you can never remove the identity.
* If you *loose* the private credential, and have no revocation credential, you CAN NOT prevent exploitation of your account.
* If you *loose* the private credentials, and have lost the revocation credential, you CAN NOT prevent exploitation of your account.
* If you *loose* your account, you CAN NOT recover it. You must create a new identity!
* Revocation lists will be huge. The block chain will be huge. This system will be extremely slow.
* Revocation is permanent. (This may be implementation specific)

There is a reason why CA systems are broken: Revocation lists are broken and not used due to their size and complexity. This system reeks of complexity. When you manage an Authentication system it *must* be simple and it *must* be able to support revocation of credentials even by a trusted third party!

Lets look at the second implementation Blockchain as the credential validation system. This is not *as* bad as the second solution.

* Like the first, you cannot REMOVE a credential from the block chain.
* It is the responsibility of the Authentication Process to implement revocation. I.E. it must maintain a list of valid credentials mapped to identity.
* You revoke in the Authentication Process, not in the Block Chain.

Suddenly, we have a system where to revoke a credential you need to revoke it in *many systems* rather than a true centralised authentication system. This is a critical fault in the case where a credential is lost or compromised. If the credential is revoked in the blockchain, now we have a system where revocations can be in 2 or more places. More complexity!

A proper, centralised system, is able to revoke credentials in the source of truth, and will have immediate lock out effects on the consuming services. Revocations can also be *temporary* or *permanent*.

Revoking credentials in an existing DB backed solution is as simple as logging in and revoking the credential. You can delete the account with no trace remaining. You can also ask the trusted third party, I.E. the operator of the authentication service to revoke your account given your ability to provide identity and authenticate in an out of band manner.

Blockchain is slow
==================

Lets get this out the way. When we go to validate the credentials I will need to maintain a complete copy of the entire blockchain, including revocations. This will be slow! Block chain is not designed for fast search, it's designed for validation of history.

When I need to authenticate an identifier and credentials:

* I need to locate the identifier
* I then validate the credential with the identifier.

Because this may be revoked I will need to assert in the blockchain is this is revoked also. For this to be performant, consumers will pre-index for fast lookup. This takes maintenance. It can be made faster if needed, but it will still not compete with other systems. The issue here is now assertion that the indexes are as valid as the blockchain itself.

This causes a number of other challenges.

* When an authentication request is presented I must always check for new content in the block chain *and index it*.
* If I choose to only update the blockchain cache after a TTL expires, this now opens a window where a revoked credential may still be valid.

Given the insanity of the second option, we will always pursue the former. However, this process is slow and complex. Which will lead to ....

Consumer behaviour and security
===============================

During a HTTP session, you do not continually send your username and password.

The username and password are sent to the authentication process, and validated. If valid, you are sent a token. This token can be replayed to assert your identity.

This means the consumer has two authentication paths.

One, is to validate the identifier and credential, and generate the token.

The second, is to validate the token and it's associated session.

Any system implementing blockchain for authentication will use blockchain in place of username and password. It will then generate a token for that site to continue to use the service.

This means the consumer has a method, to create tokens to *impersonate identites*. This is how cookies on the web work!

No attacker will ever attack the security of the authentication process (unless you royally make a mistake). They will *always* target the application and it's unique vulnerabilities, such as mishandling cookies, xss, injection, incorrect authorisation checks.

*these are not bad things*. This is how the modern web works, and we are getting better at it.

However, it DOES violate the assertion:

*"I don't want to be impersonated online by a third party"*

Blockchain prevents none of these attacks.

Trust domains and trust networks
================================

An argument for this, is that multiple consumers will all trust "The Blockchain" (as if there will only be one).

The reality is that there will be *many*. These will establish isolated authentication domains. They will not trust each other.

Historically LDAP and KRB were designed to allow trust between authentication systems. This never really happened, except between certain networks. The worlds largest single multiple domain trust is EduRoam. EduRoam is the most impressive implementation of this, being that thousands of universities participate and trust the authentication of the others.

The reason that, with the exception of eduroam, this did not take off, is due to policy. A business or site will have a policy that says one or more of:

* "Users must be in X country".
* "They must have an email".
* "They must be X age".
* "They must have parental consent".
* "They must be male/female/dolphin ..".
* "Passwords must match X complexity rules ..."
* .... many more.

Because no one could agree on the same policies applications and services *do not trust* the users created on other services. This is the single fundamental reason why a single internet identity will never be created.

Block chain *does not* solve this problem, nor does it make the implementation of a trust network easier. Consumers of the authentication will still exhibit the same trust policy issues over the system *regardless* of the strength of credentials and their validation process.

"How will this add value to a business"
=======================================

It doesn't. It adds overhead and complexity, as well as a PR disaster waiting to happen.


In conclusion
=============

Block chain for the validation of credentials may be cryptographically sound. However, for credential validation in an Authentication Process, it is not acceptable.

* There will never be a single global blockchain identity store.
* Revocation is complex and potentially impossible.
* Identities can be lost and never recovered.
* It will not scale as the chain grows.
* It doesn't prevent impersonation of identity, only of credential.
* Proper multi factor authentication will be more secure.
* It will be easier to track and trace identities.
* You loose the right to be forgotten.
* Consumers of the authentication are still the weakness.

In my opinion, Blockchain is a *terrible* idea for credential validation: It solves nothing, and only adds complexity in a problem space that we have already solved with multiple factor authentication and a good old fashioned delete key.

Personal notes
==============

This whole discussion, I kept finding more and more issues. When I went away, I found more and more flaws. This will only add "security" in the minds of the crypto nerds who love it. We won't save people during data leaks or breaches. We don't add *real* improvements to security for users or the planet with this. It doesn't even live up to the assertions it's proponents think that hold.

If you seriously are interested in improving the security of your services, investigate and implement multi factor authentication. Investigate and *actually audit* authentication code that exists rather than just hot-airing about blockchain. Most of the issues is *not* in the authentication system, it's in the compromise and data leak that happens to that system en-mass.

Authentication, Authorisation, Security. These are not sexy topics - And I don't want them to be. If you want to really improve the lives of millions, you need to get your hands dirty. You need to be a plumber, not a rock star. If you really want to improve the security and privacy of millions, we need to fix the basics we currently have, instead of adding complexity for complexities sake.

"What makes an elite unit is not that they do anything fancy or complex. They do the basics, over and over, and they do it to 110%"


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
