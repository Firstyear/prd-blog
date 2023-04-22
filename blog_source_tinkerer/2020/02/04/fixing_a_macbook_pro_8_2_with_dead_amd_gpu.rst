Fixing a MacBook Pro 8,2 with dead AMD GPU
==========================================

I've owned a MacBook Pro 8,2 late 2011 edition, which I used from 2011 to about 2018. It was a great
piece of hardware, and honestly I'm surprised it lasted so long given how many MacOS and Fedora
installs it's seen.

I upgraded to a MacBook Pro 15,1, and I gave the 8,2 to a friend who was in need of a new computer
so she could do her work. It worked really well for her until today when she's messaged me that
the machine is having a problem.

The Problem
-----------

The machine appeared to be in a bootloop, where just before swapping from the EFI GPU to the
main display server, it would go black and then lock up/reboot. Booting to single user mode
(boot holding cmd + s)
showed the machine's disk was intact with a clean apfs. The system.log showed corruption at the time
of the fault, which didn't instill confidence in me.

Attempting a recovery boot (boot holding cmd + r), this also yielded the bootloop. So we have potentially eliminated
the installed copy of MacOS as the source of the issue.

I've then used the apple hardware test (boot while holding d), and it has passed the machine as a clear
bill of health.

I have seen one of these machines give up in the past - my friends mother had one from the same
generation and that died in almost the same way - could it be the same?

The 8,2's cursed gpu stack
--------------------------

The 8,2 15" mbp has dual gpu's - it has the on cpu Intel 3000, and an AMD radeon 6750M. The two pass
through an LVDS graphics multiplexer to the main panel. The external display port however is not
so clear - the DDC lines are passed through the GMUX, but the datalines directly attach to the
the display port.

The machine is also able to boot with EFI rendering to either card. By default this is the AMD radeon.
Which ever card is used at boot is also the first card MacOS attempts to use, but it will try to swap
to the radeon later on.

This generation had a large number of the radeons develop faults in their 3d rendering capability
so it would render the EFI buffer correctly, but on the initiation of 3d rendering it would fail.
Sounds like what we have here!

To fix this ...
---------------

Okay, so this is fixable. First, we need to tell EFI to boot primarily from the intel card. Boot
to single user mode and then run.

::

    nvram fa4ce28d-b62f-4c99-9cc3-6815686e30f9:gpu-power-prefs=%01%00%00%00

Now we need to prevent loading of the AMD drivers so that during the boot MacOS doesn't attempt
to swap from Intel to the Radeon. We can do this by hiding the drivers. System integrity protection
will stop you, so you need to do this as part of recovery. Boot with cmd + r, which now works thanks
to the EFI changes, then open terminal

::

    cd /Volumes/Macintosh HD
    sudo mkdir amdkext
    sudo mv System/Library/Extensions/AMDRadeonX3000.kext amdkext/

Then reboot. You'll notice the fans go crazy because the Radeon card can't be disabled without the driver.
We can post-boot load the driver to stop the fans to fix this up.

To achieve this we make a helper script:

::

    # cat /usr/local/libexec/amd_kext_load.sh
    #!/bin/sh
    /sbin/kextload /amdkext/AMDRadeonX3000.kext

And a launchctl daemon

::

    # cat /Library/LaunchDaemons/au.net.blackhats.fy.amdkext.plist
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
            <dict>
                    <key>Label</key>
                    <string>au.net.blackhats.fy.amdkext</string>
                    <key>Program</key>
                    <string>/usr/local/libexec/amd_kext_load.sh</string>
                    <key>RunAtLoad</key>
                    <true/>
                    <key>StandardOutPath</key>
                    <string>/var/log/amd_kext_load.log</string>
            </dict>
    </plist>

Now if you reboot, you'll have a working mac, and the fans will stop properly. I've tested this with
suspend and resume too and it works! The old beast continues to live :)


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
