+++
title = "Virtual hosted django"
date = 2013-02-18
slug = "2013-02-18-Virtual_hosted_django"
# This is relative to the root!
aliases = [ "2013/02/18/Virtual_hosted_django.html" ]
+++
# Virtual hosted django

Recently I have been trying to host multiple django applications on a
single apache instance.

Sometimes, you would find that the page from a different vhost would
load incorrectly. This is due to the way that WSGI handles work thread
pools.

To fix it.

In your /etc/httpd/conf.d/wsgi.conf Make sure to comment out the
WSGIPythonPath line. :

    #WSGIPythonPath
    WSGISocketPrefix run/wsgi
    #You can add many process groups. 
    WSGIDaemonProcess group_wsgi python-path="/var/www/django/group"

Now in your VHost add the line (If your script alias is \"/\") :

    <location "/">
    WSGIProcessGroup group_wsgi
    </location>
