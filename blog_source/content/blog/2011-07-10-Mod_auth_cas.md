+++
title = "Mod auth cas"
date = 2011-07-10
slug = "2011-07-10-Mod_auth_cas"
# This is relative to the root!
aliases = [ "2011/07/10/Mod_auth_cas.html", "blog/html/2011/07/10/Mod_auth_cas.html" ]
+++
# Mod auth cas

Recently at UofA, It was mentioned in passing \"Wouldn\'t it be nice to
have [CAS](http://www.jasig.org/cas) auth on the webserver instead of
ldap basic auth?\".

\"Yes, It would be \", I said. But it got me thinking about the issues
involved. While nice to use CAS, CAS only provides authentication, not
authorization. We rely on ldap attributes for determining access to
content.

After a few minutes of reading, I found the solution.

## Installation

I tested this on CentOS 5 (As we use RHEL at work), so adjust this for
your needs.

If EPEL is not enabled you can enable it with this

[EPEL](http://fedoraproject.org/wiki/EPEL).

If you wish to only install the one package, you can set the repository
to disabled, and install with the following command

    yum install --enablerepo=epel mod_auth_cas 

Also install the ldap module. It is part of the base repo in RHEL.

    yum install mod_authz_ldap

## Configuration

Stop your apache server

We need the modules to load in a certain order, so we need to rename our
configs.

    cd /etc/httpd/conf.d/
    mv auth_cas.conf 00_auth_cas.conf
    mv authz_ldap.conf 10_authz_ldap.conf
    mv ssl.conf 20_ssl.conf

In /etc/httpd/conf.d/00_auth_cas.conf

    #
    # mod_auth_cas is an Apache 2.0/2.2 compliant module that supports the
    # CASv1 and CASv2 protocols
    #

    LoadModule auth_cas_module modules/mod_auth_cas.so
    <IfModule mod_auth_cas.c>
        CASVersion 2
        CASDebug On

        # Validate the authenticity of the login.goshen.edu SSL certificate by
        # checking its chain of authority from the root CA.
        CASCertificatePath /etc/pki/tls/certs/
        CASValidateServer Off
        CASValidateDepth 9

        CASCookiePath /var/lib/cas/

        CASLoginURL https://auth.example.com/cas/login
        CASValidateURL https://auth.example.com/cas/serviceValidate
        CASTimeout 7200
        CASIdleTimeout 7200
      </IfModule>

DO NOT RESTART APACHE YET.

You need to create the cas tickets directory, else the module will barf.

    cd /var/lib
    sudo mkdir cas
    sudo chown apache:apache cas
    sudo chmod 750 cas
    sudo semanage fcontext -a -s system_u -t httpd_var_lib_t /var/lib/cas
    sudo restorecon -r -v ./

This applies the needed SELinux policy to allow httpd to write to that
directory. If you have set SELinux to permissive or disabled, these
steps are worth taking incase you enable SELinux again in the future.

\<strong\>Configuration with LDAP authorization\</strong\>

Now we can add our ldap attributes we need. Check that
10_authz_ldap.conf matches the following

    #
    # mod_authz_ldap can be used to implement access control and 
    # authenticate users against an LDAP database.
    # 

    LoadModule authz_ldap_module modules/mod_authz_ldap.so

    <IfModule mod_authz_ldap.c>

    ## Some commented code

    </IfModule>

Now, in your SSL Directory directive add

    <Directory "/var/www/ms1">
        Order allow,deny
        Allow from all
        AuthType CAS
        AuthName "TEST CAS AUTH"
        AuthLDAPURL ldaps://ldap.example.com:636/ou=People,dc=example,dc=com?uid?one?
        require ldap-filter &(uid=username)
      </Directory>

You can start apache again after reading the filter section

## Filter

This ldap filter can be anything you desire. It can be a list of UID\'s,
sets of attributes, etc.

examples:

    #Will check for this attribute
    &(department=marketing)
    #Checks that one has both this class and this department
    &(class=compsci1001)(department=marketing)
    #Your name is either foo or bar
    |(uid=foo)(uid=bar)
    #These can be nested as well. This would allow anyone with attr and other attr OR the uid= foo into the site. 
    |(&((attr=true)(other attr=true)) (uid=foo))

You can read more about filters
[here](http://www.zytrax.com/books/ldap/apa/search.html).

Alternately, one can change the configuration to be like so

    AuthLDAPURL ldaps://ldap.example.com:636/ou=People,dc=example,dc=com?uid?one?(&(attr=foo)(attr=bar))
    Require valid-user

Note the filters are the same, but require the whole filter to be
enclosed in a set of ().
