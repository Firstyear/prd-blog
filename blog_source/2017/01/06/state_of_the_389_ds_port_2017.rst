State of the 389 ds port, 2017
==============================

Previously I have written about my efforts to port 389 ds to FreeBSD.

A great deal of progress has been made in the last few weeks (owing to my taking time off work).

I have now ported nunc-stans to freebsd, which is important as it's our new connection management system. It has an issue with long lived events, but I will resolve this soon.

The majority of patches for 389 ds have merged, with a single patch remaining to be reviewed.

Finally, I have build a freebsd makefile for the `devel root <https://github.com/Firstyear/ds-devel-root/blob/master/Makefile.fbsd>`_ to make it easier for people to install and test from source.

Once the freebsd nunc-stans and final DS patch are accepted, I'll be able to start building the portfiles.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
