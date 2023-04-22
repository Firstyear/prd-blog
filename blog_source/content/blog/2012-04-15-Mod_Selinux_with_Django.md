+++
title = "Mod Selinux with Django"
date = 2012-04-15
slug = "2012-04-15-Mod_Selinux_with_Django"
# This is relative to the root!
aliases = [ "2012/04/15/Mod_Selinux_with_Django.html", "blog/html/2012/04/15/Mod_Selinux_with_Django.html" ]
+++
# Mod Selinux with Django

Django with mod_selinux

The mod_selinux module allows you to confine a spawned apache process
into a specific selinux context. For example, you can do this via
virtual hosts, or by LocationMatch directives.

Part of my curiosity wanted to see how this works. So I made up a small
django application that would tell you the selinux context of an URL.

Install mod_selinux first

    yum install mod_selinux mod_wsgi

Now we create a VirtualHost that we can use for the test application

:

    NameVirtualHost *:80

    <VirtualHost *:80>
        ServerAdmin william@firstyear.id.au
        DocumentRoot /var/empty
        ServerName 172.16.209.150

        <LocationMatch /selinux/test/c2>
        selinuxDomainVal    *:s0:c2
        </LocationMatch>
        <LocationMatch /selinux/test/c3>
        selinuxDomainVal    *:s0:c3
        </LocationMatch>

        #Alias /robots.txt /usr/local/wsgi/static/robots.txt
        #Alias /favicon.ico /usr/local/wsgi/static/favicon.ico

        AliasMatch ^/([^/]*\.css) /var/www/django_base/static/styles/$1

        Alias /media/ /var/www/django_base/media/
        Alias /static/ /var/www/django_base/static/

        <Directory /var/www/django_base/static>
        Order deny,allow
        Allow from all
        </Directory>

        <Directory /var/www/django_base/media>
        Order deny,allow
        Allow from all
        </Directory>

        WSGIScriptAlias / /var/www/django_base/django_base/wsgi.py

        <Directory /var/www/django_base/scripts>
        Order allow,deny
        Allow from all
        </Directory>
    </VirtualHost>

We also need to alter /etc/httpd/conf.d/mod_selinux.conf to have MCS
labels.

    selinuxServerDomain     *:s0:c0.c100

And finally, download the (now sadly lost) tar ball, and unpack it to
/var/www

    cd /var/www
    tar -xvzf django_selinux_test.tar.gz

Now, navigating to the right URL will show you the different SELinux
contexts

<http://localhost/selinux/test/test> :

    Hello. Your processes context is [0, 'system_u:system_r:httpd_t:s0:c0.c100']

<http://localhost/selinux/test/c2> :

    Hello. Your processes context is [0, 'system_u:system_r:httpd_t:s0:c2']

<http://localhost/selinux/test/c3> :

    Hello. Your processes context is [0, 'system_u:system_r:httpd_t:s0:c3']

The best part about this is that this context is passed via the local
unix socket to sepgsql - meaning that specific locations in your Django
application can have different SELinux MCS labels, allowing mandatory
access controls to tables and columns. Once I work out row-level
permissions in sepgsql, these will also be available to django processes
via this means.

Example of why you want this.

You have a shopping cart application. In your users profile page, you
allow access to that URL to view / write to the credit card details of a
user. In the main application, this column is in a different MCS - So
exploitation of the django application, be it SQL injection, or remote
shell execution - the credit cards remain in a separate domain, and thus
inaccessible.

Additionally, these MCS labels are applied to files uploaded into /media
for example, so you can use this to help restrict access to documents
etc.
