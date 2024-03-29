+++
title = "Enable caBLE on your iPhone for testing"
date = 2022-04-04
slug = "2022-04-04-enable_cable_on_your_iphone_for_testing"
# This is relative to the root!
aliases = [ "2022/04/04/enable_cable_on_your_iphone_for_testing.html", "blog/html/2022/04/04/enable_cable_on_your_iphone_for_testing.html" ]
+++
# Enable caBLE on your iPhone for testing

caBLE allows a nearby device (such as your iPhone) to be used an a
webauthn authenticator. Given my work on
[WebauthnRS](https://github.com/kanidm/webauthn-rs) I naturally wanted
to test this! When I initially tried to test caBLE with webauthn via my
iPhone, I recieved an error that the operation wasn\'t available at this
time. There was no other information available.

## Debugging

After some digging into Console.app, I found the log message from
AuthenticationServicesAgent which stated:

*\"Syncing platform authenticator must be enabled to register a platform
public key credential; this can be enabled in Settings \> Developer.\"*

## Enabling Developer Settings

Run Xcode.app on your mac. On your iPhone close and reopen settings.
Then search for \"developer\".

Inside of that menu enable [Syncing Platform Authenticator]{.title-ref}
and [Additional Logging]{.title-ref} under [PassKit]{.title-ref}.

After that you should be able to test caBLE!

