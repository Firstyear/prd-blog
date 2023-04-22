+++
title = "MBP b43 wireless"
date = 2013-05-02
slug = "2013-05-02-MBP_b43_wireless"
# This is relative to the root!
aliases = [ "2013/05/02/MBP_b43_wireless.html", "blog/html/2013/05/02/MBP_b43_wireless.html" ]
+++
# MBP b43 wireless

I have found recently after about 3.7 that b43 wireless with most access
points is quite flakey. Thankfully, a fellow student, Kram found this
great blog post about getting it to work.

[blog here](http://www.rdoxenham.com/?p=317).

For the moment, you have to rebuild the module by hand on update, but
it\'s a make, make install, dracut away.

The only thing missed is that at the end:

Put the blacklist options into their own wl.conf rather than the main
blacklist for finding them.

You need to rebuild your dracut image. The following should work:

    cd /boot/
    mv initramfs-[current kernel here] initramfs-[kernel].back
    dracut
