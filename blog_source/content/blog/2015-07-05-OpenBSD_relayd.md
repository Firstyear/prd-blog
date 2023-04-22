+++
title = "OpenBSD relayd"
date = 2015-07-05
slug = "2015-07-05-OpenBSD_relayd"
# This is relative to the root!
aliases = [ "2015/07/05/OpenBSD_relayd.html", "blog/html/2015/07/05/OpenBSD_relayd.html" ]
+++
# OpenBSD relayd

I\'ve been using OpenBSD 5.7 as my network router for a while, and I\'m
always impressed by the tools avaliable.

Instead of using direct ipv6 forwarding, or NAT port forwards for
services, I\'ve found it a lot easier to use the OpenBSD relayd software
to listen on my ingress port, then to relay the traffic in.
Additionally, this allows relayd to listen on ipv4 and ipv6 and to
rewrite connections to the backend to be purely ipv6.

This helps to keep my pf.conf small and clean, and just focussed on
security and inter-vlan / vrf traffic.

The only changes to pf.conf needed are:

    anchor "relayd/*" rtable 0

The relayd.conf man page is fantastic and detailed. Read through it for
help, but my basic config is:

:

    ext_addr="ipv4"
    ext_addr6="ipv6"


    smtp_port="25"
    smtp_addr="2001:db8:0::2"

    table <smtp> { $smtp_addr }

    protocol "tcp_service" {
       tcp { nodelay, socket buffer 65536 }
    }

    relay "smtp_ext_forwarder" {
       listen on $ext_addr port $smtp_port
       listen on $ext_addr6 port $smtp_port
       protocol "tcp_service"
       forward to <smtp> port $smtp_port check tcp
    }

That\'s it! Additionally, a great benefit is that when the SMTP server
goes away, the check tcp will notice the server is down and drop the
service. This means that you won\'t have external network traffic able
to poke your boxes when services are down or have been re-iped and
someone forgets to disable the load balancer configs.

This also gives me lots of visibility into the service and connected
hosts:

    relayctl show sum
    Id      Type            Name                            Avlblty Status
    1       relay           smtp_ext_forwarder                      active
    1       table           smtp:25                                 active (1 hosts)
    1       host            2001:db8:0::2                           99.97%  up

    relayctl show sessions
    session 0:53840 X.X.X.X:3769 -> 2001:db8:0::2:25     RUNNING
            age 00:00:01, idle 00:00:01, relay 1, pid 19574

So relayd has simplified my router configuration for external services
and allows me to see and migrate services internally without fuss of my
external configuration.
