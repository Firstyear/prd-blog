What's new in 389 Directory Server 1.3.5 (unofficial)
=================================================

As a member of the 389 Directory Server (389DS) core team, I am always excited about our new
releases. We have some really great features in 1.3.5. However, our changelogs
are always large so I want to just touch on a few of my favourites.

389 Directory Server is an LDAPv3 compliant server, used around the world for
Identity Management, Authentication, Authorisation and much more. It is the
foundation of the FreeIPA projects server. As a result, it's not something we
often think about or even get excited for: but every day many of us rely on
389 Directory Server to be correct, secure and fast behind the scenes.

Tuning database cache size
--------------------------

Database cache tuning is something that is frequently discussed around 389DS to
gain the best performance from your server. We have overhauled the
database automatic tuning code to detect memory available on the system more
accurately, we split it better between backends, and make better decisions if the
ram requested is *too* much.

For those who manually tune their backend memory usage, we now have better
detection of if your tuning is going to cause stability issues. We issue better
warnings, and tell you exactly which parameters you need to alter to correct problems before they happen. By
putting the config values you need to alter in the error message, it saves
time and confusion by directing you, the administrator, to exactly what you need to do
to improve your server health and stability.

We have also eliminated an entire class of issues with database import and
re-indexing by automatically tuning the buffer sizes during the process: No more
tweaking database cache sizes to import those large databases!

Auditing for attempted changes
------------------------------

We have added new features called the auditfail log. Previously, if a change was
made, we would log who made the change, and what they changed to the audit log.
But if someone attempted a change, and it failed, we would not log it.

In 1.3.5 this has changed. You can enable the auditfail log with in cn=config

::

    nsslapd-auditfaillog-enabled: on

When a change is attempted, and fails, the reason why (I.E. incorrect object class,
lack of permission) and the data that they attempted to change is logged. This
is great for debugging applications, but also a great win for security as we can
see if someone is attempting to change data they do not have access to.

Hardening and stability
-----------------------

We have been applying static and dynamic analysis tools to 389DS
during this development cycle. Combined with our extensive test suites, we have
closed many stability bugs (overflows, use after free, double free, segfaults
and more) proactively during our development. This has made 1.3.5 in my view,
what will be the most reliable, secure version of 389DS we have ever
released.

Conclusion
----------

There are many more changes than this in the release: to learn more, see our
`release notes <http://www.port389.org/docs/389ds/releases/release-1-3-5-13.html>`_ .
Our team's goal has been to eliminate administrative
issues (not document, eliminate - never to be seen again!), improve performance and stability, and to provide better, correct defaults
in the server. So many of these changes are "out of sight" to users and even
administrators; but they are invaluable for improving services like FreeIPA 
that build upon 389 Directory Server.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
