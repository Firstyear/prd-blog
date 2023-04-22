The next year of Directory Server
=================================

Last year I wrote a post about the vision behind Directory Server and what I wanted to achieve in the project
personally. My key aims were:

* We need to modernise our tooling, and installers.
* Setting up replication groups and masters needs to be simpler.
* We need to get away from long lived static masters.
* During updates, we need to start to enable smarter choices by default.
* Out of the box we need smarter settings.
* Web Based authentication

.. more::

What was not achieved
=====================

Sadly, I ran out of time. I ended up working on other goals and not tracking these.

* Setting up replication groups and masters needs to be simpler.
* We need to get away from long lived static masters.
* Web Based authentication

These three were missed this year, due to my focus and time.

What was achieved
=================

* We need to modernise our tooling, and installers.
* During updates, we need to start to enable smarter choices by default.
* Out of the box we need smarter settings.

I was able to make large inroads in these three areas. We now have better ways to upgrade our
security and configuration setting on upgrades. We have autotuning available to us now by default.

The new python installer is now able to install blank instances, and in the next few months will
pick up many more features and improvements.

Some unlisted surprise goals that we achieved

* Improvements to QE and testing.
* Address Sanitising the entire code base.
* Proof of Concept integration of Rust plugins.
* Safety improvements to nunc-stans
* Early addition of new thread safe datastructures.
* Port DS C to FreeBSD.

What are my goals this year?
============================

* Complete libsds to allow thread safe datastructures and object management.
* Continue to improve QE and testing through integration of doxygen and cmocka.
* Password hashing and 2FA plugins in Rust.
* Complete port to FreeBSD - Python components as of Jan 2017.
* Deprecate the perl installer.
* Integration of Web Authentication (saml, oauth)
* Continue to improve and replace all our CLI tools with python.



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
