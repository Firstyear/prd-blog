Using the latest 389-ds on OpenSUSE
===================================

Thanks to some help from my friend who works on OBS, I've finally got a good package in review
for submission to tumbleweed. However, if you are impatient and want to use the "latest" and greatest
389-ds version on OpenSUSE (docker anyone?).

::

    docker run -i -t opensuse/tumbleweed:latest
    zypper ar obs://network:ldap network:ldap
    zypper in 389-ds

Now, we still have an issue with "starting" from dsctl (we don't really expect you to do it like
this ....) so you have to make a tweak to defaults.inf:

::

    vim /usr/share/dirsrv/inf/defaults.inf
    # change the following to match:
    with_systemd = 0

After this, you should now be able to follow our `new quickstart guide <http://www.port389.org/docs/389ds/howto/quickstart.html>`_ on the 389-ds website.

I'll try to keep this repo up to date as much as possible, which is great for testing and early
feedback to changes!

EDIT: Updated 2019-04-03 to change repo as changes have progressed forward.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
