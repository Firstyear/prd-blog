+++
title = "How Hype Will Turn Your Security Key Into Junk"
date = 2023-02-02
slug = "2023-02-02-how_hype_will_turn_your_security_key_into_junk"
# This is relative to the root!
aliases = [ "2023/02/02/how_hype_will_turn_your_security_key_into_junk.html" ]
+++
# How Hype Will Turn Your Security Key Into Junk

In the last few months there has been a lot of hype about \"passkeys\"
and how they are going to change authentication forever. But that hype
will come at a cost.

Obsession with passkeys are about to turn your security keys (yubikeys,
feitian, nitrokeys, \...) into obsolete and useless junk.

It all comes down to one thing - resident keys.

## What is a Resident Key

To understand the problem, we need to understand what a
discoverable/resident key is.

You have probably seen that most keys support an \'unlimited\' number of
accounts. This is achieved by sending a \"key wrapped key\" to the
security key. When the Relying Party (Authentication Server) wants to
authenticate your security key, it will provide you a \"credential id\".
That credential ID is an encrypted blob that only your security key can
decrypt. If your security key can decrypt that blob it yields a private
key that is specific to that single RP that you can use for signatures.

    ┌────────────────┐            ┌────────────────┐          ┌────────────────┐ 
    │ Relying Party  │      │     │    Browser     │     │    │  Security Key  │ 
    └────────────────┘            └────────────────┘          └────────────────┘ 
                            │                            │                       
         1. Send                                                                 
       Credential ──────────┼───────▶                    │                       
           IDs                                                                   
                            │      2. Forward to─────────┼─────▶   3. Decrypt    
                                   Security Key                   Credential ID  
                            │                            │       with Master Key 
                                                                        │        
                            │                            │              │        
                                                                        │        
                            │                            │              ▼        
                                                                4. Sign Challenge
                            │                            │       with Decrypted  
                                                                       Key       
                            │                            │              │        
                                                                        │        
                            │                            │              │        
                                                                        ▼        
                            │          6. Return  ◀──────┼───────── 5. Return    
                     ◀──────────────── Signature                    Signature    
                            │                            │                       

This is what is called a non-resident or non-discoverable credential.
The reason is that the private key must be *discovered* by the security
key having the Credential ID provided to it externally. This is because
the private keys are *not resident* inside the security enclave - only
the master key is.

Contrast to this, a resident key or discoverable credential is one where
the private key is *stored* in the security key itself. This allows the
security key to discover (hence the name) what private keys might be
used in the authentication.

    ┌────────────────┐            ┌────────────────┐          ┌────────────────┐ 
    │ Relying Party  │      │     │    Browser     │     │    │  Security Key  │ 
    └────────────────┘            └────────────────┘          └────────────────┘ 
                            │                            │                       
      1. Send Empty                                                              
       CredID list──────────┼───────▶                    │                       
                                     2. Query  ───────────────▶                  
                            │      Security Key          │      3. Discover Keys 
                                                                     for RP      
                            │       4. Select a ◀────────┼─────                  
                                   Security Key                                  
                            │                   ─────────┼────▶ 5. Sign Challenge
                                                                with Resident Key
                            │                            │             │         
                                                                       │         
                            │                            │             │         
                                                                       ▼         
                            │         7. Return  ◀───────┼──────── 6. Return     
                    ◀──────────────── Signature                    Signature     
                            │                            │                       

                            │                            │                       

                            │                            │                       

Now, the primary difference here is that resident/discoverable keys
consume *space* on the security key to store them since they need to
persist - there is no credential id to rely on to decrypt with our
master key!

### Are non-resident keys less secure?

A frequent question here is if non resident keys are less secure than
resident ones. Credential ID\'s as key wrapped keys are secure since
they are encrypted with aes128 and hmaced. This prevents them being
tampered with or decrypted by an external source. If aes128 were broken
and someone could decrypt your private-key in abscence of your security
key, they probably could also break TLS encyrption, attack ssh and do
much worse. Your key wrapped keys rely on the same security features
that TLS relies on.

## Resident Keys and Your Security Key

Now that we know what a resident key is, we can look at how these work
with your security keys.

Since resident keys store their key in the device, this needs to consume
*space* inside the security key. Generally, resident key slots are at a
premium on a security key. Nitrokeys for example only support 8 resident
keys. Yubikeys generally support between 20 and 32. Some keys support
*no* resident keys at all.

The other problem is what CTAP standard your key implements. There are
three versions - CTAP2.0, CTAP2.1PRE and CTAP2.1.

In CTAP2.1 (the latest) you can individually manage, update and delete
specific resident keys from your device.

In CTAP2.0 and CTAP2.1PRE however, you can not. You can not delete a
residentkey without *resetting the whole device*. Resetting the device
also resets your master key, meaning all your non-resident keys will no
longer work either. This makes resident keys on a CTAP2.0 and CTAP2.1PRE
device a serious commitment. You really don\'t want to accidentally fill
up that limited space you have!

In most cases, your key is *very likely* to be CTAP2.0 or CTAP2.1PRE.

## So Why Are Resident Keys a Problem?

On their own, and used carefully resident keys are great for certain
applications. The problem is the hype and obsession with *passkeys*.

In 2022 Apple annouced their passkeys feature on MacOS/iOS allowing the
use of touchid/faceid as a webauthn authenticator similar to your
security key. Probably quite wisely, rather than calling them
\"touchid\" or \"credentials\" or \"authenticators\" Apple chose to have
a nicer name for users. Honestly passkeys is a good name rather than
\"webauthn authenticator\" or \"security key\". It evokes a similar
concept to passwords which people are highly accustomed to, while also
being different enough with the \'key\' to indicate that it operates in
a different way.

