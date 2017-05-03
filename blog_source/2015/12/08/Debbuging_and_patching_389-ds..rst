Debbuging and patching 389-ds.
==============================
Debugging and working on software like 389-ds looks pretty daunting. However, I think it's one of the easiest projects to setup, debug and contribute to (for a variety of reasons).

Fixing issues like the one referenced in this post is a good way to get your hands dirty into C, gdb, and the project in general. It's how I started, by solving small issues like this, and working up to managing larger fixes and commits. You will end up doing a lot of research and testing, but you learn a lot for it.

Additionally, the 389-ds team are great people, and very willing to help and walk you through debugging and issue solving like this. 

Lets get started!

First, lets get your build env working. 

::
    
    git clone http://git.fedorahosted.org/git/389/ds.git
    

If you need to apply any patches to test, now is the time:

::
    
    cd ds
    git am ~/path/to/patch
    

Now we can actually get all the dependencies. Changes these paths to suit your environment.

::
    
    export DSPATH=~/development/389ds/ds
    sudo yum-builddep 389-ds-base
    sudo yum install libasan llvm
    mkdir -p ~/build/ds/
    cd ~/build/ds/ && $DSPATH/configure --with-openldap --enable-debug --enable-asan --prefix=/opt/dirsrv/
    make -C ~/build/ds
    sudo make -C ~/build/ds install
    

NOTE: Thanks to Viktor for the tip about yum-builddep working without a spec file.

If you are still missing packages, these commands are rough, but work.

::
    
    sudo yum install `grep "^BuildRequires" $DSPATH/rpm/389-ds-base.spec.in | awk '{ print $2 }' | grep -v "^/"`
    sudo yum install `grep "^Requires:" $DSPATH/ds/rpm/389-ds-base.spec.in | awk '{ print $2 $3 $4 $5 $6 $7 }' | grep -v "^/" | grep -v "name"`
    

Now with that out the way, we can get into it. Setup the ds install:

::
    
    sudo /opt/dirsrv/sbin/setup-ds.pl --debug General.StrictHostChecking=false
    

If you have enabled ASAN you may notice that the install freezes trying to start slapd. That's okay, at this point you can control C it. If setup-ds.pl finishes, even better.

Now lets run the instance up:

::
    
    sudo -s
    export ASAN_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
    export ASAN_OPTIONS=symbolize=1
    /opt/dirsrv/sbin/ns-slapd -d 0 -D /opt/dirsrv/etc/dirsrv/slapd-localhost
    

::
    
    [08/Dec/2015:13:09:01 +1000] - 389-Directory/1.3.5 B2015.342.252 starting up
    =================================================================
    ==28682== ERROR: AddressSanitizer: unknown-crash on address 0x7fff49a54ff0 at pc 0x7f59bc0f719f bp 0x7fff49a54c80 sp 0x7fff49a54c28
    

Uh oh! We have a crash. Lets work it out.

