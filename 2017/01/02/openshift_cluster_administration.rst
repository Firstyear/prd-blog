Openshift cluster administration
================================

Over the last 6 months I have administered a three node openshift v3 cluster in my lab environment.

The summary of this expirence is that openshift is a great idea, but not ready for production. As an administrator you will find this a frustrating, difficult experience.

.. more::

The good
========

Openshift makes running a cluster very easy in many ways. Docker "just works", services fail over smoothly. It's very reliable even as you are rebooting and updating hosts. For the most part it took care of itself. The cli and web ui are both very complete to use, and certainly it's a good direction for systems to be going.

The poor
========

Documentation
-------------

Documentation is fundamentally the weakest link, and underpins almost every single issue I have with openshift. The documentation *seems* complete, detailed and well written. Documentation being detailed and correct is the most important part of a project, it's your communication to your consumers. It's their first call when something goes wrong, and their impression of a project and it's processes rely on your documentation being correct.

However, the moment you start to use openshift, you realise there are huge swathing holes in the documentation. For example, using the NFS storage configuration guide it is *impossible* to walk away with a working storage configuration due to many missing elements. The installer does not document all the requirements you actually need to install a master or host.

It is clear that documentation has never been tested to develop or install a system, which shows a gap between the developers writing the software, and their consumption of their own documentation.

Installation
------------

The installation process is based on ansible playbooks. These playbooks seem to be untested as they are broken on almost every single git release I have used. This ranges from erroring on "missing repositories" - Without telling you what is missing (the irony being the playbook adds the repos needed for the install), to complaining you have not explicitly set out an openshift version number: hardcoding versions seems like a silly proposition in 2016/2017.

Looking away
------------

On two occasions yum upgrade trashed my cluster. One was a docker update that broke all SDN components. The other was an SELinux policy change that caused docker to not be able to launch. Again, this is underpinned by a lack of testing and what appears to be a lack of long term consumers of the software. The developer cycle is focused on a shortlived single node install, and the "developer" image is a standalone single host you are not expected to run long term.

Ipv6
----

The developers of openshift have not heard of ipv6. If you have ipv6 on your cluster machines it will not install (it breaks silently part way through). If you have ipv6 post install, your SDN breaks as services manually listen on ipv4 only. You must disable ipv6 for openshift to work. You must not have ANY AAAA records for your hosts. This was most disappointing.

It's not quite docker ...
-------------------------

Things that work in docker, don't quite work in openshift. For example, it "forces" your container to be remapped to a random uid, even if the image was built with a customer user etc. This breaks "pre-installed" applications as it does not remap from the build uid to the running one.

Additionally, volume's in docker *may* copy content as a template on first run. Openshift breaks this behaviour, so a number of containers just don't work.

This means, you can not just throw docker at openshift. You have a divide, where you have to build containers specific to openshift vs containers that work on "all platforms".

Summary
-------

Openshift is a good idea but it's currently not ready for production. I will reinvestigate in a year to see if the situation has changed.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
