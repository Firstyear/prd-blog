+++
title = "So you want to script gdb with python ..."
date = 2017-08-04
slug = "2017-08-04-so_you_want_to_script_gdb_with_python"
# This is relative to the root!
aliases = [ "2017/08/04/so_you_want_to_script_gdb_with_python.html" ]
+++
# So you want to script gdb with python \...

Gdb provides a python scripting interface. However the documentation is
highly technical and not at a level that is easily accessible.

This post should read as a tutorial, to help you understand the
interface and work toward creating your own python debuging tools to
help make gdb usage somewhat \"less\" painful.

## The problem

I have created a problem program called \"naughty\". You can find it
[here](../../../_static/gdb_py/naughty.c) .

You can compile this with the following command:

    gcc -g -lpthread -o naughty naughty.c

When you run this program, your screen should be filled with:

    thread ...
    thread ...
    thread ...
    thread ...
    thread ...
    thread ...

It looks like we have a bug! Now, we could easily see the issue if we
looked at the C code, but that\'s not the point here - lets try to solve
this with gdb.

    gdb ./naughty
    ...
    (gdb) run
    ...
    [New Thread 0x7fffb9792700 (LWP 14467)]
    ...
    thread ...

Uh oh! We have threads being created here. We need to find the problem
thread. Lets look at all the threads backtraces then.

    Thread 129 (Thread 0x7fffb3786700 (LWP 14616)):
    #0  0x00007ffff7bc38eb in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
    #1  0x00000000004007bc in lazy_thread (arg=0x7fffffffdfb0) at naughty.c:19
    #2  0x00007ffff7bbd3a9 in start_thread () from /lib64/libpthread.so.0
    #3  0x00007ffff78e936f in clone () from /lib64/libc.so.6

    Thread 128 (Thread 0x7fffb3f87700 (LWP 14615)):
    #0  0x00007ffff7bc38eb in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
    #1  0x00000000004007bc in lazy_thread (arg=0x7fffffffdfb0) at naughty.c:19
    #2  0x00007ffff7bbd3a9 in start_thread () from /lib64/libpthread.so.0
    #3  0x00007ffff78e936f in clone () from /lib64/libc.so.6

    Thread 127 (Thread 0x7fffb4788700 (LWP 14614)):
    #0  0x00007ffff7bc38eb in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
    #1  0x00000000004007bc in lazy_thread (arg=0x7fffffffdfb0) at naughty.c:19
    #2  0x00007ffff7bbd3a9 in start_thread () from /lib64/libpthread.so.0
    #3  0x00007ffff78e936f in clone () from /lib64/libc.so.6

    ...

We have 129 threads! Anyone of them could be the problem. We could just
read these traces forever, but that\'s a waste of time. Let\'s try and
script this with python to make our lives a bit easier.

## Python in gdb

Python in gdb works by bringing in a copy of the python and injecting a
special \"gdb\" module into the python run time. You can *only* access
the gdb module from within python if you are using gdb. You can not have
this work from a standard interpretter session.

We can access a dynamic python runtime from within gdb by simply calling
python.

    (gdb) python
    >print("hello world")
    >hello world
    (gdb)

The python code only runs when you press Control D.

Another way to run your script is to import them as \"new gdb
commands\". This is the most useful way to use python for gdb, but it
does require some boilerplate to start.

    import gdb

    class SimpleCommand(gdb.Command):
        def __init__(self):
            # This registers our class as "simple_command"
            super(SimpleCommand, self).__init__("simple_command", gdb.COMMAND_DATA)

        def invoke(self, arg, from_tty):
            # When we call "simple_command" from gdb, this is the method
            # that will be called.
            print("Hello from simple_command!")

    # This registers our class to the gdb runtime at "source" time.
    SimpleCommand()

We can run the command as follows:

    (gdb) source debug_naughty.py
    (gdb) simple_command
    Hello from simple_command!
    (gdb)

## Solving the problem with python

So we need a way to find the \"idle threads\". We want to fold all the
threads with the same frame signature into one, so that we can view
anomalies.

