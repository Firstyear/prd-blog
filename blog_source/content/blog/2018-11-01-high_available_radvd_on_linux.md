+++
title = "High Available RADVD on Linux"
date = 2018-11-01
slug = "2018-11-01-high_available_radvd_on_linux"
# This is relative to the root!
aliases = [ "2018/11/01/high_available_radvd_on_linux.html", "blog/html/2018/11/01/high_available_radvd_on_linux.html" ]
+++
# High Available RADVD on Linux

Recently I was experimenting again with high availability router
configurations so that in the cause of an outage or a failover the other
router will take over and traffic is still served.

This is usually done through protocols like VRRP to allow virtual ips to
exist that can be failed between. However with ipv6 one needs to still
allow clients to find the router, and in the cause of a failure, the
router advertisments still must continue for client renewals.

To achieve this we need two parts. A shared Link Local address, and a
special RADVD configuration.

Because of howe ipv6 routers work, all traffic (even global) is still
sent to your link local router. We can use an address like:

    fe80::1:1

This doesn\'t clash with any reserved or special ipv6 addresses, and
it\'s easy to remember. Because of how link local works, we can put this
on many interfaces of the router (many vlans) with no conflict.

So now to the two components.

## Keepalived

Keepalived is a VRRP implementation for linux. It has extensive
documentation and sometimes uses some implementation specific language,
but it works well for what it does.

Our configuration looks like:

    #  /etc/keepalived/keepalived.conf
    global_defs {
      vrrp_version 3
    }

    vrrp_sync_group G1 {
     group {
       ipv6_ens256
     }
    }

    vrrp_instance ipv6_ens256 {
       interface ens256
       virtual_router_id 62
       priority 50
       advert_int 1.0
       virtual_ipaddress {
        fe80::1:1
        2001:db8::1
       }
       nopreempt
       garp_master_delay 1
    }

Note that we provide both a global address and an LL address for the
failover. This is important for services and DNS for the router to have
the global, but you could omit this. The LL address however is critical
to this configuration and must be present.

Now you can start up vrrp, and you should see one of your two linux
machines pick up the address.

## RADVD

For RADVD to work, a feature of the 2.x series is required. Packaging
this for el7 is out of scope of this post, but fedora ships the version
required.

The feature is that RADVD can be configured to specify which address it
advertises for the router, rather than assuming the interface LL
autoconf address is the address to advertise. The configuration appears
as:

    # /etc/radvd.conf
    interface ens256
    {
        AdvSendAdvert on;
        MinRtrAdvInterval 30;
        MaxRtrAdvInterval 100;
        AdvRASrcAddress {
            fe80::1:1;
        };
        prefix 2001:db8::/64
        {
            AdvOnLink on;
            AdvAutonomous on;
            AdvRouterAddr off;
        };
    };

Note the AdvRASrcAddress parameter? This defines a priority list of
address to advertise that could be available on the interface.

Now start up radvd on your two routers, and try failing over between
them while you ping from your client. Remember to ping LL from a client
you need something like:

    ping6 fe80::1:1%en1

Where the outgoing interface of your client traffic is denoted after the
\'%\'.

Happy failover routing!

