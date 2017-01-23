LCA2017 - Getting Into the Rusty Bucket
=======================================

I spoke at `Linux Conf Australia 2017 <http://lca2017.org>`_ recently. I presenteda techniques and lessons
about integrating Rust with existing C code bases. This is related to my work on Directory Server.

The recording of the talk can be found on `youtube <https://www.youtube.com/watch?v=AWnza5JX7jQ>`_ and on
the `Linux Australia Mirror <http://mirror.linux.org.au/pub/linux.conf.au/2017/>`_ .

You can find the git repository for the project `on github <https://github.com/Firstyear/ds_rust>`_ .

The slides can be viewed on `slides.com <http://redhat.slides.com/wibrown/rusty-bucket?token=oPNS4Ilp>`_ .

I have already had a lot of feedback on improvements to make to this system including the use of struct
pointers instead of c_void, and the use of bindgen in certain places.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
