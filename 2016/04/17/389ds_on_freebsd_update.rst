389ds on freebsd update
=======================

A few months ago I posted an how to build 389-ds for freebsd. This was to start my porting effort.

I have now finished the port. There are still issues that the perl setup-ds.pl installer does not work, but this will be resolved soon in other ways.

For now here are the steps for 389-ds on freebsd. You may need to wait for a few days for the relevant patches to be in git.

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
    gmake
    python34

You will need to use pip for these python dependencies.

::

    sudo python3.4 -m ensurepip
    sudo pip3.4 install six pyasn1 pyasn1-modules 

You will need to install svrcore.

::

    fetch http://www.port389.org/binaries/svrcore-4.1.1.tar.bz2
    tar -xvzf svrcore-4.1.1.tar.bz2
    cd svrcore-4.1.1
    CFLAGS="-fPIC "./configure --prefix=/opt/svrcore
    make
    sudo make install

You will need the following python tools checked out:

::

    git clone https://git.fedorahosted.org/git/389/lib389.git
    git clone https://github.com/pyldap/pyldap.git
    cd pyldap
    python3.4 setup.py build
    sudo python3.4 setup.py install

Now you can clone ds and try to build it:

::

    cd
    git clone https://git.fedorahosted.org/git/389/ds.git
    cd ds
    ./configure --prefix=/opt/dirsrv --with-openldap=/usr/local --with-db --with-db-inc=/usr/local/include/db5/ --with-db-lib=/usr/local/lib/db5/ --with-sasl --with-sasl-inc=/usr/local/include/sasl/ --with-sasl-lib=/usr/local/lib/sasl2/ --with-svrcore-inc=/opt/svrcore/include/ --with-svrcore-lib=/opt/svrcore/lib/ --with-netsnmp=/usr/local
    gmake
    sudo gmake install

Go back to the lib389 directory:

