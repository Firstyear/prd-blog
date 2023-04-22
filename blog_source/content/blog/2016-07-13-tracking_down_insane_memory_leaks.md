+++
title = "tracking down insane memory leaks"
date = 2016-07-13
slug = "2016-07-13-tracking_down_insane_memory_leaks"
# This is relative to the root!
aliases = [ "2016/07/13/tracking_down_insane_memory_leaks.html", "blog/html/2016/07/13/tracking_down_insane_memory_leaks.html" ]
+++
# tracking down insane memory leaks

One of the best parts of AddressSanitizer is the built in leak
sanitiser. However, sometimes it\'s not as clear as you might wish!

    I0> /opt/dirsrv/bin/pwdhash hello                            
    {SSHA}s16epVgkKenDHQqG8hrCGhmzqkgx0H1984ttYg==

    =================================================================
    ==388==ERROR: LeakSanitizer: detected memory leaks

    Direct leak of 72 byte(s) in 1 object(s) allocated from:
        #0 0x7f5f5f94dfd0 in calloc (/lib64/libasan.so.3+0xc6fd0)
        #1 0x7f5f5d7f72ae  (/lib64/libnss3.so+0x752ae)

    SUMMARY: AddressSanitizer: 72 byte(s) leaked in 1 allocation(s).

\"Where is /lib64/libnss3.so+0x752ae\" and what can I do with it? I have
debuginfo and devel info installed, but I can\'t seem to see what line
that\'s at.

