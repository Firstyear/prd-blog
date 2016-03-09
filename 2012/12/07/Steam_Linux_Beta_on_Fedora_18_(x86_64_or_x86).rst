Steam Linux Beta on Fedora 18 (x86 64 or x86)
=============================================
These instructions are old! Use this instead:

::
    
    wget http://spot.fedorapeople.org/steam/steam.repo -O /etc/yum.repos.d/steam.repo
    yum install steam
    

OLD METHOD below

Get the .deb. 

Unpack it with
::
    
    ar x steam.deb
    tar -xvzf data.tar.gz -C /
    

Now install

::
    
    yum install glibc.i686 \
    libX11.i686 \
    libstdc++.i686 \
    mesa-libGL.i686 \
    mesa-dri-drivers.i686 \
    libtxc_dxtn.i686 \
    libXrandr.i686 \
    pango.i686 \
    gtk2.i686 \
    alsa-lib.i686 \
    nss.i686 \
    libpng12.i686 \
    openal-soft.i686 \
    pulseaudio-libs.i686
    

Now you should be able to run the steam client from /usr/bin/steam or from the Applications - Games menu

If you have issues, try 
::
    
    cd ~/.local/share/Steam
    LD_DEBUG="libs" ./steam.sh
    

To see what is going on. Sometimes you will see something like 
::
    
          9228:	  trying file=tls/i686/sse2/libGL.so.1
          9228:	  trying file=tls/i686/libGL.so.1
          9228:	  trying file=tls/sse2/libGL.so.1
          9228:	  trying file=tls/libGL.so.1
          9228:	  trying file=i686/sse2/libGL.so.1
          9228:	  trying file=i686/libGL.so.1
          9228:	  trying file=sse2/libGL.so.1
          9228:	  trying file=libGL.so.1
          9228:	 search cache=/etc/ld.so.cache
          9228:	 search path=/lib/i686:/lib/sse2:/lib:/usr/lib/i686:/usr/lib/sse2:/usr/lib		(system search path)
          9228:	  trying file=/lib/i686/libGL.so.1
          9228:	  trying file=/lib/sse2/libGL.so.1
          9228:	  trying file=/lib/libGL.so.1
          9228:	  trying file=/usr/lib/i686/libGL.so.1
          9228:	  trying file=/usr/lib/sse2/libGL.so.1
          9228:	  trying file=/usr/lib/libGL.so.1
    

And the steam client will then hang, or say "Error loading steamui.so". It is because you are missing libGL.so.1 in this case. 

running ldd against the files in ".local/share/Steam/ubuntu12_32/" should reveal most of the deps you need.
