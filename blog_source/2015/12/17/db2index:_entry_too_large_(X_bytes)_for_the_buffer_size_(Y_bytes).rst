db2index: entry too large (X bytes) for the buffer size (Y bytes)
=================================================================
We've been there: You need to reindex your dirsrv and get it back into production as fast as you can. Then all of a sudden you get this error.

Some quick research shows no way to change the mystical buffer size being referenced. You pull out your hair and wonder what's going on, so you play with some numbers, and eventually it works, but you don't know why.

It turns out, this is one of the more magical undocumented values that DS sets for itself. If we look through the code, we find that this buffer is derived from the ldbm instances c_maxsize. 

::
    
     ./ldap/servers/slapd/back-ldbm/import.c:48: 
    
    job->fifo.bsize = (inst->inst_cache.c_maxsize/10) << 3;
    

That c_maxsize is actually the value of cn=config,cn=ldbm database,cn=plugins,cn=config, nsslapd-dbcachesize.

So, say that we get the error bytes is too small as it's only (20000000 bytes) in size. We plug this in:

::
    
    (20000000 >> 3) * 10 = 25000000
    

Which in my case was the size of nsslapd-dbcachesize

If we have a hypothetical value, say 28000000 bytes, and db2index can't run, you can use this reverse to calculate the dbcachesize you need:

::
    
    (28000000 >> 3) * 10 = 35000000
    

This will create a buffersize of 28000000 so you can run the db2index task.

In the future, this value will be configurable, rather than derived which will improve the clarity of the error, and the remediation. 