::
    
    =================================================================
    ==28682== ERROR: AddressSanitizer: unknown-crash on address 0x7fff49a54ff0 at pc 0x7f59bc0f719f bp 0x7fff49a54c80 sp 0x7fff49a54c28
    WRITE of size 513 at 0x7fff49a54ff0 thread T0
        #0 0x7f59bc0f719e in scanf_common /usr/src/debug/gcc-4.8.3-20140911/obj-x86_64-redhat-linux/x86_64-redhat-linux/libsanitizer/asan/../../../../libsanitizer/sanitizer_common/sanitizer_common_interceptors_scanf.inc:305
        #1 0x7f59bc0f78b6 in __interceptor_vsscanf /usr/src/debug/gcc-4.8.3-20140911/obj-x86_64-redhat-linux/x86_64-redhat-linux/libsanitizer/asan/../../../../libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc:262
        #2 0x7f59bc0f79e9 in __interceptor_sscanf /usr/src/debug/gcc-4.8.3-20140911/obj-x86_64-redhat-linux/x86_64-redhat-linux/libsanitizer/asan/../../../../libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc:297
        #3 0x7f59b141e060 in read_metadata.isra.5 /home/wibrown/development/389ds/ds/ldap/servers/slapd/back-ldbm/dblayer.c:5268
        #4 0x7f59b1426b63 in dblayer_start /home/wibrown/development/389ds/ds/ldap/servers/slapd/back-ldbm/dblayer.c:1587
        #5 0x7f59b14d698e in ldbm_back_start /home/wibrown/development/389ds/ds/ldap/servers/slapd/back-ldbm/start.c:225
        #6 0x7f59bbd2dc60 in plugin_call_func /home/wibrown/development/389ds/ds/ldap/servers/slapd/plugin.c:1920
        #7 0x7f59bbd2e8a7 in plugin_call_one /home/wibrown/development/389ds/ds/ldap/servers/slapd/plugin.c:1870
        #8 0x7f59bbd2e8a7 in plugin_dependency_startall.isra.10.constprop.13 /home/wibrown/development/389ds/ds/ldap/servers/slapd/plugin.c:1679
        #9 0x4121c5 in main /home/wibrown/development/389ds/ds/ldap/servers/slapd/main.c:1054
        #10 0x7f59b8df5af4 in __libc_start_main /usr/src/debug/glibc-2.17-c758a686/csu/libc-start.c:274
        #11 0x4133b4 in _start (/opt/dirsrv/sbin/ns-slapd+0x4133b4)
    Address 0x7fff49a54ff0 is located at offset 448 in frame <read_metadata.isra.5> of T0's stack:
      This frame has 7 object(s):
        [32, 33) 'delimiter'
        [96, 100) 'count'
        [160, 168) 'buf'
        [224, 256) 'prfinfo'
        [288, 416) 'value'
        [448, 960) 'attribute'
        [992, 5088) 'filename'
    HINT: this may be a false positive if your program uses some custom stack unwind mechanism or swapcontext
          (longjmp and C++ exceptions *are* supported)
    SUMMARY: AddressSanitizer: unknown-crash /usr/src/debug/gcc-4.8.3-20140911/obj-x86_64-redhat-linux/x86_64-redhat-linux/libsanitizer/asan/../../../../libsanitizer/sanitizer_common/sanitizer_common_interceptors_scanf.inc:305 scanf_common
    Shadow bytes around the buggy address:
      0x1000693429a0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      0x1000693429b0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      0x1000693429c0: 00 00 00 00 00 00 f1 f1 f1 f1 01 f4 f4 f4 f2 f2
      0x1000693429d0: f2 f2 04 f4 f4 f4 f2 f2 f2 f2 00 f4 f4 f4 f2 f2
      0x1000693429e0: f2 f2 00 00 00 00 f2 f2 f2 f2 00 00 00 00 00 00
    =>0x1000693429f0: 00 00 00 00 00 00 00 00 00 00 f2 f2 f2 f2[00]00
      0x100069342a00: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      0x100069342a10: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      0x100069342a20: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
      0x100069342a30: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 f2 f2
      0x100069342a40: f2 f2 00 00 00 00 00 00 00 00 00 00 00 00 00 00
    Shadow byte legend (one shadow byte represents 8 application bytes):
      Addressable:           00
      Partially addressable: 01 02 03 04 05 06 07 
      Heap left redzone:     fa
      Heap righ redzone:     fb
      Freed Heap region:     fd
      Stack left redzone:    f1
      Stack mid redzone:     f2
      Stack right redzone:   f3
      Stack partial redzone: f4
      Stack after return:    f5
      Stack use after scope: f8
      Global redzone:        f9
      Global init order:     f6
      Poisoned by user:      f7
      ASan internal:         fe
    ==28682== ABORTING
    
    

First lets focus on the stack. Specifically:

::
    
    WRITE of size 513 at 0x7fff49a54ff0 thread T0
        #0 0x7f59bc0f719e in scanf_common /usr/src/debug/gcc-4.8.3-20140911/obj-x86_64-redhat-linux/x86_64-redhat-linux/libsanitizer/asan/../../../../libsanitizer/sanitizer_common/sanitizer_common_interceptors_scanf.inc:305
        #1 0x7f59bc0f78b6 in __interceptor_vsscanf /usr/src/debug/gcc-4.8.3-20140911/obj-x86_64-redhat-linux/x86_64-redhat-linux/libsanitizer/asan/../../../../libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc:262
        #2 0x7f59bc0f79e9 in __interceptor_sscanf /usr/src/debug/gcc-4.8.3-20140911/obj-x86_64-redhat-linux/x86_64-redhat-linux/libsanitizer/asan/../../../../libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc:297
        #3 0x7f59b141e060 in read_metadata.isra.5 /home/wibrown/development/389ds/ds/ldap/servers/slapd/back-ldbm/dblayer.c:5268
        #4 0x7f59b1426b63 in dblayer_start /home/wibrown/development/389ds/ds/ldap/servers/slapd/back-ldbm/dblayer.c:1587
    

Now, we can ignore frame 0,1,2. These are all in asan. But, we do own code in frame 3. So lets take a look there as our first port of call.

