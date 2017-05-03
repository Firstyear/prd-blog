Securing RHEL - CentOS - Fedora
===============================
We've had a prompting to investigate our OS security at my work. As a result, I've been given a pretty open mandate to investigate and deliver some simple changes that help lock down our systems and make measurable changes to security and incident analysis.

First, I used some common sense. Second, I did my research. Third, I used tools to help look at things that I would otherwise have missed.

The best tool I used was certainly OpenSCAP. Very simple to use, and gives some really basic recommendations that just make sense. Some of it's answers I took with a grain of salt. For example, account lockout modules in pam aren't needed, as we handle this via our directory services. But it can highlight areas you may have missed.

To run a scap scan:

::
    
    yum install scap-security-guide openscap openscap-scanner
    FEDORA
    oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_common --results /tmp/`hostname`-ssg-results.xml \
    --report /tmp/`hostname`-ssg-results.html /usr/share/xml/scap/ssg/content/ssg-fedora-ds.xml
    RHEL / CENTOS
    oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_common --results /tmp/`hostname`-ssg-results.xml \
    --report /tmp/`hostname`-ssg-results.html /usr/share/xml/scap/ssg/content/ssg-rhel7-ds.xml
    

Then view the output in a web browser.

Here is what I came up with.

-- Partitioning --
------------------

Sadly, you need to reinstall for these, but worth rolling out for "future builds". Here is my partition section from ks.conf. Especially important is putting audit on its own partition.

::
    
    # Partition clearing information                                                                                
    bootloader --location=mbr                                                                                       
    clearpart --initlabel --all                                                                                     
    # Disk partitioning information                                                                                 
    part /boot --fstype=ext4 --size=512 --asprimary --fsoptions=x-systemd.automount,nodev,nosuid,defaults
    # LVM                                                                                                           
    part pv.2 --size=16384 --grow --asprimary                                                                       
    volgroup vg00 pv.2                                                                                              
    logvol swap --fstype=swap --size=2048 --name=swap_lv --vgname=vg00               
    logvol / --fstype=xfs --size=512 --name=root_lv --vgname=vg00 --fsoptions=defaults
    logvol /usr --fstype=xfs --size=3072 --name=usr_lv --vgname=vg00 --fsoptions=nodev,defaults
    logvol /home --fstype="xfs" --size=512 --name=home_lv --vgname=vg00 --fsoptions=nodev,nosuid,defaults
    logvol /var  --fstype=xfs --size=3072 --name=var_lv --vgname=vg00 --fsoptions=nodev,nosuid,noexec,defaults
    logvol /var/log --fstype="xfs" --size=1536 --name=var_log_lv --vgname=vg00 --fsoptions=nodev,nosuid,noexec,defaults
    logvol /var/log/audit --fstype="xfs" --size=512 --name=var_log_audit_lv --vgname=vg00 --fsoptions=nodev,nosuid,noexec,defaults
    logvol /srv --fstype="xfs" --size=512 --name=srv_lv --vgname=vg00 --fsoptions=nodev,nosuid,defaults
    logvol /opt --fstype="xfs" --size=512 --name=opt_lv --vgname=vg00 --fsoptions=nodev,nosuid,defaults
    

With /tmp, if you mount this, and run redhat satellite, you need to be careful. Satellite expects to be able to execute out of /tmp, so don't set noexec on that partition!

-- SSH keys --
--------------

It's just good practice to use these. It saves typing in a password to a prompt which helps to limit credential exposure. We are enabling LDAP backed SSH keys now to make this easier in our workplace.

-- SELinux --
-------------

SELinux isn't perfect by any means, but it helps a lot. It can make the work of an attacker more complex, and it can help prevent data leakage via the network. Consider that by default httpd_t cannot make outgoing network connections. This is awesome to prevent data being leaked back to attackers. Well worth the time to setup these policies correctly.

If you have to set permissive to make an application work, do it on a per-domain basis with:

::
    
    semanage permissive -a httpd_t
    

This way the protections on all other processes are not removed.


On some of my systems I even run confined staff users to help prevent mistakes / malware from users. I manage this via FreeIPA.

-- Auditing --
--------------

This allows us to see who / what is altering things on our system. We extended the core auditing rules to include a few extras.

/etc/audit/rules.d/audit.rules

