+++
title = "GDB: Using memory watch points"
date = 2016-06-11
slug = "2016-06-11-gdb_using_memory_watch_points"
# This is relative to the root!
aliases = [ "2016/06/11/gdb_using_memory_watch_points.html", "blog/html/2016/06/11/gdb_using_memory_watch_points.html" ]
+++
# GDB: Using memory watch points

While programming, we\'ve all seen it.

\"Why the hell is that variable set to 1? It should be X!\"

A lot of programmers would stack print statements around till the find
the issue. Others, might look at function calls.

But in the arsenal of the programmer, is the debugger. Normally, the
debugger, is really overkill, and too complex to really solve a lot of
issues. But while trying to find an issue like this, it shines.

All the code we are about to discuss is [in the liblfdb
git](https://github.com/Firstyear/liblfdb)

