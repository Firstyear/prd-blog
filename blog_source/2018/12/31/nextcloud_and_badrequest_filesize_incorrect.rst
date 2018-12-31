Nextcloud and badrequest filesize incorrect
===========================================

My friend came to my house and was trying to share some large files with my nextcloud
instance. Part way through the upload an error occurred.

::

    "Exception":"Sabre\\DAV\\Exception\\BadRequest","Message":"expected filesize 1768906752 got 1768554496"

It turns out this error can be caused by many sources. It could be timeouts,
bad requests, network packet loss, incorrect nextcloud configuration or more.

We tried uploading larger files (by a factor of 10 times) and they worked. This
eliminated timeouts as a cause, and probably network loss. Being on ethernet direct to the
server generally also helps to eliminate packet loss as a cause compared to say internet.

We also knew that the server must not have been misconfigured because a larger
file did upload, so no file or resource limits were being hit.

This also indicated that the client was likely doing the right thing because
larger and smaller files would upload correctly. The symptom now only affected
a single file.

At this point I realised, what if the client and server were both victims to a
lower level issue? I asked my friend to ls the file and read me the number of
bytes long. It was 1768906752, as expected in nextcloud.

Then I asked him to cat that file into a new file, and to tell me the length of
the new file. Cat encountered an error, but ls on the new file indeed showed
a size of 1768554496. That means filesystem corruption! What could have lead to
this?

HFS+

Apple's legacy filesystem (and the reason I stopped using macs) is well known
for silently eating files and corrupting content. Here we had yet another case
of that damage occuring, and triggering errors elsewhere.

Bisecting these issues and eliminating possibilities through a scientific
method is always the best way to resolve the cause, and it may come from
surprising places!

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
