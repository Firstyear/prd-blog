+++
title = "Fabric starting guide"
date = 2014-09-29
slug = "2014-09-29-Fabric_starting_guide"
# This is relative to the root!
aliases = [ "2014/09/29/Fabric_starting_guide.html" ]
+++
# Fabric starting guide

After the BB14 conf, I am posting some snippets of fabric tasks. Good
luck! Feel free to email me if you have questions.

    # Fabric snippets post BB14 conf

    # It should be obvious, but no warranty, expressed or otherwise is provided
    # with this code. Use at your own risk. Always read and understand code before
    # running it in your environment. Test test test.

    # William Brown, Geraint Draheim and others: University of Adelaide
    # william at adelaide.edu.au

    ####################################################################
    #### WARNING: THIS CODE MAY NOT RUN DUE TO LACK OF IMPORT, DEPENDENCIES.
    #### OR OTHER ENVIRONMENTAL CHANGES. THIS IS INTENTIONAL. YOU SHOULD
    #### ADAPT SOME OF THESE TO YOUR OWN ENVIRONMENT AND UNDERSTAND THE CODE
    ####################################################################

    ## Decorators. These provide wrappers to functions to allow you to enforce state
    # checks and warnings to users before they run. Here are some of the most useful
    # we have developed.


    def rnt_verbose(func):
        """
        When added to a function, this will add implementation of a global VERBOSE
        flag. The reason it's not a default, is because not every function is
        converted to use it yet. Just run command:verbose=1
        """
        @wraps(func)
        def inner(*args, **kwargs):
            if kwargs.pop("verbose", None) is not None:
                global VERBOSE
                VERBOSE = True
            return func(*args, **kwargs)
        return inner


    ## IMPORTANT NOTE: This decorator MUST be before @parallel
    def rnt_imsure(warning=None):
        """
        This is a useful decorator that enforces the user types a message into
        the console before the task will run. This is invaluable for high risk
        tasks, essentially forcing that the user MUST take responsibility for their
        actions.
        """
        def decorator(func):
            @wraps(func)
            def inner(*args, **kwargs):
                # pylint: disable=global-statement
                global IMSURE_WARNING
                print("Forcing task to run in serial")
                if kwargs.pop("imsure", None) is None and IMSURE_WARNING is False:
                    if warning is not None:
                        print(warning)
                    cont = getpass('If you are sure, type "I know what I am doing." #')
                    if cont == 'I know what I am doing.':
                        IMSURE_WARNING = True
                        print('continuing in 5 seconds ...')
                        time.sleep(5)
                        print("Starting ...")
                    else:
                        print('Exiting : No actions were taken')
                        sys.exit(1)
                return func(*args, **kwargs)
            inner.parallel = False
            inner.serial = True
            return inner
        return decorator

    def rnt_untested(func):
        """
        This decorator wraps functions that we consider new and untested. It gives
        a large, visual warning to the user that this is the case, and allows
        5 seconds for them to ctrl+c before continuing.
        """
        @wraps(func)
        def inner(*args, **kwargs):
            dragon = """
     ____________________________________
    / THIS IS AN UNTESTED TASK. THERE    \\
    \\ ARE DRAGONS IN THESE PARTS         /
     ------------------------------------
          \\                   / \\  //\\
           \\    |\\___/|      /   \\//  \\\\
                /0  0  \\__  /    //  | \\ \\
               /     /  \\/_/    //   |  \\  \\
               @_^_@'/   \\/_   //    |   \\   \\
               //_^_/     \\/_ //     |    \\    \\
            ( //) |        \\///      |     \\     \\
          ( / /) _|_ /   )  //       |      \\     _\\
        ( // /) '/,_ _ _/  ( ; -.    |    _ _\\.-~        .-~~~^-.
      (( / / )) ,-{        _      `-.|.-~-.           .~         `.
     (( // / ))  '/\\      /                 ~-. _ .-~      .-~^-.  \\
     (( /// ))      `.   {            }                   /      \\  \\
      (( / ))     .----~-.\\        \\-'                 .~         \\  `. \\^-.
                 ///.----..>        \\             _ -~             `.  ^-`  ^-_
                   ///-._ _ _ _ _ _ _}^ - - - - ~                     ~-- ,.-~
                                                                      /.-~
    """
            # pylint: disable=global-statement
            global DRAGON_WARNING
            if not DRAGON_WARNING:
                print(dragon)
                if kwargs.pop("dragon", None) is None:
                    time.sleep(5)
                print("RAWR: Your problem now!!!")
                DRAGON_WARNING = True
            return func(*args, **kwargs)
        return inner

    #################################################
    # Atomic locking functions. Provides a full lock, and a read lock. This is so 
    # that multiple systems, users etc can access servers, but the servers allow
    # one and only one action to be occuring.

    ATOMIC_LOCK = "/tmp/fsm_atomic.lock"
    ATOMIC_FLOCK = "/tmp/fsm_atomic.flock"
    ATOMIC_LOCK_HOSTS = {}
    LOCAL_HOSTNAME = socket.gethostname()

    class AtomicException(Exception):
        pass

    @task
    def lock():
        """
        usage: lock

        WARNING: DO NOT RUN THIS BY HAND UNLESS YOU KNOW WHAT YOU ARE DOING!!!

        Will create the atomic FSM lock. This prevents any other atomic function 
        from being able to run.
        """
        ### I cannot stress enough, do not change this. 
        result = run("""
            (
                flock -n 9 || exit 1
                touch {lock}
                echo {hostname} > {lock}
            ) 9>{flock}
        """.format(lock=ATOMIC_LOCK, flock=ATOMIC_FLOCK, hostname=LOCAL_HOSTNAME)  )
        if result.return_code == 0:
            return True
        return False

    @task
    def unlock():
        """
        usage: unlock

        WARNING: DO NOT RUN THIS BY HAND UNLESS YOU KNOW WHAT YOU ARE DOING!!!

        Will remove the atomic FSM lock. This allows any other atomic function 
        from to run.

        Only run this if you are sure that it needs to clean out a stale lock. The 
        fsm atomic wrapper is VERY GOOD at cleaning up after itself. Only a kill -9
        to the fabric job will prevent it removing the atomic lock. Check what 
        you are doing! Look inside of /tmp/fsm_atomic.lock to see who holds the lock right now! 
        """
        ### I cannot stress enough, do not change this. 
        result = run("""
                rm {lock}
            """.format(lock=ATOMIC_LOCK))
        if result == 0:
            return True
        return False

    def _lock_check():
        # pylint: disable=global-statement
        global ATOMIC_LOCK_HOSTS
        atomic_lock = False
        t_owner = False
        if ATOMIC_LOCK_HOSTS.has_key(env.host_string):
            atomic_lock = ATOMIC_LOCK_HOSTS[env.host_string]
            t_owner = True
        if not atomic_lock:
            with hide('warnings', 'running'):
                result = get(ATOMIC_LOCK, local_path="/tmp/{host}/{page}".format(
                    page="fsm_atomic.lock", host=env.host))
                if len(result) != 0:
                    atomic_lock = True
        return atomic_lock, t_owner

    def noop(*args, **kwargs):
        log_local('No-op for %s' % env.host_string, 'NOTICE')

    def rnt_fsm_atomic_r(func):
        """
        This decorator wraps functions that relate to the FSM and changing of state. 
        It triggers an atomic lock in the FSM to prevent other state changes occuring

        Fsm atomic tasks can be nested, only the top level task will manage the lock.

        If the lock is already taken, we will NOT allow the task to run.
        """
        @wraps(func)
        def inner(*args, **kwargs):
            #If ATOMIC_LOCK_HOSTS then we own the lock, so we can use it.
            # ELSE if we don't hold ATOMIC_LOCK_HOSTS we should check. 
            # Really, only the outer most wrapper should check .... 
            with settings(warn_only=True):
                # pylint: disable=global-statement
                global ATOMIC_LOCK_HOSTS
                #We DO care about the thread owner. Consider an exclusive lock above
                # a read lock. If we didn't check that we own that exclusive lock,
                # we wouldn't be able to run.
                (atomic_lock, t_owner) = _lock_check()
                allow_run = False
                if not atomic_lock or (atomic_lock and t_owner):
                    ### We can run
                    allow_run = True
                    pass
                elif atomic_lock and not t_owner:
                    ### We can't run. The lock is held, and we don't own it.
                    log_local('ATOMIC LOCK EXISTS, CANNOT RUN %s' % env.host_string, 'NOTICE')
                elif atomic_lock and t_owner:
                    #### THIS SHOULDN'T HAPPEN EVER
                    log_local('ATOMIC LOCK STATE IS INVALID PLEASE CHECK', 'CRITICAL')
                    raise AtomicException("CRITICAL: ATOIC LOCK STATE IS INVALID PLEASE CHECK, CANNOT RUN %s" % env.host_string)
                elif not atomic_lock and not t_owner:
                    ### This means there is no lock, and we don't own one. We can run.
                    pass
                try:
                    if allow_run:
                        return func(*args, **kwargs)
                    else:
                        return noop(*args, **kwargs)
                finally:
                    pass
        return inner


    def rnt_fsm_atomic_exc(func):
        """
        This decorator wraps functions that relate to the FSM and changing of state. 
        It triggers an atomic lock in the FSM to prevent other state changes occuring
        until the task is complete.

        Fsm atomic tasks can be nested, only the top level task will manage the lock.

        If the lock is already taken, we will NOT allow the task to run.

        State is passed to nested calls that also need an atomic lock.
        """
        @wraps(func)
        def inner(*args, **kwargs):
            with settings(warn_only=True):
                # pylint: disable=global-statement
                global ATOMIC_LOCK_HOSTS
                (atomic_lock, t_owner) = _lock_check()
                atomic_lock_owner = False
                allow_run = False
                if atomic_lock and t_owner:
                    #We have the lock, do nothing.
                    pass
                    allow_run = True
                elif atomic_lock and not t_owner:
                    #Someone else has it, error.
                    log_local('ATOMIC LOCK EXISTS, CANNOT RUN %s' % env.host_string, 'IMPORTANT')
                elif not atomic_lock and t_owner:
                    #Error, can't be in this state.
                    log_local('ATOMIC LOCK STATE IS INVALID PLEASE CHECK', 'CRITICAL')
                    raise AtomicException("CRITICAL: ATOMIC LOCK STATE IS INVALID PLEASE CHECK, CANNOT RUN %s" % env.host_string)
                elif not atomic_lock and not t_owner:
                    # Create the lock.
                    if not lock():
                        log_local('LOCK TAKEN BY ANOTHER PROCESS', 'IMPORTANT')
                        raise AtomicException("CRITICAL: LOCK TAKEN BY ANOTHER PROCESS")
                    ATOMIC_LOCK_HOSTS[env.host_string] = True
                    atomic_lock_owner = True
                    allow_run = True
                try:
                    if allow_run:
                        return func(*args, **kwargs)
                    else:
                        return noop(*args, **kwargs)
                finally:
                    if atomic_lock_owner:
                        unlock()
                        ATOMIC_LOCK_HOSTS[env.host_string] = False
        return inner

    ##################################################
    # Basic service management.
    #
    ## This is how you should start. Basic start, stop, and status commands.


    @task
    @parallel
    def start():
        """
        usage: start

        Start the MapleTA database, tomcat and webserver
        """
        sudo('service postgresql start')
        sudo('service tomcat6 start')
        sudo('service httpd start')


    @task
    @parallel
    def stop():
        """
        usage: stop

        Stop the MapleTA webserver, tomcat and database
        """
        sudo('service httpd stop')
        sudo('service tomcat6 stop')
        sudo('service postgresql stop')


    @task
    def restart():
        """
        usage: restart

        Restart the MapleTA database, tomcat and webserver
        """
        stop()
        start()


    @task
    def status():
        """
        usage: status

        Check the status of MapleTA
        """
        sudo('service postgresql status')
        sudo('service tomcat6 status')
        sudo('service httpd status')

    ##################################
    # Some blackboard tasks. These rely on some of the above decorators.
    #
    ### These are well developed, and sometimes rely on code not provided here. This
    # in very intentional so that you can read it and get ideas of HOW you should 
    # build code that works in your environment.

    # Also shows the usage of decorators and how you should use them to protent tasks

    ###################################
    # Helpers
    ###################################

    def config_key(key):
        if key.endswith('=') is False:
            key += '='
        return run("egrep '{key}' {bbconfig} | cut -f2 -d\= ".format(key=key, bbconfig=BB_CONFIG))

    # return blackboard database instance
    @task
    @rnt_help
    def get_db_instance():
        """
        usage: get_db_instance

        Display the servers current DB instance / SID
        """
        x = config_key('bbconfig.database.server.instancename')
        return x

    @task
    def get_db_credentials():
        """
        usage: get_db_credentials

        This will retrieve the DB username and password from the BB server, and 
        return them as a dict {hostname:X, sid:X, username:X, password:X}
        """
        creds = {'hostname' : None,
                 'sid' : None,
                 'username' : None,
                 'password' : None}
        with hide('everything'):
            creds['hostname'] = config_key('bbconfig.database.server.fullhostname')
            #TODO: Remove this sid appending line
            creds['sid'] = config_key('bbconfig.database.server.instancename') + '.blackboard.inc'
            creds['username'] = config_key('antargs.default.vi.db.name')
            creds['password'] = config_key('antargs.default.vi.db.password')
        return creds


    @task
    @parallel
    @rnt_fsm_atomic_exc
    def force_stop():
        """
        usage: force_stop -> atomic

        Stop blackboard services on hosts in PARALLEL. This WILL bring down all
        hosts FAST. This does NOT gracefully remove from the pool. This DOES NOT
        check the sis integration queue.
        """
        log_blackboard("Stopping BB", level='NOTICE')
        if test_processes(quit=False) is True:
            sudo('/data/blackboard/bbctl stop')
            time.sleep(30)
            cleanup_processes()
            test_processes()
        log_blackboard("Stopped", level='SUCCESS')

    @task
    @serial
    @rnt_fsm_atomic_exc
    def force_restart():
        """
        usage: restart -> atomic

        Restart blackboard systems in SERIAL. This is a dumb rolling restart. This
        DOES NOT remove from the pool and DOES NOT check the SIS queue
        """
        log_blackboard("Trying to force restart blackboard", level='NOTICE')
        force_stop()
        time.sleep(60)
        start()
        log_blackboard("force restart complete", level='SUCCESS')


    @task
    @rnt_imsure()
    def pushconfigupdates():
        """
        usage: pushconfigupdates

        Run the pushconfigupdates tool on a system.
    Warning! Running PushConfigUpdates.sh deploys changes to bb-config.properties!
    * This will result in an outage to the host(s) on which it is run!
    * Be careful that bb-config.properties, and the xythos.properties configuration
    files point to the correct database before you run this!
        """
        sudo('/data/blackboard/tools/admin/PushConfigUpdates.sh')

    @rnt_fsm_atomic_exc
    def _compress_and_delete(path, fileglob, zipage=7, rmage=3660):
        """
        This will compress logs up to 7 days, and delete older than 62 days.

        The pattern is taken as:

        /a/b*/c/d.*.txt

        This is passed to find which will carry out the actions as sudo.
        """
        with settings(warn_only=True):
            sudo("find {path} -mtime +{zipage} -name '{fileglob}'  -exec gzip '{{}}' \;".format(path=path, fileglob=fileglob, zipage=zipage))
            sudo("find {path} -mtime +{rmage} -name '{fileglob}.gz'  -exec rm '{{}}' \;".format(path=path, fileglob=fileglob, rmage=rmage))

    @task
    @rnt_help
    @rnt_fsm_atomic_exc
    def rotate_tomcat_logs():
        """
        usage: rotate_tomcat_logs -> atomic

        This will rotate the tomcat logs in /data/blackboard/logs/tomcat.
        """
        log_blackboard(level="NOTICE")
        with settings(warn_only=True):
            for pattern in ['stdout-stderr-*.log', 'bb-access-log.*.txt',
                    'activemq.txt.*.txt', 'catalina-log.txt.*.txt', 'gc.*.txt',
                    'thread_dump*.txt', '*.hprof' ]:
                _compress_and_delete("/data/blackboard/logs/tomcat/", pattern)
