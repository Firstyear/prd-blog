SUSE Open Build Service cheat sheet
===================================

Part of starting at SUSE has meant that I get to learn about Open Build Service. I've known that
the project existed for a long time but I have never had a chance to use it. So far I'm thoroughly
impressed by how it works and the features it offers.

As A Consumer
-------------

The best part of OBS is that it's trivial on OpenSUSE to consume content from it. Zypper can add
projects with the command:

::

    zypper ar obs://<project name> <repo nickname>
    zypper ar obs://network:ldap network:ldap

I like to give the repo nickname (your choice) to be the same as the project name so I know what
I have enabled. Once you run this you can easily consume content from OBS.

Package Management
------------------

As someone who has started to contribute to the suse 389-ds package, I've been slowly learning
how this work flow works. OBS similar to GitHub/Lab allows a branching and request model.

On OpenSUSE you will want to use the osc tool for your workflow:

::

    zypper in osc

You can branch from an existing project to make changes with:

::

    osc branch <project> <package>
    osc branch network:ldap 389-ds

This will branch the project to my home namespace. For me this will land in
"home:firstyear:branches:network:ldap". Now I can checkout the content on to my machine to work on
it.

::

    osc co <project>
    osc co home:firstyear:branches:network:ldap

This will create the folder "home:...:ldap" in the current working directory.

From here you can now work on the project. Some useful commands are:

Add new files to the project (patches, new source tarballs etc).

::

    osc add <path to file>
    osc add feature.patch
    osc add new-source.tar.xz

Edit the change log of the project (I think this is used in release notes?)

::

    osc vc

Build your changes locally matching the system you are on. Packages normally build on all/most
OpenSUSE versions and architectures, this will build just for your local system and arch.

::

    osc build

Commit your changes to the OBS server, where a complete build will be triggered:

::

    osc commit

View the results of the last commit:

::

    osc results

Enable people to use your branch/project as a repository. You edit the project metadata and enable
repo publishing:

::

    osc meta prj -e <name of project>
    osc meta prj -e home:firstyear:branches:network:ldap

    # When your editor opens, change this section to enabled (disabled by default):
    <publish>
      <enabled />
    </publish>

NOTE: In some cases if you have the package already installed, and you add the repo/update it won't
install from your repo. This is because in SUSE packages have a notion of "vendoring". They continue
to update from the same repo as they were originally installed from. So if you want to change this you
use:

::

    zypper [d]up --from <repo name>

You can then create a "request" to merge your branch changes back to the project origin. This is:

::

    osc sr

So far this is as far as I have gotten with OBS, but I already appreciate how great this work flow
is for package maintainers, reviewers and consumers. It's a pleasure to work with software this well
built.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