::
    
    # This file contains the auditctl rules that are loaded
    # whenever the audit daemon is started via the initscripts.
    # The rules are simply the parameters that would be passed
    # to auditctl.
    
    # First rule - delete all
    -D
    
    # Increase the buffers to survive stress events.
    # Make this bigger for busy systems
    -b 8192
    
    #
    # Feel free to add below this line. See auditctl man page
    -w /etc/ -p wa -k etc_modification
    
    # Detect login log tampering
    -w /var/log/faillog -p wa -k logins
    -w /var/log/lastlog -p wa -k logins
    -w /var/run/utmp -p wa -k session
    -w /var/log/btmp -p wa -k session
    -w /var/log/wtmp -p wa -k session
    
    # audit_time_rules
    ## REMOVE STIME ON RHEL
    #-a always,exit -F arch=b32 -S stime -S adjtimex -S settimeofday -S clock_settime -k audit_time_rules
    #-a always,exit -F arch=b64 -S stime -S adjtimex -S settimeofday -S clock_settime -k audit_time_rules
    
    # audit_rules_networkconfig_modification
    -a always,exit -F arch=b32 -S sethostname -S setdomainname -k audit_rules_networkconfig_modification
    -a always,exit -F arch=b64 -S sethostname -S setdomainname -k audit_rules_networkconfig_modification
    
    # Audit kernel module manipulation
    -a always,exit -F arch=b32 -S init_module -S delete_module -k modules
    -a always,exit -F arch=b64 -S init_module -S delete_module -k modules
    
    ################################################################################
    # These are super paranoid rules at this point. Only use if you are willing to take
    # a 3% to 10% perf degredation.
    
    # Perhaps remove the uid limits on some of these actions? We often get attacked via services, not users. These rules are more for workstations...
    
    #-a always,exit -F arch=b32 -S chmod -S chown -S fchmod -S fchmodat -S fchown -S fchownat -S fremovexattr -S fsetxattr -S lchown -S lremovexattr -S lsetxattr -S removexattr -S setxattr -F auid>=500 -F auid!=4294967295 -k perm_mod
    #-a always,exit -F arch=b32 -S creat -S open -S openat -S open_by_handle_at -S truncate -S ftruncate -F exit=-EACCES -F auid>=500 -F auid!=4294967295 -k access
    #-a always,exit -F arch=b32 -S creat -S open -S openat -S open_by_handle_at -S truncate -S ftruncate -F exit=-EPERM -F auid>=500 -F auid!=4294967295 -k access
    #-a always,exit -F arch=b32 -S rmdir -S unlink -S unlinkat -S rename -S renameat -F auid>=500 -F auid!=4294967295 -k delete
    # This rule is more useful on a workstation with automount ...
    #-a always,exit -F arch=b32 -S mount -F auid>=500 -F auid!=4294967295 -k export
    
    #-a always,exit -F arch=b64 -S chmod -S chown -S fchmod -S fchmodat -S fchown -S fchownat -S fremovexattr -S fsetxattr -S lchown -S lremovexattr -S lsetxattr -S removexattr -S setxattr -F auid>=500 -F auid!=4294967295 -k perm_mod
    #-a always,exit -F arch=b64 -S creat -S open -S openat -S open_by_handle_at -S truncate -S ftruncate -F exit=-EACCES -F auid>=500 -F auid!=4294967295 -k access
    #-a always,exit -F arch=b64 -S creat -S open -S openat -S open_by_handle_at -S truncate -S ftruncate -F exit=-EPERM -F auid>=500 -F auid!=4294967295 -k access
    #-a always,exit -F arch=b64 -S rmdir -S unlink -S unlinkat -S rename -S renameat -F auid>=500 -F auid!=4294967295 -k delete
    # This rule is more useful on a workstation with automount ...
    #-a always,exit -F arch=b64 -S mount -F auid>=500 -F auid!=4294967295 -k export
    
    # This setting means you need a reboot to changed audit rules.
    #  probably worth doing .... 
    #-e 2
    
    

To handle all the extra events I increased my audit logging sizes

/etc/audit/auditd.conf
::
    
    log_file = /var/log/audit/audit.log                                                                             
    log_format = RAW                                                                                                
    log_group = root                                                                                                
    priority_boost = 4                                                                                              
    flush = INCREMENTAL                                                                                             
    freq = 20                                                                                                       
    num_logs = 5                                                                                                    
    disp_qos = lossy                                                                                                
    dispatcher = /sbin/audispd                                                                                      
    name_format = NONE                                                                                              
    max_log_file = 20                                                                  
    max_log_file_action = ROTATE                                                                                    
    space_left = 100                                                                                                
    space_left_action = EMAIL                                                                                       
    action_mail_acct = root                                                                                         
    admin_space_left = 75                                                                                           
    admin_space_left_action = SUSPEND                                                                               
    admin_space_left_action = email                                                                                 
    disk_full_action = SUSPEND                                                                                      
    disk_error_action = SUSPEND                                                                                     
    tcp_listen_queue = 5                                                                                            
    tcp_max_per_addr = 1                                                                                            
    tcp_client_max_idle = 0                                                                                         
    enable_krb5 = no                                                                                                
    krb5_principal = auditd  
    

