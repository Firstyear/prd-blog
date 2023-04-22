Work around docker exec bug
===========================

There is currently a docker exec bug in Centos/RHEL 7 that causes errors such as:

::

    # docker exec -i -t instance /bin/sh
    rpc error: code = 2 desc = oci runtime error: exec failed: container_linux.go:247: starting container process caused "process_linux.go:110: decoding init error from pipe caused \"read parent: connection reset by peer\""


As a work around you can use nsenter instead:

::

    PID=docker inspect --format {{.State.Pid}} <name of container>
    nsenter --target $PID --mount --uts --ipc --net --pid /bin/sh

For more information, you can see the `bugreport here. <https://bugzilla.redhat.com/show_bug.cgi?id=1655214>`_



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