First, let\'s make a \"stackfold\" command, and get it to list the
current program.

    class StackFold(gdb.Command):
    def __init__(self):
        super(StackFold, self).__init__("stackfold", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        # An inferior is the 'currently running applications'. In this case we only
        # have one.
        inferiors = gdb.inferiors()
        for inferior in inferiors:
            print(inferior)
            print(dir(inferior))
            print(help(inferior))

    StackFold()

To reload this in the gdb runtime, just run \"source debug_naughty.py\"
again. Try running this: Note that we dumped a heap of output? Python
has a neat trick that dir and help can both return strings for printing.
This will help us to explore gdb\'s internals inside of our program.

We can see from the inferiors that we have threads available for us to
interact with:

    class Inferior(builtins.object)
     |  GDB inferior object
    ...
     |  threads(...)
     |      Return all the threads of this inferior.

Given we want to fold the stacks from all our threads, we probably need
to look at this! So lets get one thread from this, and have a look at
it\'s help.

    inferiors = gdb.inferiors()
    for inferior in inferiors:
        thread_iter = iter(inferior.threads())
        head_thread = next(thread_iter)
        print(help(head_thread))

Now we can run this by re-running \"source\" on our script, and calling
stackfold again, we see help for our threads in the system.

At this point it get\'s a little bit less obvious. Gdb\'s python
integration relates closely to how a human would interact with gdb. In
order to access the content of a thread, we need to change the gdb
context to access the backtrace. If we were doing this by hand it would
look like this:

    (gdb) thread 121
    [Switching to thread 121 (Thread 0x7fffb778e700 (LWP 14608))]
    #0  0x00007ffff7bc38eb in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
    (gdb) bt
    #0  0x00007ffff7bc38eb in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
    #1  0x00000000004007bc in lazy_thread (arg=0x7fffffffdfb0) at naughty.c:19
    #2  0x00007ffff7bbd3a9 in start_thread () from /lib64/libpthread.so.0
    #3  0x00007ffff78e936f in clone () from /lib64/libc.so.6

We need to emulate this behaviour with our python calls. We can swap to
the thread\'s context with:

    class InferiorThread(builtins.object)
     |  GDB thread object
    ...
     |  switch(...)
     |      switch ()
     |      Makes this the GDB selected thread.

Then once we are in the context, we need to take a different approach to
explore the stack frames. We need to explore the \"gdb\" modules raw
context.

    inferiors = gdb.inferiors()
    for inferior in inferiors:
        thread_iter = iter(inferior.threads())
        head_thread = next(thread_iter)
        # Move our gdb context to the selected thread here.
        head_thread.switch()
        print(help(gdb))

Now that we have selected our thread\'s context, we can start to explore
here. gdb can do a lot within the selected context - as a result, the
help output from this call is really large, but it\'s worth reading so
you can understand what is possible to achieve. In our case we need to
start to look at the stack frames.

To look through the frames we need to tell gdb to rewind to the
\"newest\" frame (ie, frame 0). We can then step down through
progressively older frames until we exhaust. From this we can print a
rudimentary trace:

    head_thread.switch()

    # Reset the gdb frame context to the "latest" frame.
    gdb.newest_frame()
    # Now, work down the frames.
    cur_frame = gdb.selected_frame()
    while cur_frame is not None:
        print(cur_frame.name())
        # get the next frame down ....
        cur_frame = cur_frame.older()

    (gdb) stackfold 
    pthread_cond_wait@@GLIBC_2.3.2
    lazy_thread
    start_thread
    clone

Great! Now we just need some extra metadata from the thread to know what
thread id it is so the user can go to the correct thread context. So
lets display that too:

    head_thread.switch()

    # These are the OS pid references.
    (tpid, lwpid, tid) = head_thread.ptid
    # This is the gdb thread number
    gtid = head_thread.num
    print("tpid %s, lwpid %s, tid %s, gtid %s" % (tpid, lwpid, tid, gtid))
    # Reset the gdb frame context to the "latest" frame.

    (gdb) stackfold
    tpid 14485, lwpid 14616, tid 0, gtid 129

At this point we have enough information to fold identical stacks.
We\'ll iterate over every thread, and if we have seen the \"pattern\"
before, we\'ll just add the gdb thread id to the list. If we haven\'t
seen the pattern yet, we\'ll add it. The final command looks like:

    def invoke(self, arg, from_tty):
        # An inferior is the 'currently running applications'. In this case we only
        # have one.
        stack_maps = {}
        # This creates a dict where each element is keyed by backtrace.
        # Then each backtrace contains an array of "frames"
        #
        inferiors = gdb.inferiors()
        for inferior in inferiors:
            for thread in inferior.threads():
                # Change to our threads context
                thread.switch()
                # Get the thread IDS
                (tpid, lwpid, tid) = thread.ptid
                gtid = thread.num
                # Take a human readable copy of the backtrace, we'll need this for display later.
                o = gdb.execute('bt', to_string=True)
                # Build the backtrace for comparison
                backtrace = []
                gdb.newest_frame()
                cur_frame = gdb.selected_frame()
                while cur_frame is not None:
                    backtrace.append(cur_frame.name())
                    cur_frame = cur_frame.older()
                # Now we have a backtrace like ['pthread_cond_wait@@GLIBC_2.3.2', 'lazy_thread', 'start_thread', 'clone']
                # dicts can't use lists as keys because they are non-hashable, so we turn this into a string.
                # Remember, C functions can't have spaces in them ...
                s_backtrace = ' '.join(backtrace)
                # Let's see if it exists in the stack_maps
                if s_backtrace not in stack_maps:
                    stack_maps[s_backtrace] = []
                # Now lets add this thread to the map.
                stack_maps[s_backtrace].append({'gtid': gtid, 'tpid' : tpid, 'bt': o} )
        # Now at this point we have a dict of traces, and each trace has a "list" of pids that match. Let's display them
        for smap in stack_maps:
            # Get our human readable form out.
            o = stack_maps[smap][0]['bt']
            for t in stack_maps[smap]:
                # For each thread we recorded
                print("Thread %s (LWP %s))" % (t['gtid'], t['tpid']))
            print(o)

Here is the final output.

    (gdb) stackfold
    Thread 129 (LWP 14485))
    Thread 128 (LWP 14485))
    Thread 127 (LWP 14485))
    ...
    Thread 10 (LWP 14485))
    Thread 9 (LWP 14485))
    Thread 8 (LWP 14485))
    Thread 7 (LWP 14485))
    Thread 6 (LWP 14485))
    Thread 5 (LWP 14485))
    Thread 4 (LWP 14485))
    Thread 3 (LWP 14485))
    #0  0x00007ffff7bc38eb in pthread_cond_wait@@GLIBC_2.3.2 () from /lib64/libpthread.so.0
    #1  0x00000000004007bc in lazy_thread (arg=0x7fffffffdfb0) at naughty.c:19
    #2  0x00007ffff7bbd3a9 in start_thread () from /lib64/libpthread.so.0
    #3  0x00007ffff78e936f in clone () from /lib64/libc.so.6

    Thread 2 (LWP 14485))
    #0  0x00007ffff78d835b in write () from /lib64/libc.so.6
    #1  0x00007ffff78524fd in _IO_new_file_write () from /lib64/libc.so.6
    #2  0x00007ffff7854271 in __GI__IO_do_write () from /lib64/libc.so.6
    #3  0x00007ffff7854723 in __GI__IO_file_overflow () from /lib64/libc.so.6
    #4  0x00007ffff7847fa2 in puts () from /lib64/libc.so.6
    #5  0x00000000004007e9 in naughty_thread (arg=0x0) at naughty.c:27
    #6  0x00007ffff7bbd3a9 in start_thread () from /lib64/libpthread.so.0
    #7  0x00007ffff78e936f in clone () from /lib64/libc.so.6

    Thread 1 (LWP 14485))
    #0  0x00007ffff7bbe90d in pthread_join () from /lib64/libpthread.so.0
    #1  0x00000000004008d1 in main (argc=1, argv=0x7fffffffe508) at naughty.c:51

With our stackfold command we can easily see that threads 129 through 3
have the same stack, and are idle. We can see that tread 1 is the main
process waiting on the threads to join, and finally we can see that
thread 2 is the culprit writing to our display.

## My solution

You can find my solution to this problem as a [reference implementation
here](../../../_static/gdb_py/debug_naughty.py) .