::

    sudo pw user add dirsrv
    sudo PYTHONPATH=`pwd` python3.4 lib389/clitools/ds_setup.py -f ~/setup-ds-admin.inf -v
    sudo chown -R dirsrv:dirsrv /opt/dirsrv/var/{run,lock,log,lib}/dirsrv
    sudo chmod 775 /opt/dirsrv/var
    sudo chmod 775 /opt/dirsrv/var/*
    sudo /opt/dirsrv/sbin/ns-slapd -d 0 -D /opt/dirsrv/etc/dirsrv/slapd-localhost

This is a really minimal setup routine right now. If it all worked, you can now run your instance. Here is my output belowe:

::

    INFO:lib389.tools:Running setup with verbose
    INFO:lib389.tools:Using inf from /home/william/setup-ds-admin.inf
    INFO:lib389.tools:Configuration ['general', 'slapd', 'rest', 'backend-userRoot']
    INFO:lib389.tools:Configuration general {'selinux': False, 'full_machine_name': 'localhost.localdomain', 'config_version': 2, 'strict_host_checking': True}
    INFO:lib389.tools:Configuration slapd {'secure_port': 636, 'root_password': 'password', 'port': 389, 'cert_dir': '/opt/dirsrv/etc/dirsrv/slapd-localhost/', 'lock_dir': '/opt/dirsrv/var/lock/dirsrv/slapd-localhost', 'ldif_dir': '/opt/dirsrv/var/lib/dirsrv/slapd-localhost/ldif', 'backup_dir': '/opt/dirsrv/var/lib/dirsrv/slapd-localhost/bak', 'prefix': '/opt/dirsrv', 'instance_name': 'localhost', 'bin_dir': '/opt/dirsrv/bin/', 'data_dir': '/opt/dirsrv/share/', 'local_state_dir': '/opt/dirsrv/var', 'run_dir': '/opt/dirsrv/var/run/dirsrv', 'schema_dir': '/opt/dirsrv/etc/dirsrv/slapd-localhost/schema', 'config_dir': '/opt/dirsrv/etc/dirsrv/slapd-localhost/', 'root_dn': 'cn=Directory Manager', 'log_dir': '/opt/dirsrv/var/log/dirsrv/slapd-localhost', 'tmp_dir': '/tmp', 'user': 'dirsrv', 'group': 'dirsrv', 'db_dir': '/opt/dirsrv/var/lib/dirsrv/slapd-localhost/db', 'sbin_dir': '/opt/dirsrv/sbin', 'sysconf_dir': '/opt/dirsrv/etc', 'defaults': '1.3.5'}
    INFO:lib389.tools:Configuration backends [{'name': 'userRoot', 'sample_entries': True, 'suffix': 'dc=example,dc=com'}]
    INFO:lib389.tools:PASSED: user / group checking
    INFO:lib389.tools:PASSED: Hostname strict checking
    INFO:lib389.tools:PASSED: prefix checking
    INFO:lib389:dir (sys) : /opt/dirsrv/etc/sysconfig
    INFO:lib389.tools:PASSED: instance checking
    INFO:lib389.tools:PASSED: root user checking
    INFO:lib389.tools:PASSED: network avaliability checking
    INFO:lib389.tools:READY: beginning installation
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/var/lib/dirsrv/slapd-localhost/bak
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/etc/dirsrv/slapd-localhost/
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/etc/dirsrv/slapd-localhost/
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/var/lib/dirsrv/slapd-localhost/db
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/var/lib/dirsrv/slapd-localhost/ldif
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/var/lock/dirsrv/slapd-localhost
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/var/log/dirsrv/slapd-localhost
    INFO:lib389.tools:ACTION: creating /opt/dirsrv/var/run/dirsrv
    INFO:lib389.tools:ACTION: Creating certificate database is /opt/dirsrv/etc/dirsrv/slapd-localhost/
    INFO:lib389.tools:ACTION: Creating dse.ldif
    INFO:lib389.tools:FINISH: completed installation
    Sucessfully created instance

::

    [17/Apr/2016:14:44:21.030683607 +1000] could not open config file "/opt/dirsrv/etc/dirsrv/slapd-localhost//slapd-collations.conf" - absolute path?
    [17/Apr/2016:14:44:21.122087994 +1000] 389-Directory/1.3.5.1 B2016.108.412 starting up
    [17/Apr/2016:14:44:21.460033554 +1000] convert_pbe_des_to_aes:  Checking for DES passwords to convert to AES...
    [17/Apr/2016:14:44:21.461012440 +1000] convert_pbe_des_to_aes - No DES passwords found to convert.
    [17/Apr/2016:14:44:21.462712083 +1000] slapd started.  Listening on All Interfaces port 389 for LDAP requests

If we do an ldapsearch:

::

    fbsd-389-port# uname -r -s
    FreeBSD 10.2-RELEASE
    fbsd-389-port# ldapsearch -h localhost -b '' -s base -x +
    # extended LDIF
    #
    # LDAPv3
    # base <> with scope baseObject
    # filter: (objectclass=*)
    # requesting: + 
    #

    #
    dn:
    creatorsName: cn=server,cn=plugins,cn=config
    modifiersName: cn=server,cn=plugins,cn=config
    createTimestamp: 20160417044112Z
    modifyTimestamp: 20160417044112Z
    subschemaSubentry: cn=schema
    supportedExtension: 2.16.840.1.113730.3.5.7
    supportedExtension: 2.16.840.1.113730.3.5.8
    supportedExtension: 1.3.6.1.4.1.4203.1.11.3
    supportedExtension: 1.3.6.1.4.1.4203.1.11.1
    supportedControl: 2.16.840.1.113730.3.4.2
    supportedControl: 2.16.840.1.113730.3.4.3
    supportedControl: 2.16.840.1.113730.3.4.4
    supportedControl: 2.16.840.1.113730.3.4.5
    supportedControl: 1.2.840.113556.1.4.473
    supportedControl: 2.16.840.1.113730.3.4.9
    supportedControl: 2.16.840.1.113730.3.4.16
    supportedControl: 2.16.840.1.113730.3.4.15
    supportedControl: 2.16.840.1.113730.3.4.17
    supportedControl: 2.16.840.1.113730.3.4.19
    supportedControl: 1.3.6.1.1.13.1
    supportedControl: 1.3.6.1.1.13.2
    supportedControl: 1.3.6.1.4.1.42.2.27.8.5.1
    supportedControl: 1.3.6.1.4.1.42.2.27.9.5.2
    supportedControl: 1.2.840.113556.1.4.319
    supportedControl: 1.3.6.1.4.1.42.2.27.9.5.8
    supportedControl: 1.3.6.1.4.1.4203.666.5.16
    supportedControl: 2.16.840.1.113730.3.4.14
    supportedControl: 2.16.840.1.113730.3.4.20
    supportedControl: 1.3.6.1.4.1.1466.29539.12
    supportedControl: 2.16.840.1.113730.3.4.12
    supportedControl: 2.16.840.1.113730.3.4.18
    supportedFeatures: 1.3.6.1.4.1.4203.1.5.1
    supportedSASLMechanisms: EXTERNAL
    supportedLDAPVersion: 2
    supportedLDAPVersion: 3
    vendorName: 389 Project
    vendorVersion: 389-Directory/1.3.5.1 B2016.108.412


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
