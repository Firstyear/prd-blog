+++
title = "LCA2017 - Getting Into the Rusty Bucket"
date = 2017-01-23
slug = "2017-01-23-lca2017_getting_into_the_rusty_bucket"
# This is relative to the root!
aliases = [ "2017/01/23/lca2017_getting_into_the_rusty_bucket.html", "blog/html/2017/01/23/lca2017_getting_into_the_rusty_bucket.html" ]
+++
# LCA2017 - Getting Into the Rusty Bucket

I spoke at [Linux Conf Australia 2017](http://lca2017.org) recently. I
presented techniques and lessons about integrating Rust with existing C
code bases. This is related to my work on Directory Server.

The recording of the talk can be found on
[youtube](https://www.youtube.com/watch?v=AWnza5JX7jQ) and on the [Linux
Australia Mirror](http://mirror.linux.org.au/pub/linux.conf.au/2017/) .

You can find the git repository for the project [on
github](https://github.com/Firstyear/ds_rust) .

The slides can be viewed on
[slides.com](http://redhat.slides.com/wibrown/rusty-bucket?token=oPNS4Ilp)
.

I have already had a lot of feedback on improvements to make to this
system including the use of struct pointers instead of c_void, and the
use of bindgen in certain places.

