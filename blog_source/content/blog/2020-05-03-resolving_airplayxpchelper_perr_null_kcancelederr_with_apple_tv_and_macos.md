+++
title = "Resolving AirPlayXPCHelper Perr NULL kCanceledErr with Apple TV and MacOS"
date = 2020-05-03
slug = "2020-05-03-resolving_airplayxpchelper_perr_null_kcancelederr_with_apple_tv_and_macos"
# This is relative to the root!
aliases = [ "2020/05/03/resolving_airplayxpchelper_perr_null_kcancelederr_with_apple_tv_and_macos.html" ]
+++
# Resolving AirPlayXPCHelper Perr NULL kCanceledErr with Apple TV and MacOS

I decided to finally get an Apple TV so that I could use my iPad and
MacBook Pro to airplay to my projector. So far I\'ve been really
impressed by it and how well it works with modern amplifiers and my
iPad.

Sadly though, when I tried to use my MacBook pro to airplay to the Apple
TV I recieved an \"Unable to connect\" error, with no further
description.

## Initial Research

The first step was to look in console.app at the local system logs. The
following item stood out:

    error 09:24:41.459722+1000 AirPlayXPCHelper ### Error: CID 0xACF10006, Peer NULL, -6723/0xFFFFE5BD kCanceledErr

I only found a single result on a search for this, and they resolved the
problem by disabling their MacOS firewall - attempting this myself did
not fix the issue. There are also reports of apple service staff
disabling the firewall to resolve airplay problems too.

## Time to Dig Further \...

Now it was time to look more. To debug an Apple TV you need to connect a
USB-C cable to it\'s service port on the rear of the device, while you
connect this to a Mac on the other side. Console.app will then show you
the streamed logs from the device.

While looking on the Apple TV I noticed the following log item:

    [AirPlay] ### [0x8F37] Set up session 16845584210140482044 with [<ipv6 address>:3378]:52762 failed: 61/0x3D ECONNREFUSED {
    "timingProtocol" : "NTP",
    "osName" : "Mac OS X",
    ...
    "isScreenMirroringSession" : true,
    "osVersion" : "10.15.4",
    "timingPort" : 64880,
    ...
    }

I have trimmed this log, as most details don\'t matter. What is
important is that it looks like the Apple TV is attempting to
back-connect to the MacBook Pro, which has a connection refused. From
iOS it appears that the video/timing channel is initiated from the iOS
device, so no back-connection is required, but for AirPlay to work from
the MacBook Pro to the Apple TV, the Apple TV must be able to connect
back on high ports with new UDP/TCP sessions for NTP to synchronise
clocks.

## My Network

My MacBook pro is on a seperate VLAN to my Apple TV for security
reasons, mainly because I don\'t want most devices to access management
consoles of various software that I have installed. I have used the
Avahi reflector on my USG to enable cross VLAN discovery. This would
appear to be issue, is that my firewall is not allowing the NTP traffic
back to my MacBook pro.

To resolve this I allowed some high ports from the Apple TV to connect
back to the VLAN my MacBook Pro is on, and I allowed built-in software
to recieve connections.

Once this was done, I was able to AirPlay across VLANs to my Apple TV!

