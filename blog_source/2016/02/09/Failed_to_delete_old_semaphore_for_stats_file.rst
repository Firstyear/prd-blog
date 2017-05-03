Failed to delete old semaphore for stats file
=============================================
Today I was getting this error:

::
    
    [09/Feb/2016:12:21:26 +101800] - 389-Directory/1.3.5 B2016.040.145 starting up
    [09/Feb/2016:12:21:26 +101800] - Failed to delete old semaphore for stats file (/opt/dirsrv/var/run/dirsrv/slapd-localhost.stats). Error 13 (Permission denied).
    

But when you check:

::
    
    /opt# ls -al /opt/dirsrv/var/run/dirsrv/slapd-localhost.stats
    ls: cannot access /opt/dirsrv/var/run/dirsrv/slapd-localhost.stats: No such file or directory
    

Turns out on linux this isn't actually where the file is. You need to remove:

::
    
    /dev/shm/sem.slapd-localhost.stats
    

A bug will be opened shortly .... 
