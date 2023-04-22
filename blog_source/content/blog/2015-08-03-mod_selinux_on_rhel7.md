+++
title = "mod selinux on rhel7"
date = 2015-08-03
slug = "2015-08-03-mod_selinux_on_rhel7"
# This is relative to the root!
aliases = [ "2015/08/03/mod_selinux_on_rhel7.html", "blog/html/2015/08/03/mod_selinux_on_rhel7.html" ]
+++
# mod selinux on rhel7

I have now compiled and testing mod_selinux on el7. I\'m trying to get
this into EPEL now.

To test this once you have done a build.

    #!/usr/bin/env python
    import cgi
    import cgitb; cgitb.enable()  # for troubleshooting
    import selinux

    print "Content-type: text/html"
    print
    print """
    <html>
    <head><title>Selinux CGI context</title></head>
    <body>
      <p>Current context is %s</p>
    </body>
    </html>
    """ % cgi.escape(str(selinux.getcon()))

Put this cgi into:

    /var/www/cgi-bin/selinux-c1.cgi
    /var/www/cgi-bin/selinux-c2.cgi
    /var/www/cgi-bin/selinux-c3.cgi

Now, install and configure httpd.

/etc/httpd/conf.d/mod_selinux.conf

    <VirtualHost *:80>
     DocumentRoot          /var/www/html

        <LocationMatch /cgi-bin/selinux-c2.cgi>
        selinuxDomainVal    *:s0:c2
        </LocationMatch>
        <LocationMatch /cgi-bin/selinux-c3.cgi>
        selinuxDomainVal    *:s0:c3
        </LocationMatch>

    </VirtualHost>

Now when you load each page you should see different contexts such as:
\"Current context is \[0,
\'system_u:system_r:httpd_sys_script_t:s0:c3\'\]\"

You can easily extend these location-match based contexts onto django
project urls etc. Consider you have a file upload. You place that into
c1, and then have all other processes in c2. If the url needs to look at
the file, then you place that in c1 also.

Alternately, you can use this for virtualhost isolation, or even if you
feel game, write new policies to allow more complex rules within your
application.

34
