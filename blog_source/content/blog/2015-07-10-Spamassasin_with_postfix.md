+++
title = "Spamassasin with postfix"
date = 2015-07-10
slug = "2015-07-10-Spamassasin_with_postfix"
# This is relative to the root!
aliases = [ "2015/07/10/Spamassasin_with_postfix.html" ]
+++
# Spamassasin with postfix

I run my own email servers for the fun of it, and to learn about the
best practices etc. I\'ve learnt a lot about email as a result so the
exercise has paid off.

For about 2 years, I had no spam at all. But for some reason about 5
months ago, suddenly my email address was found, and spam ensued. I
didn\'t want to spend my life hand filtering out the spam, so enter
spamasssasin.

My mail server config itself is the subject of a different post. Today
is just about integrating in spamassassin with postfix.

First, make sure we have all the packages we need. I\'m a centos/fedora
user, so adjust as needed.

    yum install postfix spamass-milter spamassassin

The default spamassassin configuration is good, but I\'m always open to
ideas on how to improve it.

Now we configure postfix to pass mail through the spamassasin milter.

postfix/main.cf :

    smtpd_milters = unix:/run/spamass-milter/postfix/sock

Now, enable our spamassasin and postfix service

    systemctl enable spamass-milter
    systemctl enable postfix

Now when you recieve email from spamers, they should be tagged with
\[SPAM\].

I use dovecot sieve filters on my mailbox to sort these emails out into
a separate spam folder.

One of the best things that I learnt with spamassassin is that it\'s
bayesian filters are very powerful if you train them.

So I setup a script to help me train the spamassasin bayesian filters.
This relies heavily on you as a user manually moving spam that is
\"missed\" from your inbox into your spam folder. You must move it all
else this process doesn\'t work!

    cd /var/lib/dovecot/vmail/william
    sa-learn --progress --no-sync --ham {.,.INBOX.archive}/{cur,new}
    sa-learn --progress --no-sync --spam .INBOX.spam/{cur,new}
    sa-learn --progress --sync

First, we learn \"real\" messages from our inbox and our inbox archive.
Then we learn spam from our spam folders. Finally, we commit the new
bayes database.

This could be extended to multiple users with:

    cd /var/lib/dovecot/vmail/
    sa-learn --progress --no-sync --ham {william,otheruser}/{.,.INBOX.archive}/{cur,new}
    sa-learn --progress --no-sync --spam {william,otheruser}/.INBOX.spam/{cur,new}
    sa-learn --progress --sync

Of course, this completely relies on that user ALSO classifying their
mail correctly!

However, all users will benefit from the \"learning\" of a few dedicated
users.

Some other golden tips for blocking spam, are to set these in postfix\'s
main.cf. Most spammers will violate some of these rules at some point. I
often see many blocked because of the invalid helo rules.

Note, I don\'t do \"permit networks\" because of the way my load
balancer is configured.

main.cf :

    smtpd_delay_reject = yes
    smtpd_helo_required = yes
    smtpd_helo_restrictions =
        reject_non_fqdn_helo_hostname,
        reject_invalid_helo_hostname,
        permit
    smtpd_relay_restrictions = permit_sasl_authenticated reject_unauth_destination reject_non_fqdn_recipient reject_unknown_recipient_domain reject_unknown_sender_domain
    smtpd_sender_restrictions =
        reject_non_fqdn_sender,
        reject_unknown_sender_domain,
        permit
    smtpd_recipient_restrictions = reject_unauth_pipelining reject_non_fqdn_recipient reject_unknown_recipient_domain permit_sasl_authenticated reject_unauth_destination permit

Happy spam hunting!
