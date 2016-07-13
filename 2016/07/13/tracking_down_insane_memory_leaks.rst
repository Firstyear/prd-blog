tracking down insane memory leaks
=================================

One of the best parts of AddressSanitizer is the built in leak sanitiser. However, sometimes it's not as clear as you might wish!

::

    I0> /opt/dirsrv/bin/pwdhash hello                            
    {SSHA}s16epVgkKenDHQqG8hrCGhmzqkgx0H1984ttYg==

    =================================================================
    ==388==ERROR: LeakSanitizer: detected memory leaks

    Direct leak of 72 byte(s) in 1 object(s) allocated from:
        #0 0x7f5f5f94dfd0 in calloc (/lib64/libasan.so.3+0xc6fd0)
        #1 0x7f5f5d7f72ae  (/lib64/libnss3.so+0x752ae)

    SUMMARY: AddressSanitizer: 72 byte(s) leaked in 1 allocation(s).


"Where is /lib64/libnss3.so+0x752ae" and what can I do with it? I have debuginfo and devel info installed, but I can't seem to see what line that's at.

So we run the llvm symboliser manually over the output, and we get:

::

    =================================================================
    ==391==ERROR: LeakSanitizer: detected memory leaks

    Direct leak of 72 byte(s) in 1 object(s) allocated from:
        #0 0x7f65b8d3dfd0 in calloc (/lib64/libasan.so.3+0xc6fd0)
        #0 0x7f65b6be72ae in ?? error.c:109:0

    SUMMARY: AddressSanitizer: 72 byte(s) leaked in 1 allocation(s).

So we don't know *where* it's happening, except that it's in error.c *somewhere* in libnss3.so.

Lets take a look at an nss checkout then.

::

    nss I0> find . -name error.c  
    ./lib/base/error.c

Low and behold, line 109

::

        new_bytes = (new_size * sizeof(PRInt32)) + sizeof(error_stack);
        /* Use NSPR's calloc/realloc, not NSS's, to avoid loops! */
        new_stack = PR_Calloc(1, new_bytes);

        if ((error_stack *)NULL != new_stack) {
            if ((error_stack *)NULL != rv) {
                (void)nsslibc_memcpy(new_stack, rv, rv->header.space);

Looks like our Calloc! From here, we just need to work out what's calling error_get_my_stack, and progress. Gdb can easily insert break points to find the caller and trace.

So even if you don't think you have all the information, you can always progress on issues with some more investigation. Don't be afraid to read!


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
