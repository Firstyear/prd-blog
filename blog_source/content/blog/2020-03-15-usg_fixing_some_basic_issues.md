+++
title = "USG fixing avahi"
date = 2020-03-15
slug = "2020-03-15-usg_fixing_some_basic_issues"
# This is relative to the root!
aliases = [ "2020/03/15/usg_fixing_some_basic_issues.html", "blog/html/2020/03/15/usg_fixing_some_basic_issues.html" ]
+++
# USG fixing avahi

Sadly on the USG pro 4 avahi will regularly spiral out of control taking
up 100% cpu. To fix this, we set an hourly restart:

    sudo -s
    crontab -e

Then add:

    15 * * * * /usr/sbin/service avahi-daemon restart

