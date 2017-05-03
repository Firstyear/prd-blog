OpenBSD BGP and VRFs
====================
VRFs, or in OpenBSD rdomains, are a simple, yet powerful (and sometimes confusing) topic. 

Simply, when you have a normal router or operating system, you have a single router table. You have network devices attached into this routing table, traffic may be sent between those interfaces, or they may exit via a default route.

::
    
    10.0.1.1/24
    eth0 -->   |           |
    10.0.2.1/24| rdomain 0 | --> pppoe0 default route
    eth1 -->   |           |
    
    

So in this example, traffic from 10.0.1.1 can flow to 10.0.2.1 and vice versa. Traffic that matches neither of these will be sent down the pppoe0 default route.

Now, lets show what that looks like with two rdomains:

::
    
    10.0.1.1/24
    eth0 -->   |           |
    10.0.2.1/24| rdomain 0 | --> pppoe0 default route
    eth1 -->   |           |
               -------------
    10.0.3.1/24|           |
    eth2 -->   | rdomain 1 |
    10.0.4.1/24|           |
    

Now, in our example, traffic for interfaces on rdomain 0 will flow to each other as normal. At the same time, traffic between devices in rdomain 1 will flow correctly also. However, no traffic BETWEEN rdomain 0 and rdomain 1 is permitted.

This also means you could do:

::
    
    10.0.1.1/24
    eth0 -->   |           |
    10.0.2.1/24| rdomain 0 | --> pppoe0 default route
    eth1 -->   |           |
               -------------
    10.0.3.1/24|           |
    eth2 -->   | rdomain 1 | --> pppoe1 different default route
    10.0.4.1/24|           |
    eth3 -->   |           |
    

So some networks have one default route, while other networks have a different default route. Guest networks come to mind ;)

Or you can do:

::
    
    10.0.1.1/24
    eth0 -->   |           |
    10.0.2.1/24| rdomain 0 | 
    eth1 -->   |           |
               -------------
    10.0.1.1/24|           |
    eth2 -->   | rdomain 1 |
    10.0.2.1/24|           |
    eth3 -->   |           |
    

Note that now our ipv4 ip ranges over lap: However, because the traffic entered an interface on a specific rdomain, the traffic will always stay in that rdomain. Traffic from eth1 to 10.0.1.1/24 will always go to eth0. Never eth2, as that would be crossing rdomains.

So rdomains are really powerful for network isolation, security, multiple routers or allowing overlapping ip ranges to be reused.


Now, we change to a different tact: BGP. BGP is the border gateway protocol. It allows two routers to distribute routes between them so they are aware of and able to route traffic correctly. For example.

::
    
    
    10.0.1.0/24|          |   IC   |          | 10.0.2.0/24
    eth0 -->   | router A | <----> | router B | <-- eth1
               |          |        |          |
    

Normally with no assistance router A and B could only see each other via the interconnect IC. 10.0.1.0/24 is a mystery to router B, as is 10.0.2.0/24 from router A. They just aren't connected so they can't route traffic. 

By enabling BGP from A to B over the interconnect, router A can discover the networks attached to router B and vice versa. With this information, both routers can correctly send traffic destined to the other via the IC as they now know the correct destinations and connections. 


There are plenty of documents on enabling both of these technologies in isolation: However, I had a hard time finding a document that showed how we do both at the same time. I wanted to build:

::
    
                 router A               router B
    10.0.1.1/24                                      10.0.3.1/24
    eth0 -->   |           |    IC1   |           |  <-- eth0
    10.0.2.1/24| rdomain 0 |  <---->  | rdomain 0 |  10.0.4.1/24
    eth1 -->   |           |          |           |  <-- eth1
               -------------          -------------
    10.0.1.1/24|           |    IC2   |           |  10.0.3.1/24
    eth2 -->   | rdomain 1 |  <---->  | rdomain 1 |  <-- eth2
    10.0.2.1/24|           |          |           |  10.0.4.1/24
    eth3 -->   |           |          |           |  <-- eth3
    

So I wanted the networks of rdomain 0 from router A to be exported to rdomain 0 of router B, and the networks of router A rdomain 1 to be exported into router B rdomain 1.

The way this is achieved is with BGP communities. The BGP router makes a single connection from router A to router B. The BGPd process on A, is aware of rdomains and is able to read the complete system rdomain state. Each rdomains route table is exported into a community. For example, you would have AS:0 and AS:1 in my example. On the recieving router, the contents of the community are imported to the assocated rdomain. For example, community AS:0 would be imported to rdomain 0.

Now, ignoring all the other configuration of interfaces with rdomains and pf, here is what a basic BGP configuration would look like for router A:

