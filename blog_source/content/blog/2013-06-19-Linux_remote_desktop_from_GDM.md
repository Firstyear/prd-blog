+++
title = "Linux remote desktop from GDM"
date = 2013-06-19
slug = "2013-06-19-Linux_remote_desktop_from_GDM"
# This is relative to the root!
aliases = [ "2013/06/19/Linux_remote_desktop_from_GDM.html", "blog/html/2013/06/19/Linux_remote_desktop_from_GDM.html" ]
+++
# Linux remote desktop from GDM

For quite some time I have wanted to be able to create thin linux
workstations that automatically connect to a remote display manager of
some kind for the relevant desktop services. This has always been
somewhat of a mystery to me, but I found the final answer to be quite
simple.

First, you need a system like a windows Remote Desktop server, or xrdp
server configured. Make sure that you can connect and login to it.

Now install your thin client. I used CentOS with a minimal desktop
install to give me an X server.

Install the \"rdesktop\" package on your thin client.

Now you need to add the Remote Desktop session type.

Create the file \"/usr/bin/rdesktop-session\" (Or /opt or /srv. Up to
you - but make sure it\'s executable)

    #!/bin/bash
    /usr/bin/rdesktop -d domain.example.com -b -a 32 -x lan -f termserv.example.com

Now you need to create a session type that GDM will recognise. Put this
into \"/usr/share/xsessions/rdesktop.desktop\". These options could be
improved etc.

    [Desktop Entry]
    Name=RDesktop
    Comment=This session logs you into RDesktop
    Exec=/usr/bin/rdesktop-session
    TryExec=/usr/bin/rdesktop-session
    Terminal=True
    Type=Application

    [Window Manager]
    SessionManaged=true

Create a user who will automatically connect to the TS.

    useradd remote_login

Configure GDM to automatically login after a time delay. The reason for
the time delay, is so that after the rdesktop session is over, at the
GDM display, a staff member can shutdown the thin client.

    [daemon]
    TimedLoginEnable=True
    TimedLogin=remote_login
    TimedLoginDelay=15

Finally, set the remote login user\'s session to RDesktop
\"/home/remote_login/.dmrc\"

    [Desktop]
    Session=rdesktop

And that\'s it!

If you are using windows terminal services, you will notice that the
login times out after about a minute, GDM will reset, wait 15 seconds
and connect again, causing a loop of this action. To prevent this, you
should extend the windows server login timeout. On the terminal server:

    HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\[[Connection endpoint]]\LogonTimeout (DWord, seconds for timeout)

\[\[Connection endpoint\]\] is the name in RD Session Host
configurations : I had rebuilt mine as default and was wondering why
this no longer worked. This way you can apply the logon timeout to
different session connections.

Update: Actually, it needs to be RDP-Tcp regardless of the connection
endpoint. Bit silly.
