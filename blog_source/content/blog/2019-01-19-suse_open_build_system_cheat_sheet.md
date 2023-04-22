+++
title = "SUSE Open Build Service cheat sheet"
date = 2019-01-19
slug = "2019-01-19-suse_open_build_system_cheat_sheet"
# This is relative to the root!
aliases = [ "2019/01/19/suse_open_build_system_cheat_sheet.html" ]
+++
# SUSE Open Build Service cheat sheet

Part of starting at SUSE has meant that I get to learn about Open Build
Service. I\'ve known that the project existed for a long time but I have
never had a chance to use it. So far I\'m thoroughly impressed by how it
works and the features it offers.

## As A Consumer

The best part of OBS is that it\'s trivial on OpenSUSE to consume
content from it. Zypper can add projects with the command:

    zypper ar obs://<project name> <repo nickname>
    zypper ar obs://network:ldap network:ldap

I like to give the repo nickname (your choice) to be the same as the
project name so I know what I have enabled. Once you run this you can
easily consume content from OBS.

## Package Management

As someone who has started to contribute to the suse 389-ds package,
I\'ve been slowly learning how this work flow works. OBS similar to
GitHub/Lab allows a branching and request model.

On OpenSUSE you will want to use the osc tool for your workflow:

    zypper in osc
    # If you plan to use the "service" command
    zypper in obs-service-tar obs-service-obs_scm obs-service-recompress obs-service-set_version obs-service-download_files python-xml obs-service-format_spec_file

You can branch from an existing project to make changes with:

    osc branch <project> <package>
    osc branch network:ldap 389-ds

This will branch the project to my home namespace. For me this will land
in \"home:firstyear:branches:network:ldap\". Now I can checkout the
content on to my machine to work on it.

    osc co <project>
    osc co home:firstyear:branches:network:ldap

This will create the folder \"home:\...:ldap\" in the current working
directory.

From here you can now work on the project. Some useful commands are:

Add new files to the project (patches, new source tarballs etc).

    osc add <path to file>
    osc add feature.patch
    osc add new-source.tar.xz

Edit the change log of the project (I think this is used in release
notes?)

    osc vc

To ammend your changes, use:

    osc vc -e

Build your changes locally matching the system you are on. Packages
normally build on all/most OpenSUSE versions and architectures, this
will build just for your local system and arch.

    osc build

Make sure you clean up files you aren\'t using any more with:

    osc rm <filename>
    # This commands removes anything untracked by osc.
    osc clean

Commit your changes to the OBS server, where a complete build will be
triggered:

    osc commit

View the results of the last commit:

    osc results

Enable people to use your branch/project as a repository. You edit the
project metadata and enable repo publishing:

    osc meta prj -e <name of project>
    osc meta prj -e home:firstyear:branches:network:ldap

    # When your editor opens, change this section to enabled (disabled by default):
    <publish>
      <enabled />
    </publish>

NOTE: In some cases if you have the package already installed, and you
add the repo/update it won\'t install from your repo. This is because in
SUSE packages have a notion of \"vendoring\". They continue to update
from the same repo as they were originally installed from. So if you
want to change this you use:

    zypper [d]up --from <repo name>

You can then create a \"request\" to merge your branch changes back to
the project origin. This is:

    osc sr

A helpful maintainer will then review your changes. You can see this
with.

    osc rq show <your request id>

If you change your request, to submit again, use:

    osc sr

And it will ask if you want to replace (supercede) the previous request.

I was also helped by a friend to provie a \"service\" configuration that
allows generation of tar balls from git. It\'s not always appropriate to
use this, but if the repo has a \"\_service\" file, you can regenerate
the tar with:

    osc service ra

So far this is as far as I have gotten with OBS, but I already
appreciate how great this work flow is for package maintainers,
reviewers and consumers. It\'s a pleasure to work with software this
well built.

As an additional piece of information, it\'s a good idea to read the [OBS Packaging Guidelines](https://en.opensuse.org/openSUSE:Packaging_Patches_guidelines)

:   to be sure that you are doing the right thing!

\# Acts as tail

:   osc bl osc r -v

\# How to access the meta and docker stuff

> osc meta pkg -e osc meta prj -e

(will add vim to the buildroot), then you can chroot (allow editing in
the build root)

> osc chroot osc build -x vim

-k \<dir\> keeps artifacts in directory dir IE rpm outputs

oscrc buildroot variable, mount tmpfs to that location.

docker privs SYS_ADMIN, SYS_CHROOT

Multiple spec: commit second spec to pkg then:

> osc linkpac prj pkg prj new-link-pkg

rpm \--eval \'%{variable}\'

%setup -n \"name of what the directory unpacks to, not what to rename
to\"

When no link exists

> osc submitpac destprj deskpkg

