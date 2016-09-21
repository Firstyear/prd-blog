The mysterious crashing of my laptop
====================================

Recently I have grown unhappy with Fedora. The updates to the i915 graphics
driver have caused my laptop to kernel panic just connecting and removing
external displays: unacceptable to someone who moves their laptop around as much
as I do.

In the spirit of being a corporate schill, I have now installed and run Red Hat
Workstation on my laptop.

I noticed that randomly my laptop would just "freeze" and stop responding. It
was impossible to debug, and nothing was ever written to dmesg to help explain it.
Not even a reinstall would solve the issue. I was getting very frustrated with
the sad state of linux.

However a solution came from an un-expected place. While talking to a mate, I
mentioned the `blog of Dan Luu <http://danluu.com/>`_. He writes some amazing
articles, I highly recommend reading it. Specifically, I was discussing cpu
instruction bugs, and refered to `Dan's post <http://danluu.com/cpu-bugs/>`_ about 
this topic.

Reading through I noticed at the bottom of the page "And then there’s this
`Broadwell bug that hangs Linux if you don’t disable low-power states. <https://bugzilla.kernel.org/show_bug.cgi?id=103351>`_ ".
Following it, and reading I realised this sounded very familiar. Looking up my
CPU model, I realised it was one of the affected Broadwell's.

It looked like the fix went out in an Intel microcode update in early 2016. Checking
the version of microcode_ctl in RHEL7 stable, I noticed that the
latest microcode update was from July of 2015! I wasn't seeing this lock up in
Fedora because it had the microcode update, but in RHEL7, it was on an older
version, so I was now exposed to the bug. Remember that microcode doesn't
persist between power cycles, so the package version in your distro does matter
for this.

Going into the internal build system at Red Hat, I grabbed the pre-release version
of the microcode_ctl package which was built in July of 2016: Magic, the hangs
have stopped.

So by complete accident, talking to a friend about cpu bugs, helped me solve my
own laptop crash.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
