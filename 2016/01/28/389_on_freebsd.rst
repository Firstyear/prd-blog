389 on freebsd
==============
I've decided to start porting 389-ds to freebsd.

So tonight I took the first steps. Let's see if we can get it to build in a dev environment like I would use normally.

You will need to install these deps:

::
    
    autotools
    git
    openldap-client
    db5
    cyrus-sasl
    pkgconf
    nspr
    nss
    net-snmp
    

You then need to install svrcore. I'll likely add a port for this too.

::
    
    fetch https://ftp.mozilla.org/pub/directory/svrcore/releases/4.0.4/src/svrcore-4.0.4.tar.bz2
    tar -xvjf svrcore-4.0.4.tar.bz2
    cd svrcore-4.0.4
    ./configure --prefix=/opt/svrcore
    make
    sudo make install
    

Now you can clone ds and try to build it:

::
    
    cd
    git clone https://git.fedorahosted.org/git/389/ds.git
    cd ds
    ./configure --prefix=/opt/dirsrv --with-openldap=/usr/local --with-db --with-db-inc=/usr/local/include/db5/ --with-db-lib=/usr/local/lib/db5/ --with-sasl --with-sasl-inc=/usr/local/include/sasl/ --with-sasl-lib=/usr/local/lib/sasl2/ --with-svrcore-inc=/opt/svrcore/include/ --with-svrcore-lib=/opt/svrcore/lib/ --with-netsnmp=/usr/local
    make
    

If it's like me you get the following:

::
    
    make: "/usr/home/admin_local/ds/Makefile" line 10765: warning: duplicate script for target "%/dirsrv" ignored
    make: "/usr/home/admin_local/ds/Makefile" line 10762: warning: using previous script for "%/dirsrv" defined here
    make: "/usr/home/admin_local/ds/Makefile" line 10767: warning: duplicate script for target "%/dirsrv" ignored
    make: "/usr/home/admin_local/ds/Makefile" line 10762: warning: using previous script for "%/dirsrv" defined here
    make: "/usr/home/admin_local/ds/Makefile" line 10768: warning: duplicate script for target "%/dirsrv" ignored
    make: "/usr/home/admin_local/ds/Makefile" line 10762: warning: using previous script for "%/dirsrv" defined here
    perl ./ldap/servers/slapd/mkDBErrStrs.pl -i /usr/local/include/db5/ -o .
    make  all-am
    make[1]: "/usr/home/admin_local/ds/Makefile" line 10765: warning: duplicate script for target "%/dirsrv" ignored
    make[1]: "/usr/home/admin_local/ds/Makefile" line 10762: warning: using previous script for "%/dirsrv" defined here
    make[1]: "/usr/home/admin_local/ds/Makefile" line 10767: warning: duplicate script for target "%/dirsrv" ignored
    make[1]: "/usr/home/admin_local/ds/Makefile" line 10762: warning: using previous script for "%/dirsrv" defined here
    make[1]: "/usr/home/admin_local/ds/Makefile" line 10768: warning: duplicate script for target "%/dirsrv" ignored
    make[1]: "/usr/home/admin_local/ds/Makefile" line 10762: warning: using previous script for "%/dirsrv" defined here
    depbase=`echo ldap/libraries/libavl/avl.o | sed 's|[^/]*$|.deps/&|;s|\.o$||'`; cc -DHAVE_CONFIG_H -I.     -DBUILD_NUM= -DVENDOR="\"389 Project\"" -DBRAND="\"389\"" -DCAPBRAND="\"389\""  -UPACKAGE_VERSION -UPACKAGE_TARNAME -UPACKAGE_STRING -UPACKAGE_BUGREPORT -I./ldap/include -I./ldap/servers/slapd -I./include -I.  -DLOCALSTATEDIR="\"/opt/dirsrv/var\"" -DSYSCONFDIR="\"/opt/dirsrv/etc\""  -DLIBDIR="\"/opt/dirsrv/lib\"" -DBINDIR="\"/opt/dirsrv/bin\""  -DDATADIR="\"/opt/dirsrv/share\"" -DDOCDIR="\"/opt/dirsrv/share/doc/389-ds-base\""  -DSBINDIR="\"/opt/dirsrv/sbin\"" -DPLUGINDIR="\"/opt/dirsrv/lib/dirsrv/plugins\"" -DTEMPLATEDIR="\"/opt/dirsrv/share/dirsrv/data\""     -g -O2 -MT ldap/libraries/libavl/avl.o -MD -MP -MF $depbase.Tpo -c -o ldap/libraries/libavl/avl.o ldap/libraries/libavl/avl.c && mv -f $depbase.Tpo $depbase.Po
    rm -f libavl.a
    ar cru libavl.a ldap/libraries/libavl/avl.o
    ranlib libavl.a
    cc -DHAVE_CONFIG_H -I.     -DBUILD_NUM= -DVENDOR="\"389 Project\"" -DBRAND="\"389\"" -DCAPBRAND="\"389\""  -UPACKAGE_VERSION -UPACKAGE_TARNAME -UPACKAGE_STRING -UPACKAGE_BUGREPORT -I./ldap/include -I./ldap/servers/slapd -I./include -I.  -DLOCALSTATEDIR="\"/opt/dirsrv/var\"" -DSYSCONFDIR="\"/opt/dirsrv/etc\""  -DLIBDIR="\"/opt/dirsrv/lib\"" -DBINDIR="\"/opt/dirsrv/bin\""  -DDATADIR="\"/opt/dirsrv/share\"" -DDOCDIR="\"/opt/dirsrv/share/doc/389-ds-base\""  -DSBINDIR="\"/opt/dirsrv/sbin\"" -DPLUGINDIR="\"/opt/dirsrv/lib/dirsrv/plugins\"" -DTEMPLATEDIR="\"/opt/dirsrv/share/dirsrv/data\""  -I./lib/ldaputil -I/usr/local/include  -I/usr/local/include/nss -I/usr/local/include/nss/nss -I/usr/local/include/nspr   -I/usr/local/include/nspr   -g -O2 -MT lib/ldaputil/libldaputil_a-cert.o -MD -MP -MF lib/ldaputil/.deps/libldaputil_a-cert.Tpo -c -o lib/ldaputil/libldaputil_a-cert.o `test -f 'lib/ldaputil/cert.c' || echo './'`lib/ldaputil/cert.c
    In file included from lib/ldaputil/cert.c:16:
    /usr/include/malloc.h:3:2: error: "<malloc.h> has been replaced by <stdlib.h>"
    #error "<malloc.h> has been replaced by <stdlib.h>"
     ^
    1 error generated.
    *** Error code 1
    
    Stop.
    make[1]: stopped in /usr/home/admin_local/ds
    *** Error code 1
    
    Stop.
    make: stopped in /usr/home/admin_local/ds
    
    

Time to start looking at including some #ifdef __FREEBSD__ macros.