::
    
    AS 64524
    router-id 172.24.17.1
    fib-update yes
    
    rdomain 0 {
            rd 64523:0
            import-target rt 64524:0
            export-target rt 64524:0
            
            network inet connected
            network 0.0.0.0/0
            network inet6 connected
            network ::/0
    
    }
    rdomain 1 {
            rd 64523:1
            import-target rt 64524:1
            export-target rt 64524:1
            
            network inet connected
            #network 0.0.0.0/0
            network inet6 connected
            #network ::/0
    
    }
    group ibgp {
            announce IPv4 unicast
            announce IPv6 unicast
            remote-as 64524
            neighbor 2001:db8:0:17::2 {
                descr "selena"
            }
            neighbor 172.24.17.2 {
                descr "selena"
            }
    }
    
    deny from any
    allow from any inet prefixlen 8 - 24
    allow from any inet6 prefixlen 16 - 48
    
    # accept a default route (since the previous rule blocks this)
    #allow from any prefix 0.0.0.0/0
    #allow from any prefix ::/0
    
    # filter bogus networks according to RFC5735
    #deny from any prefix 0.0.0.0/8 prefixlen >= 8           # 'this' network [RFC1122]
    deny from any prefix 10.0.0.0/8 prefixlen >= 8          # private space [RFC1918]
    deny from any prefix 100.64.0.0/10 prefixlen >= 10      # CGN Shared [RFC6598]
    deny from any prefix 127.0.0.0/8 prefixlen >= 8         # localhost [RFC1122]
    deny from any prefix 169.254.0.0/16 prefixlen >= 16     # link local [RFC3927]
    deny from any prefix 172.16.0.0/12 prefixlen >= 12      # private space [RFC1918]
    deny from any prefix 192.0.2.0/24 prefixlen >= 24       # TEST-NET-1 [RFC5737]
    deny from any prefix 192.168.0.0/16 prefixlen >= 16     # private space [RFC1918]
    deny from any prefix 198.18.0.0/15 prefixlen >= 15      # benchmarking [RFC2544]
    deny from any prefix 198.51.100.0/24 prefixlen >= 24    # TEST-NET-2 [RFC5737]
    deny from any prefix 203.0.113.0/24 prefixlen >= 24     # TEST-NET-3 [RFC5737]
    deny from any prefix 224.0.0.0/4 prefixlen >= 4         # multicast
    deny from any prefix 240.0.0.0/4 prefixlen >= 4         # reserved
    
    # filter bogus IPv6 networks according to IANA
    #deny from any prefix ::/8 prefixlen >= 8
    deny from any prefix 0100::/64 prefixlen >= 64          # Discard-Only [RFC6666]
    deny from any prefix 2001:2::/48 prefixlen >= 48        # BMWG [RFC5180]
    deny from any prefix 2001:10::/28 prefixlen >= 28       # ORCHID [RFC4843]
    deny from any prefix 2001:db8::/32 prefixlen >= 32      # docu range [RFC3849]
    deny from any prefix 3ffe::/16 prefixlen >= 16          # old 6bone
    deny from any prefix fc00::/7 prefixlen >= 7            # unique local unicast
    deny from any prefix fe80::/10 prefixlen >= 10          # link local unicast
    deny from any prefix fec0::/10 prefixlen >= 10          # old site local unicast
    deny from any prefix ff00::/8 prefixlen >= 8            # multicast
    
    allow from any prefix 2001:db8:0::/56 prefixlen >= 64
    # This allow should override the deny 172.16.0.0/12 above.
    allow from any prefix 172.24.0.0/16 prefixlen >= 24      # private space [RFC1918]
    
    

So lets break this down.

::
    
    AS 64524
    router-id 172.24.17.1
    fib-update yes
    

This configuration snippet defines our AS, our router ID and that we want to update the routing tables (forwarding information base)

::
    
    rdomain 0 {
            rd 64523:0
            import-target rt 64524:0
            export-target rt 64524:0
            
            network inet connected
            network 0.0.0.0/0
            network inet6 connected
            network ::/0
    
    }
    

This looks similar to the configuration of rdomain 1. We define the community with the rd statement, route distinguisher. We define that we will only be importing routes from the AS:community identifier provided by the other BGP instance. We also define that we are exporting our routes from this rdomain to the specified AS:community. 

Finally, we define the networks that we will advertise in BGP. We could define these manually, or by stating network inet[6] connected, we automatically will export any interface that exists within this rdomain.

::
    
    group ibgp {
            announce IPv4 unicast
            announce IPv6 unicast
            remote-as 64524
            neighbor 2001:db8:0:17::2 {
                descr "selena"
            }
            neighbor 172.24.17.2 {
                descr "selena"
            }
    }
    

This defines our connection to the other bgp neighbour. A big gotcha here is that BGP4 only exports ipv4 routes over an ipv4 connection, and ipv6 over an ipv6 connection. You must therefore define both ipv4 and ipv6 to export both types of routers to the other router. 

Finally, the allow / deny statements filter the valid networks that we accept for fib updates. This should always be defined to guarantee that your don't accidentally accept routes that should not be present. 

Router B has a nearly identical configuration, just change the neighbour definitions over.

Happy routing!


UPDATE: Thanks to P. Caetano for advice on improving the filter allow/deny section.

