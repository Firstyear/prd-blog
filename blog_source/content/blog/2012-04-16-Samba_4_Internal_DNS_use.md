+++
title = "Samba 4 Internal DNS use"
date = 2012-04-16
slug = "2012-04-16-Samba_4_Internal_DNS_use"
# This is relative to the root!
aliases = [ "2012/04/16/Samba_4_Internal_DNS_use.html" ]
+++
# Samba 4 Internal DNS use

It took me a while to find this in an email from a mailing list.

To use the internal DNS from samba4 rather than attempting to use BIND9
append the line \"\--dns-backend=SAMBA_INTERNAL\" to your provision
step.