-- PAM and null passwords --
----------------------------

Scap noticed that the default config of password-auth-ac contained nullok on some lines. Remove this:

::
    
    BEFORE
    auth        sufficient    pam_unix.so nullok try_first_pass
    AFTER
    auth        sufficient    pam_unix.so try_first_pass
    

-- Firewall (Backups, SMH, NRPE) --
-----------------------------------

Backup clients (Amanda, netbackup, commvault) tend to have very high privilege, no SELinux, and are security swiss cheese. Similar is true for vendor systems like HP system management homepage, and NRPE (nagios). It's well worth locking these down. Before we had blanket "port open" rules, now these are tighter.

In iptables, you should use the "-s" to specify a source range these are allowed to connect from. The smaller the range, the better.

In firewalld, you need to use the rich language. Which is a bit more verbose, and finicky than iptables. My rules end up as:
::
    
    rule family="ipv4" source address="10.0.0.0/24" port port="2381" protocol="tcp" accept
    

For example. Use the firewalld-cmd with the --add-rich-rule, or use ansibles rich_rule options.

-- AIDE (HIDS) --
-----------------

Aide is a fantastic and simple file integrity checker. I have an ansible role that I can tack onto the end of all my playbooks to automatically update the AIDE database so that it stays consistent with changes, but will allow us to see out of band changes. 

The default AIDE config often picks up files that change frequently. I have an aide.conf that still provides function, but without triggering false alarms. I include aide-local.conf so that other teams / staff can add application specific aide monitoring that doesn't conflict with my work. 

