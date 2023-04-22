+++
title = "Using ramdisks with Cargo"
date = 2019-08-26
slug = "2019-08-26-using_ramdisks_with_cargo"
# This is relative to the root!
aliases = [ "2019/08/26/using_ramdisks_with_cargo.html", "blog/html/2019/08/26/using_ramdisks_with_cargo.html" ]
+++
# Using ramdisks with Cargo

I have a bit of a history of killing SSDs - probably because I do a bit
too much compiling and management of thousands of tiny files. Plenty of
developers have this problem! So while thinking one evening, I was
curious if I could setup a ramdisk on my mac for my cargo work to output
to.

## Making the ramdisk

On Linux you\'ll need to use tmpfs or some access to /dev/shm.

On OSX you need to run a script like the following:

    diskutil partitionDisk $(hdiutil attach -nomount ram://4096000) 1 GPTFormat APFS 'ramdisk' '100%'

This creates and mounts a 4GB ramdisk to /Volumes/ramdisk. Make sure you
have enough ram!

## Asking cargo to use it

We probably don\'t want to make our changes permant in Cargo.toml, so
we\'ll use the environment:

    CARGO_TARGET_DIR=/Volumes/ramdisk/rs cargo ...

## Does it work?

Yes!

Disk Build (SSD, 2018MBP)

    Finished dev [unoptimized + debuginfo] target(s) in 2m 29s

4 GB APFS ramdisk

    Finished dev [unoptimized + debuginfo] target(s) in 1m 53s

For me it\'s more valuable to try and save those precious SSD write
cycles, so I think I\'ll try to stick with this setup. You can see how
much rust writes by doing a clean + build. My project used the
following:

    Filesystem                             Size   Used  Avail Capacity    iused               ifree %iused  Mounted on
    /dev/disk110s1                        2.0Gi  1.2Gi  751Mi    63%       3910 9223372036854771897    0%   /Volumes/ramdisk

## Make it permanent

Put the following in
/Library/LaunchDaemons/au.net.blackhats.fy.ramdisk.plist

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
            <dict>
                    <key>Label</key>
                    <string>au.net.blackhats.fy.ramdisk</string>
                    <key>Program</key>
                    <string>/usr/local/libexec/ramdisk.sh</string>
                    <key>RunAtLoad</key>
                    <true/>
                    <key>StandardOutPath</key>
                    <string>/var/log/ramdisk.log</string>
            </dict>
    </plist>

And the following into /usr/local/libexec/ramdisk.sh

    #!/bin/bash
    date
    diskutil partitionDisk $(hdiutil attach -nomount ram://4096000) 1 GPTFormat APFS 'ramdisk' '100%'

Finally put this in your [cargo file of
choice](https://doc.rust-lang.org/cargo/reference/config.html)

    [build]
    target-dir = "/Volumes/ramdisk/rs"

Future william will need to work out if there are negative consequences
to multiple cargo projects sharing the same target directory \... hope
not!

## Launchctl tips

    # Init the service
    launchctl load /Library/LaunchDaemons/au.net.blackhats.fy.ramdisk.plist

## References

[lanuchd.info](https://www.launchd.info/)