The problem (from an external view) is that passkeys was a branding or
naming term of something - but overnight authentication thought leaders
needed to be *on the hype*. \"What is a passkey?\". Since Apple didn\'t
actually define it, this left a void for our thought leaders to answer
that question for users hungry to know \"what indeed is a passkey?\".

As a creator of a relying party and the webauthn library for Rust, we
defined passkeys as the name for \"all possible authenticators\" that a
person may choose to use. We wanted to support the goal to remove and
eliminate passwords, and passkeys are a nice name for this.

Soon after that, some community members took to referring to passkeys to
mean \"credentials that are synchronised between multiple devices\".
This definition is at the least, not harmful, even if it doesn\'t
express that there are many possible types of authenticators that can be
used.

Some months later a person took the stage at FIDO\'s Authenticate
conference and annouced \"a passkey is a resident key\". Because of the
scale and size of the platform, this definition has now stuck. This
definition has become so invasive that even *FIDO* now use it as [their
definition](https://fidoalliance.org/passkeys/#faq).

Part of the reason this definition is hyped is because it works with an
upcoming browser feature that allows autocomplete of a username and
webauthn credential if the key is resident. You don\'t have to type your
username. This now means that we have webauthn libraries pushing for
residentkey as a requirement for all registrations, and many people will
follow this advice without seeing the problem.

The problem is that security keys with their finite storage and lack of
credential management will fill up *rapidly*. In my password manager I
have more than 150 stored passwords. If all of these were to become
resident keys I would need to buy at lesat 5 yubikeys to store all the
accounts, and then another 5-10 as \"backups\". I really don\'t want to
have to juggle and maintain 10 to 15 yubikeys \...

This is an awful user experience to put it mildly. People who choose to
use security keys, now won\'t be able to due to passkeys resident key
requirements. What will also confuse users is this comes on the tail of
FIDO certified keys marketing with statements (which are true with
non-resident keys) like:

*Infinite key pair storage*

*There is no limit to the number of accounts registered in \[redacted\]
FIDO® Security Key.*

To add further insult, an expressed goal of the Webauthn Work Group is
that users should always be free to choose any authenticator they wish
without penalty. Passkeys forcing key residency flies directly in the
face of this.

This leaves few authenticator types which will work properly in this
passkey world. Apples own passkeys, Android passkeys, password managers
that support webauthn, Windows with TPM 2.0, and Chromium based browsers
on MacOS (because of how they use the touchid as a TPM).

## What Can Be Done?

### Submit to the Webauth WG / Browsers to change rk=preferred to exclude security keys

Rather than passkeys being resident keys, passkeys could be expanded to
be all possible authenticators where some subset opportunistically are
resident. This puts passwordless front and center with residency as a
bonus ui/ux for those who opt to use devices that support unlimited
resident keys.

Currently there are three levels of request an RP can make to request
resident keys. Discouraged, Preferred and Required. Here is what happens
with different authenticator types when you submit each level.

    ┌────────────────────┬────────────────────┬────────────────────┐
    │      Roaming       │      Platform      │      Platform      │
    │   Authenticator    │   Authenticator    │   Authenticator    │
    │     (Yubikey)      │(Android Behaviour) │  (iOS Behaviour)   │
    └────────────────────┴────────────────────┴────────────────────┘
    ┌────────────────────┐ ┌────────────────────┬────────────────────┬────────────────────┐
    │                    │ │                    │                    │                    │
    │   rk=discouraged   │ │      RK false      │     RK false       │      RK true       │
    │                    │ │                    │                    │                    │
    ├────────────────────┤ ├────────────────────┼────────────────────┼────────────────────┤
    │                    │ │                    │                    │                    │
    │   rk=preferred     │ │      RK true (!)   │      RK true       │      RK true       │
    │                    │ │                    │                    │                    │
    ├────────────────────┤ ├────────────────────┼────────────────────┼────────────────────┤
    │                    │ │                    │                    │                    │
    │    rk=required     │ │      RK true       │      RK true       │      RK true       │
    │                    │ │                    │                    │                    │
    └────────────────────┘ └────────────────────┴────────────────────┴────────────────────┘

Notice that in rk=preferred the three columns behave the same as
rk=required?

Rather than passkeys setting rk=required, if rk=preferred were softened
so that on preferred meant \"create a resident key only if storage is
unlimited\" then we would have a situation where Android/iOS would
always get resident keys, and security keys would not have space
consumed.

However, so far the WG is resistant to this change. It is not out of the
question that browsers could implement this change externally, but that
would in reality be down to the chrome team to decide.

### Insist on your Passkey library setting rk=discouraged

Rather than rk=required which excludes security keys, rk=discouraged is
the next best thing. Yes it means that android users won\'t get
conditional UI. But what do we prefer - some people have to type a
username (that already has provisions to autocomplete anyway). Or do we
damage and exclude security keys completely?

### Contact FIDO and request RK storage as a certification feature

Currently FIDO doesn\'t mandate any amount of storage requirements for
certified devices. Given that FIDO also seem to want resident keys, then
they should also mandate that certified devices have the ability to
store thousands of resident keys. This way as a consumer you can pick
and select certified devices.

### Something Else?

If you have other ideas on how to improve this let me know!

## Conclusion

The hype around passkeys being resident keys will prevent - or severly
hinder - users of security keys from choosing the authenticator they
want to use online in the future.

