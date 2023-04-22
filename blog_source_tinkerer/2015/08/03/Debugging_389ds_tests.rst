Debugging 389ds tests
=====================
I've always found when writing tests for 389ds that's it's really handy to have the ldif of data and the logs from a unit test available. However, by default, these are stored.

I discovered that if you add instance.backupFS() just before your instance.delete() you can keep a full dump of the data and logs from the instance. 

It can also be useful to call db2ldif before you run the backup so that you have a human readable copy of the data on hand as well. 

I've found the best pattern is:

::
    
        def tearDown(self):
            if self.instance.exists():
                self.instance.db2ldif(bename='userRoot', suffixes=[DEFAULT_SUFFIX], excludeSuffixes=[], encrypt=False, \
                    repl_data=False, outputfile='%s/ldif/%s.ldif' % (self.instance.dbdir,INSTANCE_SERVERID ))
                self.instance.clearBackupFS()
                self.instance.backupFS()
                self.instance.delete()
    
    

This puts an ldif dump of the DB into the backup path, we then clear old backups for our test instance (else it won't over-write them), finally, we actually do the backup. You should see:

::
    
    snip ...
    DEBUG:lib389:backupFS add = /var/lib/dirsrv/slapd-effectiverightsds/ldif/effectiverightsds.ldif (/)
    snip ...
    INFO:lib389:backupFS: archive done : /tmp/slapd-effectiverightsds.bck/backup_08032015_092510.tar.gz
    

Then you can extract this in /tmp/slapd-instance, and examine your logs and the ldif of what was really in your ldap server at the time. 

