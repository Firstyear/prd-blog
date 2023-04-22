+++
title = "Upgrading OpenSUSE 15.0 to 15.1"
date = 2019-09-25
slug = "2019-09-25-upgrading_opensuse_15_0_to_15_1"
# This is relative to the root!
aliases = [ "2019/09/25/upgrading_opensuse_15_0_to_15_1.html" ]
+++
# Upgrading OpenSUSE 15.0 to 15.1

It\'s a little bit un-obvious how to do this. You have to edit the repo
files to change the release version, then refresh + update.

    sed -ri 's/15\.0/15.1/' /etc/zypp/repos.d/*.repo
    zypper ref
    zypper dup
    reboot

Note this works on a transactional host too:

    sed -ri 's/15\.0/15.1/' /etc/zypp/repos.d/*.repo
    transactional-update dup
    reboot

It would be nice if these was an upgrade tool that would attempt the
upgrade and revert the repo files, or use temporary repo files for the
upgrade though. It would be a bit nicer as a user experience than sed of
the repo files.

