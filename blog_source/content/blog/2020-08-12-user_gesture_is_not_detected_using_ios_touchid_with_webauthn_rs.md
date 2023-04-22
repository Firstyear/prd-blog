+++
title = "User gesture is not detected - using iOS TouchID with webauthn-rs"
date = 2020-08-12
slug = "2020-08-12-user_gesture_is_not_detected_using_ios_touchid_with_webauthn_rs"
# This is relative to the root!
aliases = [ "2020/08/12/user_gesture_is_not_detected_using_ios_touchid_with_webauthn_rs.html", "blog/html/2020/08/12/user_gesture_is_not_detected_using_ios_touchid_with_webauthn_rs.html" ]
+++
# User gesture is not detected - using iOS TouchID with webauthn-rs

I was recently contacted by a future user of
[webauthn-rs](https://github.com/kanidm/webauthn-rs) who indicated that
the library may not currently support Windows Hello as an authenticator.
This is due to the nature of the device being a platform attached
authenticator and that webauthn-rs at the time did not support
attachment preferences.

As I have an ipad, and it\'s not a primary computing device I decided to
upgrade to iPadOS 14 beta to try out webauthn via touch (and handwriting
support).

## The Issue

After watching [Jiewen\'s WWDC
presentation](https://developer.apple.com/videos/play/wwdc2020/10670/)
about using TouchID with webauthn, I had a better idea about some of the
server side requirements to work with this.

Once I started to test though, I would recieve the following error in
the safari debug console.

    User gesture is not detected. To use the platform authenticator,
    call 'navigator.credentials.create' within user activated events.

I was quite confused by this error - a user activated event seems to be
a bit of an unknown term, and asking other people they also didn\'t
quite know what it meant. My demo site was using a button input with
onclick event handlers to call javascript similar to the following:

    function register() {
    fetch(REG_CHALLENGE_URL + username, {method: "POST"})
       .then(res => {
          ... // error handling
       })
       .then(res => res.json())
       .then(challenge => {
         challenge.publicKey.challenge = fromBase64(challenge.publicKey.challenge);
         challenge.publicKey.user.id = fromBase64(challenge.publicKey.user.id);
         return navigator.credentials.create(challenge)
           .then(newCredential => {
             console.log("PublicKeyCredential Created");
                  .... 
             return fetch(REGISTER_URL + username, {
               method: "POST",
               body: JSON.stringify(cc),
               headers: {
                 "Content-Type": "application/json",
               },
             })
           })

This works happily in Firefox and Chrome, and for iPadOS it event works
with my yubikey 5ci.

I investigated further to determine if the issue was in the way I was
presenting the registration to the
[navigator.credentials.create]{.title-ref} function. Comparing to
webauthn.io (which does work with TouchID on iPadOS 14 beta), I noticed
some subtle differences but nothing that should cause an issue like
this.

After much pacing, thinking and asking for help I eventually gave in and
went to the source of webkit

## The Solution

Reading through the webkit source I noted that the check within the code
was looking for association of how the event was initiated. This comes
from a context that is available within the browser. This got me to
think about the fact that the fetch api is *async*, and I realised at
this point that webauthn.io was using the [jQuery.ajax]{.title-ref}
apis. I altered my demo to use the same, and it began to work with
TouchID. That meant that the user activation was being lost over the
async boundary to the fetch API. (note: it\'s quite reasonable to expect
user interaction to use [navigator.credentials]{.title-ref} to prevent
tricking or manipulating users into activating their webauthn devices).

I emailed Jiewen, who responded overnight and informed me that this is
an issue, and it\'s being tracked in the [webkit
bugzilla](https://bugs.webkit.org/show_bug.cgi?id=214722) . He assures
me that it will be resolved in a future release. Many thanks to him for
helping me with this issue!

At this point I now know that TouchID will work with webauthn-rs, and I
can submit some updates to the library to help support this.

## Notes on Webauthn with TouchID

It\'s worth pointing out a few notes from the WWDC talk, and the
differences I have observed with webauthn on real devices.

In the presentation it is recommended that in your Credential Creation
Options, that you (must?) define the options listed to work with TouchID

    authenticatorSelection: { authenticatorAttachment: "platform" },
    attestation: "direct"

It\'s worth pointing out that authenticatorAttachment is only a *hint*
to the client to which credentials it should use. This allows your web
page to streamline the UI flow (such as detection of platform key and
then using that to toggle the authenticatorAttachment), but it\'s not an
enforced security policy. *There is no part of the attestation response
that indicates the attachement method*. The only way to determine that
the authenticator is a platform authenticator would be in attestation
\"direct\" to validate the issuing CA or the device\'s AAGUID match the
expectations you hold for what authenticators can be used within your
organisation or site.

Additionally, TouchID does work with *no* authenticatorAttachment hint
(safari prompts if you want to use an external key or TouchID), and that
[attestation: \"none\"]{.title-ref} also works. This means that a
minimised and default set of Credential Creation Options will allow you
to work with the majority of webauthn devices.

Finally, the WWDC video glosses over the server side process. Be sure to
follow the w3c standard for verifying attestations, or use a library
that implementes this standard (such as
[webauthn-rs](https://github.com/kanidm/webauthn-rs) or [duo-labs go
webauthn](https://github.com/duo-labs/webauthn/)). I\'m sure that other
libraries exist, but it\'s critical that they follow the w3c process as
webauthn is quite complex and fiddly to implement in a correct and
secure manner.