::
    
    vim ldap/servers/slapd/back-ldbm/dblayer.c +5268
    
    5262             if (NULL != nextline) {                                              
    5263                 *nextline++ = '\0';                                              
    5264                 while ('\n' == *nextline) {                                      
    5265                     nextline++;                                                  
    5266                 }                                                                
    5267             }                                                                    
    5268             sscanf(thisline,"%512[a-z]%c%128s",attribute,&delimiter,value);      /* <---- THIS LINE */
    5269             if (0 == strcmp("cachesize",attribute)) {                            
    5270                 priv->dblayer_previous_cachesize = strtoul(value, NULL, 10);     
    5271             } else if (0 == strcmp("ncache",attribute)) {                        
    5272                 number = atoi(value);                                            
    5273                 priv->dblayer_previous_ncache = number;                          
    5274             } else if (0 == strcmp("version",attribute)) { 
    

So the crash is that we write of size 513 here. Lets look at the function sscanf, to see what's happening.

::
    
    man sscanf
    
    int sscanf(const char *str, const char *format, ...);
    ...
    The scanf() family of functions scans input according to format as described below
    ...
    

So, we know that we are writing something too large here. Lets checkout the size of our values at that point.

::
    
    gdb /opt/dirsrv/sbin/ns-slapd
    
    Reading symbols from /opt/dirsrv/sbin/ns-slapd...done.
    (gdb) set args -d 0 -D /opt/dirsrv/etc/dirsrv/slapd-localhost
    (gdb) break dblayer.c:5268
    No source file named dblayer.c.
    Make breakpoint pending on future shared library load? (y or [n]) y
    Breakpoint 1 (dblayer.c:5268) pending.
    (gdb) run
    Starting program: /opt/dirsrv/sbin/ns-slapd -d 0 -D /opt/dirsrv/etc/dirsrv/slapd-localhost
    [Thread debugging using libthread_db enabled]
    Using host libthread_db library "/lib64/libthread_db.so.1".
    Detaching after fork from child process 28690.
    [08/Dec/2015:13:18:08 +1000] - slapd_nss_init: chmod failed for file /opt/dirsrv/etc/dirsrv/slapd-localhost/cert8.db error (2) No such file or directory.
    [08/Dec/2015:13:18:08 +1000] - slapd_nss_init: chmod failed for file /opt/dirsrv/etc/dirsrv/slapd-localhost/key3.db error (2) No such file or directory.
    [08/Dec/2015:13:18:08 +1000] - slapd_nss_init: chmod failed for file /opt/dirsrv/etc/dirsrv/slapd-localhost/secmod.db error (2) No such file or directory.
    [08/Dec/2015:13:18:08 +1000] - 389-Directory/1.3.5 B2015.342.252 starting up
    
    Breakpoint 1, read_metadata (li=0x6028000121c0) at /home/wibrown/development/389ds/ds/ldap/servers/slapd/back-ldbm/dblayer.c:5268
    5268	            sscanf(thisline,"%512[a-z]%c%128s",attribute,&delimiter,value);
    Missing separate debuginfos, use: debuginfo-install sqlite-3.7.17-6.el7_1.1.x86_64
    
    

If you are missing more debuginfo, install them, and re-run.

::
    
    (gdb) set print repeats 20
    (gdb) print thisline
    $6 = 0x600c0015e900 "cachesize:10000000\nncache:0\nversion:5\nlocks:10000\n"
    (gdb) print attribute
    $7 = "\200\275\377\377\377\177\000\000p\275\377\377\377\177\000\000\301\066\031\020\000\000\000\000\243|\023\352\377\177\000\000\377\377\377\377\000\000\000\000\000\253bu\256\066\357oPBS\362\377\177\000\000p\277\377\377\377\177\000\000\300\317\377\377\377\177\000\000\320\356\a\000\b`\000\000\060\277\377\377\377\177\000\000\003\000\000\000\000\000\000\000\346w\377\177\000\020\000\000\262AT\362\377\177\000\000\340-T\362\377\177\000\000p\277\377\377\377\177\000\000\247\277\377\377\377\177\000\000\000\020\000\000\377\177\000\000*\021\346\364'\000\200<\240\300L\352\377\177\000\000\000\000\000\000\000\000\000\000\000\253bu\256\066\357o\003\000\000\000\000\000\000\000\210\275U\362\377\177\000\000i\000\020\000\000\000\000\000"...
    (gdb) print &delimiter
    $8 = 0x7fffffffbbb0 "*\021\346\364\377\177"
    (gdb) print value
    $9 = "A\000\000\000\000\000\000\000\070\276\377\377\377\177\000\000\020\276\377\377\377\177\000\000\001\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\330\000\001\000F`\000\000\200\375\000\000F`\000\000\257O\336\367\377\177\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\001\000\000\000\377\177\000\000\000\000\000\000\000\000\000\000\001\000\000\000\000\000\000\000\200\375\000\000F`\000\000\306c%\352\377\177\000\000\236\061T\362\377\177\000"
    

Some of these are some chunky values! Okay, lets try and see which one is a bit too big.


::
    
    (gdb) print sizeof(attribute)
    $10 = 512
    (gdb) print sizeof(&delimiter)
    $11 = 8
    (gdb) print sizeof(value)
    $12 = 128
    

So, if our write is size 513, the closest is probably the attribute variable. But it's only size 512? How is this causing an issue?

Well, if we look at the sscanf man page again for the substitution that attribute will land in (%512[a-z]) we see:

::
    
    Matches a nonempty sequence of characters from the specified set of accepted characters
    ...
    must be enough room for  all the characters in the string, plus a terminating null byte.
    

So, we have space for 512 chars, which is the size of the attribute block, but we don't have space for the null byte! So lets add it in:

::
    
    5194     char attribute[513];                                                         
    

If we keep looking at the man page we see another error too for %128s

::
    
    ...next pointer must be a pointer to character array that is long enough to hold the input sequence and the terminating null byte ('\0'), which is added automatically.
    

So lets preemptively fix that too.

::
    
    5195     char value[129], delimiter;                                                  
    

Now rebuild

::
    
    make -C ~/build/ds
    sudo make -C ~/build/ds install
    

Lets run slapd and see if it fixed it:

::
    
    sudo -s
    export ASAN_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer
    export ASAN_OPTIONS=symbolize=1
    /opt/dirsrv/sbin/ns-slapd -d 0 -D /opt/dirsrv/etc/dirsrv/slapd-localhost
    

::
    
    I0> /opt/dirsrv/sbin/ns-slapd -d 0 -D /opt/dirsrv/etc/dirsrv/slapd-localhost
    [08/Dec/2015:13:47:20 +1000] - slapd_nss_init: chmod failed for file /opt/dirsrv/etc/dirsrv/slapd-localhost/cert8.db error (2) No such file or directory.
    [08/Dec/2015:13:47:20 +1000] - slapd_nss_init: chmod failed for file /opt/dirsrv/etc/dirsrv/slapd-localhost/key3.db error (2) No such file or directory.
    [08/Dec/2015:13:47:20 +1000] - slapd_nss_init: chmod failed for file /opt/dirsrv/etc/dirsrv/slapd-localhost/secmod.db error (2) No such file or directory.
    [08/Dec/2015:13:47:20 +1000] - 389-Directory/1.3.5 B2015.342.344 starting up
    [08/Dec/2015:13:47:27 +1000] - slapd started.  Listening on All Interfaces port 389 for LDAP requests
    

Format this into a patch with git:

::
    
    git commit -a
    git format-patch HEAD~1
    

My patch looks like this

::
    
    From eab0f0e9fc24c1915d2767a87a8f089f6d820955 Mon Sep 17 00:00:00 2001
    From: William Brown <firstyear at redhat.com>
    Date: Tue, 8 Dec 2015 13:52:29 +1000
    Subject: [PATCH] Ticket 48372 - ASAN invalid write in dblayer.c
    
    Bug Description:  During server start up we attempt to write 513 bytes to a
    buffer that is only 512 bytes long.
    
    Fix Description:  Increase the size of the buffer that sscanf writes into.
    
    https://fedorahosted.org/389/ticket/48372
    
    Author: wibrown
    
    Review by: ???
    ---
     ldap/servers/slapd/back-ldbm/dblayer.c | 4 ++--
     1 file changed, 2 insertions(+), 2 deletions(-)
    
    diff --git a/ldap/servers/slapd/back-ldbm/dblayer.c b/ldap/servers/slapd/back-ldbm/dblayer.c
    index 33506f4..9168c8c 100644
    --- a/ldap/servers/slapd/back-ldbm/dblayer.c
    +++ b/ldap/servers/slapd/back-ldbm/dblayer.c
    @@ -5191,8 +5191,8 @@ static int read_metadata(struct ldbminfo *li)
         PRFileInfo64 prfinfo;
         int return_value = 0;
         PRInt32 byte_count = 0;
    -    char attribute[512];
    -    char value[128], delimiter;
    +    char attribute[513];
    +    char value[129], delimiter;
         int number = 0;
         dblayer_private *priv = (dblayer_private *)li->li_dblayer_private;
     
    -- 
    2.5.0
    
    

One more bug fixed! Lets get it commited. If you don't have a FAS account, please email the git format-patch output to 389-devel@lists.fedoraproject.org else, raise a ticket on https://fedorahosted.org/389



43
