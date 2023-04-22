+++
title = "Load balanced 389 instance with freeipa kerberos domain."
date = 2015-12-11
slug = "2015-12-11-Load_balanced_389_instance_with_freeipa_kerberos_domain."
# This is relative to the root!
aliases = [ "2015/12/11/Load_balanced_389_instance_with_freeipa_kerberos_domain..html" ]
+++
# Load balanced 389 instance with freeipa kerberos domain.

[I no longer recommend using FreeIPA - Read more
here!](/blog/html/2019/07/10/i_no_longer_recommend_freeipa.html)

First, create a fake host that we can assign services too. This is for
the load balancer (f5, netscaler, ace, haproxy)

    ipa host-add haproxydemo.ipa.example.com --random --force

Now you can add the keytab for the loadbalanced service.

    ipa service-add --force ldap/haproxydemo.ipa.example.com

Then you need to delegate the keytab to the ldap servers that will sit
behind the lb.

    ipa service-add-host ldap/haproxydemo.ipa.example.com --hosts=liza.ipa.example.com

You should be able to extract this keytab on the host now.

    ipa-getkeytab -s alina.ipa.example.com -p ldap/haproxydemo.ipa.example.com -k /etc/dirsrv/slapd-localhost/ldap.keytab 

into /etc/sysconfig/dirsrv-localhost

    KRB5_KTNAME=/etc/dirsrv/slapd-localhost/ldap.keytab 

Now, restart the instance and make sure you can\'t connect directly.

Setup haproxy. I had a huge amount of grief with ipv6, so I went v4 only
for this demo. :

    global
        log         127.0.0.1 local2

        chroot      /var/lib/haproxy
        pidfile     /var/run/haproxy.pid
        maxconn     4000
        user        haproxy
        group       haproxy
        daemon

        stats socket /var/lib/haproxy/stats

    listen ldap :3389
            mode tcp
            balance roundrobin

            server ldap 10.0.0.2:389 check
            timeout connect        10s
            timeout server          1m

    ldapsearch -H ldap://haproxydemo.ipa.example.com:3389 -Y GSSAPI

Reveals a working connection!
