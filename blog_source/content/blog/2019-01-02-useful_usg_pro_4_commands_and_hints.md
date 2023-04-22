+++
title = "Useful USG pro 4 commands and hints"
date = 2019-01-02
slug = "2019-01-02-useful_usg_pro_4_commands_and_hints"
# This is relative to the root!
aliases = [ "2019/01/02/useful_usg_pro_4_commands_and_hints.html" ]
+++
# Useful USG pro 4 commands and hints

I\'ve recently changed from a FreeBSD vm as my router to a Ubiquiti PRO
USG4. It\'s a solid device, with many great features, and I\'m really
impressed at how it \"just works\" in many cases. So far my only
disappointment is lack of documentation about the CLI, especially for
debugging and auditing what is occuring in the system, and for
troubleshooting steps. This post will aggregate some of my knowledge
about the topic.

## Current config

Show the current config with:

    mca-ctrl -t dump-cfg

You can show system status with the \"show\" command. Pressing ? will
cause the current compeletion options to be displayed. For example:

    # show <?>
    arp              date             dhcpv6-pd        hardware

## DNS

The following commands show the DNS statistics, the DNS configuration,
and allow changing the cache-size. The cache-size is measured in number
of records cached, rather than KB/MB. To make this permanent, you need
to apply the change to config.json in your controllers sites folder.

    show dns forwarding statistics
    show system name-server
    set service dns forwarding cache-size 10000
    clear dns forwarding cache

## Logging

You can see and aggregate of system logs with

    show log

Note that when you set firewall rules to \"log on block\" they go to
dmesg, not syslog, so as a result you need to check dmesg for these.

It\'s a great idea to forward your logs in the controller to a syslog
server as this allows you to aggregate and see all the events occuring
in a single time series (great when I was diagnosing an issue recently).

## Interfaces

To show the system interfaces

    show interfaces

To restart your pppoe dhcp6c:

    release dhcpv6-pd interface pppoe0
    renew dhcpv6-pd interface pppoe0

There is a current issue where the firmware will start dhcp6c on eth2
and pppoe0, but the session on eth2 blocks the pppoe0 client. As a
result, you need to release on eth2, then renew of pppoe0

If you are using a dynamic prefix rather than static, you may need to
reset your dhcp6c duid.

    delete dhcpv6-pd duid

To restart an interface with the vyatta tools:

    disconnect interface pppoe
    connect interface pppoe

## OpenVPN

I have setup customised OpenVPN tunnels. To show these:

    show interfaces openvpn detail

These are configured in config.json with:

    # Section: config.json - interfaces - openvpn
        "vtun0": {
                "encryption": "aes256",
                # This assigns the interface to the firewall zone relevant.
                "firewall": {
                        "in": {
                                "ipv6-name": "LANv6_IN",
                                "name": "LAN_IN"
                        },
                        "local": {
                                "ipv6-name": "LANv6_LOCAL",
                                "name": "LAN_LOCAL"
                        },
                        "out": {
                                "ipv6-name": "LANv6_OUT",
                                "name": "LAN_OUT"
                        }
                },
                "mode": "server",
                # By default, ubnt adds a number of parameters to the CLI, which
                # you can see with ps | grep openvpn
                "openvpn-option": [
                        # If you are making site to site tunnels, you need the ccd
                        # directory, with hostname for the file name and
                        # definitions such as:
                        # iroute 172.20.0.0 255.255.0.0
                        "--client-config-dir /config/auth/openvpn/ccd",
                        "--keepalive 10 60",
                        "--user nobody",
                        "--group nogroup",
                        "--proto udp",
                        "--port 1195"
                ],
                "server": {
                        "push-route": [
                                "172.24.0.0/17"
                        ],
                        "subnet": "172.24.251.0/24"
                },
                "tls": {
                        "ca-cert-file": "/config/auth/openvpn/vps/vps-ca.crt",
                        "cert-file": "/config/auth/openvpn/vps/vps-server.crt",
                        "dh-file": "/config/auth/openvpn/dh2048.pem",
                        "key-file": "/config/auth/openvpn/vps/vps-server.key"
                }
        },

## Netflow

Net flows allow a set of connection tracking data to be sent to a remote
host for aggregation and analysis. Sadly this process was mostly
undocumented, bar some useful forum commentors. Here is the process that
I came up with. This is how you configure it live:

    set system flow-accounting interface eth3.11
    set system flow-accounting netflow server 172.24.10.22 port 6500
    set system flow-accounting netflow version 5
    set system flow-accounting netflow sampling-rate 1
    set system flow-accounting netflow timeout max-active-life 1
    commit

To make this persistent:

    "system": {
                "flow-accounting": {
                        "interface": [
                                "eth3.11",
                                "eth3.12"
                        ],
                        "netflow": {
                                "sampling-rate": "1",
                                "version": "5",
                                "server": {
                                        "172.24.10.22": {
                                                "port": "6500"
                                        }
                                },
                                "timeout": {
                                        "max-active-life": "1"
                                }
                        }
                }
        },

To show the current state of your flows:

    show flow-accounting

