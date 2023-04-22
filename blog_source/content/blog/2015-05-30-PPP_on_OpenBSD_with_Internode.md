+++
title = "PPP on OpenBSD with Internode"
date = 2015-05-30
slug = "2015-05-30-PPP_on_OpenBSD_with_Internode"
# This is relative to the root!
aliases = [ "2015/05/30/PPP_on_OpenBSD_with_Internode.html", "blog/html/2015/05/30/PPP_on_OpenBSD_with_Internode.html" ]
+++
# PPP on OpenBSD with Internode

It\'s taken me some time to get this to work nicely.

First, you\'ll need to install OpenBSD 56 or 57.

Once done, you need to configure your ethernet interface facing your
router that you would have setup in pppoe bridge mode.

/etc/hostname.vio0 :

    rdomain 0
    inet 172.24.17.1 255.255.255.0 NONE
    inet6 2001:db8:17::1 64
    up

NOTE: You can ignore the rdomain statement, but I\'ll cover these is a
later blog post.

Now you need to configure the pppoe interface.

/etc/hostname.pppoe0 :

    !/bin/sleep 10
    rdomain 0
    inet 0.0.0.0 255.255.255.255 NONE pppoedev vio0 authproto chap authname 'USERNAME@internode.on.net' authkey 'PASSWORD'
    dest 0.0.0.1
    inet6 eui64
    up
    !/sbin/route -T 0 add default -ifp pppoe0 0.0.0.1
    !if [ -f /tmp/dhcp6c ] ; then kill -9 `cat /tmp/dhcp6c`; fi
    !/bin/sleep 5
    !/usr/local/sbin/dhcp6c -c /etc/dhcp6c.conf -p /tmp/dhcp6c pppoe0
    !/sbin/route -T 0 add -inet6 default -ifp pppoe0 fe80::

That\'s quite the interface config!

You need the first sleep to make sure that vio0 is up before this
interface starts. Horrible, but it works.

Then you define the interface in the same rdomain, and inet6 eui64 is
needed so that you can actually get a dhcp6 lease. Then you bring up the
interface. Dest is needed to say that the remote router is the device
connected at the other end of the tunnel. We manually add the default
route for ipv4, and we start the dhcp6c client (After killing any
existing ones). Finally, we add the ipv6 default route down the
interface

Now, the contents of dhcp6c.conf are below:

    # tun0/pppoe0 is the PPPoE interface
    interface pppoe0 {
      send ia-pd 0;
    };

    # em1 is the modem interface
    interface vio0 {
      information-only;
    };

    id-assoc pd {
    # em0 is the interface to the internal network
      prefix-interface vio0 {
        sla-id 23;
        sla-len 8;
      };
    };

These are already configured to make the correct request to internode
for a /56. If you only get a /64 you need to tweak sla-len.

Most of this is well documented, but the real gotchas are in the
hostname.pppoe0 script, especially around the addition of the default
route and the addition of dhcp6c.

If you are running PF, besides normal NAT setup etc, you\'ll need this
for IPv6 to work:

    interface_ext_r0="{pppoe0}"

    pass in quick on $interface_ext_r0 inet6 proto udp from fe80::/64 port 547 to fe80::/64 port 546 keep state rtable 0
