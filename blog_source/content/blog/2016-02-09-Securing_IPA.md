+++
title = "Securing IPA"
date = 2016-02-09
slug = "2016-02-09-Securing_IPA"
# This is relative to the root!
aliases = [ "2016/02/09/Securing_IPA.html", "blog/html/2016/02/09/Securing_IPA.html" ]
+++
# Securing IPA

[I no longer recommend using FreeIPA - Read more
here!](/blog/html/2019/07/10/i_no_longer_recommend_freeipa.html)

By default IPA has some weak security around TLS and anonymous binds.

We can improve this by changing the following options.

    nsslapd-minssf-exclude-rootdse: on
    nsslapd-minssf: 56
    nsslapd-require-secure-binds: on

The last one you may want to change is:

    nsslapd-allow-anonymous-access: on

I think this is important to have on, as it allows non-domain members to
use ipa, but there are arguments to disabling anon reads too.
