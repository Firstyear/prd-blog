Debugging MacOS bluetooth audio stutter
=======================================

I was noticing that audio to my bluetooth headphones from my iPhone was always flawless, but I started
to noticed stutter and drops from my MBP. After exhausting some basic ideas, I was stumped.

To the duck duck go machine, and I searched for issues with bluetooth known issues. Nothing
appeared.

However, I then decided to debug the issue - thankfully there was plenty of advice on this matter.
Press shift + option while clicking bluetooth in the menu-bar, and then you have a debug menu.
You can also open Console.app and search for "bluetooth" to see all the bluetooth related logs.

I noticed that when the audio stutter occured that the following pattern was observed.

::

    default	11:25:45.840532 +1000	wirelessproxd	About to scan for type: 9 - rssi: -90 - payload: <00000000 00000000 00000000 00000000 00000000 0000> - mask: <00000000 00000000 00000000 00000000 00000000 0000> - peers: 0
    default	11:25:45.840878 +1000	wirelessproxd	Scan options changed: YES
    error	11:25:46.225839 +1000	bluetoothaudiod	Error sending audio packet: 0xe00002e8
    error	11:25:46.225899 +1000	bluetoothaudiod	Too many outstanding packets. Drop packet of 8 frames (total drops:451 total sent:60685 percentDropped:0.737700) Outstanding:17

There was always a scan, just before the stutter initiated. So what was scanning?

I searched for the error related to packets, and there were a lot of false leads. From weird
apps to dodgy headphones. In this case I could eliminate both as the headphones worked with other
devices, and I don't have many apps installed.

So I went back and thought about what macOS services could be the problem, and I found that
airdrop would scan periodically for other devices to send and recieve files. Disabling Airdrop
from the sharing menu in System Prefrences cleared my audio right up.





.. author:: default
.. categories:: none
.. tags:: none
.. comments::