::
    
    # Example configuration file for AIDE.
    
    @@define DBDIR /var/lib/aide
    @@define LOGDIR /var/log/aide
    
    # The location of the database to be read.
    database=file:@@{DBDIR}/aide.db.gz
    
    # The location of the database to be written.
    #database_out=sql:host:port:database:login_name:passwd:table
    #database_out=file:aide.db.new
    database_out=file:@@{DBDIR}/aide.db.new.gz
    
    # Whether to gzip the output to database
    gzip_dbout=yes
    
    # Default.
    verbose=5
    
    #report_url=file:@@{LOGDIR}/aide.log
    report_url=stdout
    #report_url=stderr
    #NOT IMPLEMENTED report_url=mailto:root@foo.com
    report_url=syslog:LOG_AUTH
    
    # These are the default rules.
    #
    #p:      permissions
    #i:      inode:
    #n:      number of links
    #u:      user
    #g:      group
    #s:      size
    #b:      block count
    #m:      mtime
    #a:      atime
    #c:      ctime
    #S:      check for growing size
    #acl:           Access Control Lists
    #selinux        SELinux security context
    #xattrs:        Extended file attributes
    #md5:    md5 checksum
    #sha1:   sha1 checksum
    #sha256:        sha256 checksum
    #sha512:        sha512 checksum
    #rmd160: rmd160 checksum
    #tiger:  tiger checksum
    
    #haval:  haval checksum (MHASH only)
    #gost:   gost checksum (MHASH only)
    #crc32:  crc32 checksum (MHASH only)
    #whirlpool:     whirlpool checksum (MHASH only)
    
    FIPSR = p+i+n+u+g+s+m+c+acl+selinux+xattrs+sha256
    
    # Fips without time because of some database/sqlite issues
    FIPSRMT = p+i+n+u+g+s+acl+selinux+xattrs+sha256
    
    #R:             p+i+n+u+g+s+m+c+acl+selinux+xattrs+md5
    #L:             p+i+n+u+g+acl+selinux+xattrs
    #E:             Empty group
    #>:             Growing logfile p+u+g+i+n+S+acl+selinux+xattrs
    
    # You can create custom rules like this.
    # With MHASH...
    # ALLXTRAHASHES = sha1+rmd160+sha256+sha512+whirlpool+tiger+haval+gost+crc32
    ALLXTRAHASHES = sha1+rmd160+sha256+sha512+tiger
    # Everything but access time (Ie. all changes)
    EVERYTHING = R+ALLXTRAHASHES
    
    # Sane, with multiple hashes
    # NORMAL = R+rmd160+sha256+whirlpool
    NORMAL = FIPSR+sha512
    
    # For directories, don't bother doing hashes
    DIR = p+i+n+u+g+acl+selinux+xattrs
    
    # Access control only
    PERMS = p+i+u+g+acl+selinux+xattrs
    
    # Logfile are special, in that they often change
    LOG = >
    
    # Just do sha256 and sha512 hashes
    LSPP = FIPSR+sha512
    LSPPMT = FIPSRMT+sha512
    
    # Some files get updated automatically, so the inode/ctime/mtime change
    # but we want to know when the data inside them changes
    DATAONLY =  p+n+u+g+s+acl+selinux+xattrs+sha256
    
    # Next decide what directories/files you want in the database.
    
    /boot   NORMAL
    /bin    NORMAL
    /sbin   NORMAL
    /usr/bin NORMAL
    /usr/sbin NORMAL
    /lib    NORMAL
    /lib64  NORMAL
    # These may be too variable
    /opt    NORMAL
    /srv    NORMAL
    # These are too volatile
    # We can check USR if we want, but it doesn't net us much.
    #/usr    NORMAL
    !/usr/src
    !/usr/tmp
    
    # Check only permissions, inode, user and group for /etc, but
    # cover some important files closely.
    /etc    PERMS
    !/etc/mtab
    # Ignore backup files
    !/etc/.*~
    /etc/exports  NORMAL
    /etc/fstab    NORMAL
    /etc/passwd   NORMAL
    /etc/group    NORMAL
    /etc/gshadow  NORMAL
    /etc/shadow   NORMAL
    /etc/security/opasswd   NORMAL
    
    /etc/hosts.allow   NORMAL
    /etc/hosts.deny    NORMAL
    
    /etc/sudoers NORMAL
    /etc/sudoers.d NORMAL
    /etc/skel NORMAL
    
    /etc/logrotate.d NORMAL
    
    /etc/resolv.conf DATAONLY
    
    /etc/nscd.conf NORMAL
    /etc/securetty NORMAL
    
    # Shell/X starting files
    /etc/profile NORMAL
    /etc/bashrc NORMAL
    /etc/bash_completion.d/ NORMAL
    /etc/login.defs NORMAL
    /etc/zprofile NORMAL
    /etc/zshrc NORMAL
    /etc/zlogin NORMAL
    /etc/zlogout NORMAL
    /etc/profile.d/ NORMAL
    /etc/X11/ NORMAL
    
    # Pkg manager
    /etc/yum.conf NORMAL
    /etc/yumex.conf NORMAL
    /etc/yumex.profiles.conf NORMAL
    /etc/yum/ NORMAL
    /etc/yum.repos.d/ NORMAL
    
    # Ignore lvm files that change regularly
    !/etc/lvm/archive
    !/etc/lvm/backup
    !/etc/lvm/cache
    
    # Don't scan log by default, because not everything is a "growing log file".
    !/var/log   LOG
    !/var/run/utmp LOG
    
    # This gets new/removes-old filenames daily
    !/var/log/sa
    # As we are checking it, we've truncated yesterdays size to zero.
    !/var/log/aide.log
    !/var/log/journal
    
    # LSPP rules...
    # AIDE produces an audit record, so this becomes perpetual motion.
    # /var/log/audit/ LSPP
    /etc/audit/ LSPP
    /etc/audisp/ LSPP
    /etc/libaudit.conf LSPP
    /usr/sbin/stunnel LSPP
    /var/spool/at LSPP
    /etc/at.allow LSPP
    /etc/at.deny LSPP
    /etc/cron.allow LSPP
    /etc/cron.deny LSPP
    /etc/cron.d/ LSPP
    /etc/cron.daily/ LSPP
    /etc/cron.hourly/ LSPP
    /etc/cron.monthly/ LSPP
    /etc/cron.weekly/ LSPP
    /etc/crontab LSPP
    /var/spool/cron/root LSPP
    
    /etc/login.defs LSPP
    /etc/securetty LSPP
    /var/log/faillog LSPP
    /var/log/lastlog LSPP
    
    /etc/hosts LSPP
    /etc/sysconfig LSPP
    
    /etc/inittab LSPP
    #/etc/grub/ LSPP
    /etc/rc.d LSPP
    
    /etc/ld.so.conf LSPP
    
    /etc/localtime LSPP
    
    /etc/sysctl.conf LSPP
    
    /etc/modprobe.conf LSPP
    
    /etc/pam.d LSPP
    /etc/security LSPP
    /etc/aliases LSPP
    /etc/postfix LSPP
    
    /etc/ssh/sshd_config LSPP
    /etc/ssh/ssh_config LSPP
    
    /etc/stunnel LSPP
    
    /etc/vsftpd.ftpusers LSPP
    /etc/vsftpd LSPP
    
    /etc/issue LSPP
    /etc/issue.net LSPP
    
    /etc/cups LSPP
    
    # Check our key stores for tampering.
    /etc/pki LSPPMT
    !/etc/pki/nssdb/
    /etc/pki/nssdb/cert8.db LSPP
    /etc/pki/nssdb/cert9.db LSPP
    /etc/pki/nssdb/key3.db LSPP
    /etc/pki/nssdb/key4.db LSPP
    /etc/pki/nssdb/pkcs11.txt LSPP
    /etc/pki/nssdb/secmod.db LSPP
    
    # Check ldap and auth configurations.
    /etc/openldap LSPP
    /etc/sssd LSPP
    
    # Ignore the prelink cache as it changes.
    !/etc/prelink.cache
    
    # With AIDE's default verbosity level of 5, these would give lots of
    # warnings upon tree traversal. It might change with future version.
    #
    #=/lost\+found    DIR
    #=/home           DIR
    
    # Ditto /var/log/sa reason...
    !/var/log/and-httpd
    
    #/root   NORMAL
    # Admins dot files constantly change, just check PERMS
    #/root/\..* PERMS
    # Check root sensitive files
    /root/.ssh/ NORMAL
    /root/.bash_profile NORMAL
    /root/.bashrc NORMAL
    /root/.cshrc NORMAL
    /root/.tcshrc NORMAL
    /root/.zshrc NORMAL
    
    
    @@include /etc/aide-local.conf
    
    

