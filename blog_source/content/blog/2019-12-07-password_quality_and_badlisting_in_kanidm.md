+++
title = "Password Quality and Badlisting in Kanidm"
date = 2019-12-07
slug = "2019-12-07-password_quality_and_badlisting_in_kanidm"
# This is relative to the root!
aliases = [ "2019/12/07/password_quality_and_badlisting_in_kanidm.html" ]
+++
# Password Quality and Badlisting in Kanidm

Passwords are still a required part of any IDM system. As much as I wish
for Kanidm to only support webauthn and stronger authentication types,
at the end of the day devices can be lost, destroyed, some people may
not be able to afford them, some clients aren\'t compatible with them
and more.

This means the current state of the art is still multi-factor auth.
Something you have and something you know.

Despite the presence of the multiple factors, it\'s still important to
quality check passwords. Microsoft\'s Azure security team [have written
about
passwords](https://techcommunity.microsoft.com/t5/Azure-Active-Directory-Identity/Your-Pa-word-doesn-t-matter/ba-p/731984),
and it really drives home the current situation. I would certainly trust
these people at Microsoft to know what they are talking about given the
scale of what they have to defend daily.

The most important take away is that trying to obscure the password from
a bruteforce is a pointless exercise because passwords end up in
password dumps, they get phished, keylogged, and more. MFA matters!

It\'s important here to look at the \"easily guessed\" and \"credential
stuffing\" category. That\'s what we really want to defend against with
password quality, and MFA protects us against keylogging, phising (only
webauthn), and reuse.

## Can we Avoid This?

Yes! Kanidm supports a \"generated\" password that is a long, high
entropy password that should be stored in a password manager or similar
tool to prevent human knowledge. This fits to our \"device as
authentication\" philosophy. You authenticate to your device (phone,
laptop etc), and then the devices stored passwords authenticate you from
that point on. This has the benefit that devices and password managers
generally perform better checking of the target where we enter the
password, making phising less likely.

But sometimes we can\'t rely on this, so we still need human-known
passwords, so we still take steps to handle these.

## Quality

In the darkages, we would decree that human known passwords had to have
a number, symbol, roman numeral, no double letters, one capital letter,
two kanji and no symbols that could be part of an sql injection because
of that one legacy system we can\'t patch.

This lead to people making horrid, un-rememberable passwords in
leetspeak, or giving up altogether and making the excellent
\"Password1\" (which passes AD minimum password requirements on server
2003).

What we really want is entropy, length, and memorability. Dropbox made a
great library for this called zxcvbn, which has since [been ported to
rust](https://docs.rs/zxcvbn/2.0.0/zxcvbn/index.html) . I highly
recommend it.

This library is great because it focuses on entropy, and then if the
password doesn\'t meet these requirements, the library recommends ways
to improve. This is excellent for human interaction and experience,
guiding people to create better passwords that they can remember, rather
than our outdated advice of the complex passwords as described above.

## Badlisting

Badlisting is another great technique for improving password quality.
It\'s essentially a blocklist of passwords that people are not allowed
to set. This way you can have corporate-specific breach lists, or the
top 10k most used passwords badlisted to prevent users using them. For
example, \"correct horse battery staple\" may be a strong password, but
it\'s well known thanks to xkcd.

It\'s also good for preventing password reuse in your company if you are
phished and the credentials privately notified to you as some of the
regional CERT\'s do, allowing you to block these without them being in a
public breach list.

This is important as many bots will attempt to spam these passwords
against accounts (rate limiting auth and soft-locking accounts also
helps to delay these attack styles).

## In Kanidm

In Kanidm, we chose to use both approaches. First we check the password
with zxcvbn, then we ensure it\'s not in a badlist.

In order to minimise the size of the badlist, the badlist uses case
insensitive storage so that multiple variants of \"password\" and
\"PasSWOrD\" are only listed once. We also preprocessed the badlist with
zxcvbn to remove any passwords that it would have denied from being
entered. The preprocessor tool will be shipped with kanidm so that
administrators can preprocess their own lists before adding them to the
badlist configuration.

## Creating a Badlist

I decided to do some analysis on a well known set of passwords
maintained on the [seclists
repository](https://github.com/danielmiessler/SecLists/tree/master/Passwords)
. Apparently this is what pentesters reach for when they want to
bruteforce or credential stuff on a domain.

I analysed this in three ways. The first was as a full set of passwords
(about 25 million) and a smaller but \"popular\" set in the \"rockyou\"
files which is about 60,000 passwords. Finally I did an analysis of the
rockyou + top 10 million most common (which combined was 1011327 unique
passwords, so about 50k of the rockyou set is from top 10 million).

From the 25 million set I ran this through a preprocessor tool that I
developed for kanidm. It eliminated anything less than a score of 3 and
no length rule. This showed that zxcvbn was able to prevent 80% of these
inputs from being allowed. If I was to ship this full list, this would
contain 4.8 million badlisted passwords. It\'s pretty amazing already
that zxcvbn stops 80% of bad passwords that end up in breaches from
being able to be used, with the remaining 20% likely to be complex
passwords that just got dumped by other means.

However, for the badlist in Kanidm, I decided to start with \"what\'s
popular\" for now, and to allow sites to add extra content if they
desire. This meant that I focused instead on the \"rockyou\" password
set instead.

From the rockyou set I did more tests. zxcvbn has a concept of scores,
and we can have policy to request a minimum score is present to allow
the password. I did a score 3 test, a score 3 with min pw len 10 and a
score 4 test. This showed the following results which has the % blocked
by zxcvbn and the no. that passed which will required badlisting as
zxcvbn can\'t detect them (today).

    TEST     | % blocked | no. passed
    ---------------------------------
     s3      |  98.3%    |  1004
     s3 + 10 |  98.9%    |  637
     s4      |  99.7%    |  133

Personally, it\'s quite hilarious that \"2fast2furious\" passed the
score 3 check, and \"30secondstomars\" and \"dracomalfoy\" passed the
score 4 check, but who am I to judge - that\'s what bad lists are for.

More seriously, I found it interesting to see the effect of the check on
length - not only was the preprocessor step faster, but alone that
eliminated \~400 passwords that would have \"passed\" on score 3.

Finally, from the rockyou + 10m set, the results show the following in
the same conditions.

    TEST     | % blocked | no. passed
    ---------------------------------
     s3      |  89.9%    |  101349
     s3 + 10 |  92.4%    |  76425
     s4      |  96.5%    |  34696

This shows that a very \"easy\" win is to enforce password length, in
addition to entropy checkers like zxcvbn, which are effective to block
92% of the most common passwords in use on a broad set and 98% of what a
pentester will look for (assuming rockyou lists). If you have a high
security environment you should consider setting zxcvbn to request
passwords of score 4 (the maximum), given that on the 10m set it had a
96.5% block rate.

## Conclusions

You should use zxcvbn, it\'s a great library, which quickly reduces a
huge amount of risk from low quality passwords.

After that your next two strongest controls are password length, and
being able to support badlisting.

Better yet, use MFA like Webauthn as well, and support server-side
generated high-entropy passwords!

