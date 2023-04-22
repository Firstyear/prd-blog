+++
title = "Slow mac sleep"
date = 2012-04-26
slug = "2012-04-26-Slow_mac_sleep"
# This is relative to the root!
aliases = [ "2012/04/26/Slow_mac_sleep.html", "blog/html/2012/04/26/Slow_mac_sleep.html" ]
+++
# Slow mac sleep

Recently, I have noticed that my shiny macbook pro 8,2, with 16GB of ram
and it\'s super fast intel SSD, was taking quite a long time to sleep -
near 20 seconds to more than a minute in some cases. This caused me
frustration to no avail.

However, recently, in an attempt to reclaim disk space from the SSD, in
the form of a wasted 16GB chunk in /private/var/vm/sleepimage . This
lead me to read the documentation on pmutil.

hibernate mode is set to 3 by default - this means that when you close
the lid on your MBP, it dumps the contents of ram to sleepimage, and
then suspends to ram. This means in the case that you lose power while
suspended, you can still restore your laptop state safely. I don\'t feel
I need this, so I ran the following. :

    sudo pmset -a hibernatemode 0
    sudo rm /private/var/vm/sleepimage

Now I have saved 16GB of my SSD (And read write cycles) and my MBP
sleeps in 2 seconds flat.
