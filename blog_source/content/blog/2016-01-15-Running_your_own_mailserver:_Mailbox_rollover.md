+++
title = "Running your own mailserver: Mailbox rollover"
date = 2016-01-15
slug = "2016-01-15-Running_your_own_mailserver:_Mailbox_rollover"
# This is relative to the root!
aliases = [ "2016/01/15/Running_your_own_mailserver:_Mailbox_rollover.html" ]
+++
# Running your own mailserver: Mailbox rollover

UPDATE 2019: Don\'t run your own! Use fastmail instead :D!

I go to a lot of effort to run my own email server. I don\'t like
google, and I want to keep them away from my messages. While it incurs
both financial, and administrative cost, sometimes the benefits are
fantastic.

I like to sort my mail to folders based on server side filters (which
are fantastic, server side filtering is the way to go). I also like to
keep my mailboxes in yearly fashion, so they don\'t grow tooo large. I
keep every email I ever receive, and it\'s saved my arse a few times.

Rolling over year to year for most people would be a pain: You need to
move all the emails from one folder (mailbox) to another, which incurs a
huge time / download / effort cost.

Running your own mailserver though, you don\'t have this issue. It takes
a few seconds to complete a year rollover. You can even script it like I
did.

    #!/bin/bash

    export MAILUSER='email address here'
    export LASTYEAR='2015'
    export THISYEAR='2016'

    # Stop postfix first. this way server side filters aren't being used and mails routed while we fiddle around.
    systemctl stop postfix

    # Now we can fiddle with mailboxes

    # First, we want to make the new archive.

    doveadm mailbox create -u ${MAILUSER} archive.${THISYEAR}

    # Create a list of mailboxes.

    export MAILBOXES=`doveadm mailbox list -u ${MAILUSER} 'INBOX.*' | awk -F '.' '{print $2}'`
    echo $MAILBOXES

    # Now move the directories to archive.
    # Create the new equivalents

    for MAILBOX in ${MAILBOXES}
    do
        doveadm mailbox rename -u ${MAILUSER} INBOX.${MAILBOX} archive.${LASTYEAR}.${MAILBOX}
        doveadm mailbox subscribe -u ${MAILUSER} archive.${LASTYEAR}.${MAILBOX}
        doveadm mailbox create -u ${MAILUSER} INBOX.${MAILBOX}
    done

    doveadm mailbox list -u ${MAILUSER}

    # Start postfix back up

    systemctl start postfix

Now I have clean, shiny mailboxes, all my filters still work, and my
previous year\'s emails are tucked away for safe keeping and posterity.

The only catch with my script is you need to run it on January 1st, else
you get 2016 mails in the 2015 archive. You also still need to move the
inbox contents from 2015 manually to the archive. But it\'s not nearly
the same hassle as moving thousands of mailing list messages around.
