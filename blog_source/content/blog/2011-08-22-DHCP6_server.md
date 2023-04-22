+++
title = "DHCP6 server"
date = 2011-08-22
slug = "2011-08-22-DHCP6_server"
# This is relative to the root!
aliases = [ "2011/08/22/DHCP6_server.html" ]
+++
# DHCP6 server

I have been battling with setting up one of these for a long time. It so
happens most areas of the internet, forget to mention one vital piece of
the DHCP6 puzzle - DHCP6 is not standalone. It is an addition to RADVD.
Thus you need to run both for it to work correctly.

Why would you want DHCP6 instead of RADVD? Well, RADVD may be good for
your simple home use with a few computers, and MDNS name resoultion. But
when you look at a business, a LAN party, or those who want DDNS
updates, it is essential.

First, we need to setup RADVD properly. The order of these directives is
*very* important.

    interface eth0
    {
        AdvManagedFlag on;
        AdvOtherConfigFlag on;
        AdvSendAdvert on;
        MinRtrAdvInterval 5;
        MaxRtrAdvInterval 60;
        prefix 2001:db8:1234:4321/64
        {
            AdvOnLink on;
            AdvAutonomous on;
            AdvRouterAddr on;
        };
    };

Next, we need to configure DHCP6. I am using the ISC-DHCP4 server. DHCP6
needs its own instance. Fedora provides a seperate script for this
(dhcpd6.service) that you can use. On other OSes\' you may not have this
and will need to start DHCPD manually with the -6 flag. Here is the
config you need.

    server-name "server.example.com" ;
    server-identifier server.example.com ;

    authoritative;
    option dhcp6.name-servers 2001:db8:1234:4321::1 ;
    ddns-update-style interim ;
    ddns-domainname "example.com";

    subnet6 2001:db8:1234:4321::/64 {
            range6 2001:db8:1234:4321::10 2001:db8:1234:4321::110 ;
    }

Now, since DHCP6 uses UDP / TCP (Its layer 3, and runs across link
local), you must consider your firewall. On both client and server you
need to accept icmp6, port 546 and 547 from the following addresses

    Server:
    Source - fe80::/16 
    Destination - ff02::1:2

    Client
    Source - ff02::1:2
    Source - fe80::/16 
    Destination - fe80::/16

A set of example iptables rules on the server side would be

    -A INPUT -p ipv6-icmp -j ACCEPT
    -A INPUT -s fe80::/16 -d ff02::1:2 -i eth0 -p udp -m udp --dport 546 -j ACCEPT
    -A INPUT -s fe80::/16 -d ff02::1:2 -i eth0 -p tcp -m tcp --dport 546 -j ACCEPT
    -A INPUT -s fe80::/16 -d ff02::1:2 -i eth0 -p udp -m udp --dport 547 -j ACCEPT
    -A INPUT -s fe80::/16 -d ff02::1:2 -i eth0 -p tcp -m tcp --dport 547 -j ACCEPT

And similar enough for the client.

Now start radvd, dhcp6 and your firewalls. Then on your client run.
Enjoy your DHCP6! :

    dhclient -d -v -6 interface

From here, it is very similar to DHCP4 to add things like DDNS updates
to your DHCP6 server.
