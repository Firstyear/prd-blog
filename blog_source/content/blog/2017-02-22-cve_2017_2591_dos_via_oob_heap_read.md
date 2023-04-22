+++
title = "CVE-2017-2591 - DoS via OOB heap read"
date = 2017-02-22
slug = "2017-02-22-cve_2017_2591_dos_via_oob_heap_read"
# This is relative to the root!
aliases = [ "2017/02/22/cve_2017_2591_dos_via_oob_heap_read.html", "blog/html/2017/02/22/cve_2017_2591_dos_via_oob_heap_read.html" ]
+++
# CVE-2017-2591 - DoS via OOB heap read

On 18 of Jan 2017, the following [email found it\'s way to my
notifications](http://seclists.org/oss-sec/2017/q1/129) .

    This is to disclose the following CVE:

    CVE-2017-2591 389 Directory Server: DoS via OOB heap read

    Description :

    The "attribute uniqueness" plugin did not properly NULL-terminate an array
    when building up its configuration, if a so called 'old-style'
    configuration, was being used (Using nsslapd-pluginarg<X> parameters) .

    A attacker, authenticated, but possibly also unauthenticated, could
    possibly force the plugin to read beyond allocated memory and trigger a
    segfault.

    The crash could also possibly be triggered accidentally.

    Upstream patch :
    https://fedorahosted.org/389/changeset/ffda694dd622b31277da07be76d3469fad86150f/
    Affected versions : from 1.3.4.0

    Fixed version : 1.3.6

    Impact: Low
    CVSS3 scoring : 3.7 -- CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L

    Upstream bug report : https://fedorahosted.org/389/ticket/48986

So I decided to pull this apart: Given I found the issue and wrote the
fix, I didn\'t deem it security worthy, so why was a CVE raised?