-- Time --
----------

Make sure you run an NTP client. I'm a fan of chrony these days, as it's syncs quickly and reliably.

-- Collect core dumps and abrt --
---------------------------------

Install and run kdump and abrtd so you can analyse why something crashed, to determine if it was malicious or not.

::
    
    yum install kexec-tools abrt abrt-cli
    systemctl enable abrtd
    

At the same time, you need to alter kdump.conf to dump correctly

::
    
    xfs /dev/os_vg/var_lv                                                            
    path /crash                                                                      
    core_collector makedumpfile -l --message-level 7 -d 23,31                        
    default reboot   
    

Finally, append crashkernel=auto to your grub commandline.

-- Sysctl --
------------

These are an evolved set of sysctls and improvements to our base install that help tune some basic network and other areas to strengthen the network stack and base OS.

::
    
    # Ensure ASLR
    kernel.randomize_va_space = 2
    # limit access to dmesg
    ## does this affect ansible facts
    kernel.dmesg_restrict = 1
    
    # Prevent suid binaries core dumping. Helps to prevent memory / data leaks
    fs.suid_dumpable = 0
    
    # https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt
    # Controls IP packet forwarding
    net.ipv4.ip_forward = 0
    
    # Controls source route verification
    net.ipv4.conf.default.rp_filter = 1
    
    # Do not accept source routing
    net.ipv4.conf.default.accept_source_route = 0
    
    # Controls the System Request debugging functionality of the kernel
    kernel.sysrq = 0
    
    # Controls whether core dumps will append the PID to the core filename.
    # Useful for debugging multi-threaded applications.
    kernel.core_uses_pid = 1
    # Decrease the time default value for tcp_fin_timeout connection
    net.ipv4.tcp_fin_timeout = 35
    # Decrease the time default value for tcp_keepalive_time connection
    net.ipv4.tcp_keepalive_time = 600
    # Provide more ports and timewait buckets to increase connectivity
    net.ipv4.ip_local_port_range = 8192 61000
    net.ipv4.tcp_max_tw_buckets = 1000000
    
    ## Network Hardening ##
    net.ipv4.tcp_max_syn_backlog = 4096
    net.ipv4.conf.all.accept_redirects = 0
    net.ipv4.conf.all.secure_redirects = 0
    net.ipv4.conf.default.accept_redirects = 0
    net.ipv4.conf.default.secure_redirects = 0
    net.ipv4.icmp_echo_ignore_broadcasts = 1
    net.ipv4.conf.all.send_redirects = 0
    net.ipv4.conf.default.send_redirects = 0
    net.ipv4.icmp_ignore_bogus_error_responses = 1
    
    net.nf_conntrack_max = 262144
    
