I no longer recommend FreeIPA
=============================

It's probably taken me a few years to write this, but I can no longer recommend FreeIPA for
IDM installations.

Why not?
--------

The FreeIPA project focused on Kerberos and SSSD, with enough other parts glued on to look like
a complete IDM project. Now that's fine, but it means that concerns in other parts of the project
are largely ignored. It creates design decisions that are not scalable or robust.

Due to these decisions IPA has stability issues and scaling issues that other products do not.

To be clear: security systems like IDM or LDAP can *never* go down. That's not acceptable.

What do you recommend instead?
------------------------------

* `Kanidm <https://kanidm.github.io/kanidm/stable/>`_
* Samba with AD
* AzureAD
* 389 Directory Server

All of these projects are very reliable, secure, scalable.

Kanidm specifically is my own project built from the ground up, which has tried to learn from the
mistakes and successes of AD, FreeIPA and 389-ds. It's what I recommend the most.

Additionally, we have done a lot of work into 389
to improve our out of box IDM capabilities too, but there is more to be done too. The
Samba AD team have done great things too, and deserve a lot of respect for what they have done.

Is there more detail than this?
-------------------------------

Yes - buy me a drink and I'll talk :)

Didn't you help?
----------------

I tried and it was not taken on board. Issues I reported years ago still exist today 🙃.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
