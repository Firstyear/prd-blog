Building containers on OBS
==========================

My friend showed me how to build containers in OBS, the opensuse build service. It makes it
really quite nice, as the service can parse your dockerfile, and automatically trigger
rebuilds when any package dependency in the chain requires a rebuild.

The simplest way is to have a seperate project for your containers to make the repository
setup a little easier.

When you edit the project metadata, if the project doesn't already exist, a new one is
created. So we can start by filling out the template from the command:

::

    osc meta prj -e home:firstyear:containers


This will give you a template: We need to add some repository lines:

::

    <project name="home:firstyear:apps">
      <title>Containers Demo</title>
      <description>Containers Demo</description>
      <person userid="firstyear" role="bugowner"/>
      <person userid="firstyear" role="maintainer"/>
      <build>
        <enable/>
      </build>
      <publish>
        <enable/>
      </publish>
      <debuginfo>
        <enable/>
      </debuginfo>
      <!-- this repository -->
      <repository name="containers">
        <path project="openSUSE:Templates:Images:Tumbleweed" repository="containers"/>
        <arch>x86_64</arch>
      </repository>
    </project>

Remember, to set the publist to "enable" if you want the docker images you build to be pushed
to the registry!

Now that that's done, we can check out the project, and create a new container package within.

::

    osc co home:firstyear:containers
    cd home:firstyear:containers
    osc mkpac mycontainer

Now in the mycontainer folder you can start to build a container. Add your dockerfile:

::

    #!BuildTag: mycontainer
    #
    # docker pull registry.opensuse.org/home/firstyear/apps/containers/mycontainer:latest
    #                                   ^projectname        ^repos     ^ build tag
    FROM opensuse/tumbleweed:latest

    #
    # only one zypper ar command per line. only repositories inside the OBS are allowed
    #
    RUN zypper ar http://download.opensuse.org/repositories/home:firstyear:apps/openSUSE_Tumbleweed/ "home:firstyear:apps"
    RUN zypper mr -p 97 "home:firstyear:apps"
    RUN zypper --gpg-auto-import-keys ref
    RUN zypper install -y vim-data vim python3-ipython shadow python3-praw
    # Then the rest of your container as per usual ...


Then to finish up, you can commit this:

::

    osc add Dockerfile
    osc ci
    osc results







.. author:: default
.. categories:: none
.. tags:: none
.. comments::
