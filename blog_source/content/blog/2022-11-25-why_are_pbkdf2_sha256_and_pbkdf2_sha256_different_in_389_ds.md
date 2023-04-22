+++
title = "Why are PBKDF2-SHA256 and PBKDF2_SHA256 different in 389-ds?"
date = 2022-11-25
slug = "2022-11-25-why_are_pbkdf2_sha256_and_pbkdf2_sha256_different_in_389_ds"
# This is relative to the root!
aliases = [ "2022/11/25/why_are_pbkdf2_sha256_and_pbkdf2_sha256_different_in_389_ds.html", "blog/html/2022/11/25/why_are_pbkdf2_sha256_and_pbkdf2_sha256_different_in_389_ds.html" ]
+++
# Why are PBKDF2-SHA256 and PBKDF2_SHA256 different in 389-ds?

In a mailing list discussion recently it came up about what password
hash format should you use in 389-ds. Confusingly we have two PBKDF2
SHA256 implementations, which has a bit of history.

## Too Lazy, Didn\'t Read

Use PBKDF2-SHA256. (hyphen, not underscore).

## What\'s PBKDF2 anyway?

Passwords are a shared-knowledge secret, so knowledge of the password
allows you to authenticate as the person. When we store that secret, we
don\'t want it stored in a form where a person can steal and use it.
This is why we don\'t store passwords cleartext - A rogue admin or a
database breach would leak your passwords (and people do love to re-use
their passwords over many websites \...)

Because of this authentication experts recommend *hashing* your
password. A one-way hash function given an input, will always produce
the same output, but given the hash output, you can not derive the
input.

However, this also isn\'t the full story. Simply hashing your password
isn\'t enough because people have found many other attacks. These
include things like rainbow tables which are a compressed and
precomputed \"lookup\" of hash outputs to their inputs. You can also
bruteforce dictionaries of common passwords to see if they match. All of
these processes for an attacker use their CPU to generate these tables
or bruteforce the passwords.

Most hashes though are designed to be *fast* and in many cases your CPU
has hardware to accelerate and speed these up. All this does is mean
that if you use a *verification hash* for storing passwords then an
attacker just can attack your stored passwords even faster.

To combat this, what authentication experts truly recommend is *key
derivation functions*. A key derivation function is similar to a hash
where an input always yields the same output, but a KDF also intends to
be resource consuming. This can be ram or cpu time for example. The
intent is that an attacker bruteforcing your KDF hashed passwords should
have to expend a large amount of CPU time and resources, while also
producing far fewer results.

## How is this related to - vs \_?

In 389-ds when I implemented PBKDF2_SHA256 I specifically chose to use
the \'\_\' (underscore) to not conflict to \'-\' which is the OpenLDAP
PBKDF2 scheme. We have differences in how we store our PBKDF2_SHA256 in
the userPassword value so they aren\'t compatible. At the time since I
was writing the module in C it was easier to use our own internal format
than to attempt C String manipulation which is a common source of
vulnerabilities. I opted to use a binary array with fixed lengths and
offsets so that we could do bound checks rather than attempting to split
a string with delimiters (and yes, I accounted for endianness in the
design).

The issue however is that after we implemented this we ran into a
problem with NSS (the cryptographic library) that 389-ds uses. NSS
PBKDF2 implementation is flawed, and is 4 times slower (I think, I
can\'t find the original report from RedHat Bugzilla) than OpenSSL for
the same result. This means that for 389-ds to compute a password hash
in say \... 1 second, OpenSSL can do the same in 0.25 seconds. Since we
have response time objectives we wish to meet, this forced 389-ds to use
fewer PBKDF2 rounds, well below the NIST SP800-63b recommendations.

For a long time we accepted this because it was still a significant
improvement over our previous salted sha256 single round implementation,
and we hoped the NSS developers would resolve the issue. However, they
did not fix it and did not accept it was a security issue.

Since then, we\'ve added support for Rust into 389-ds and had a growing
interest to migrate from OpenLDAP to 389-ds. To support this, I added
support for OpenLDAP formatted password hashes to be directly imported
to 389-ds with a Rust plugin called pwdchan that is now part of 389-ds
by default. In this plugin we used the OpenSSL cryptographic provider
which does not have the same limitations as NSS, meaning we can increase
the number of PBKDF2 rounds to the NIST SP800-63b recommendations
without sacrificing large amounts of (wasted) CPU time.

## Conclusion

Use PBKDF2-SHA256.

-   It\'s written in Rust.
-   It meets NIST SP800-63b recommendations.

