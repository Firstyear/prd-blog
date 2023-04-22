+++
title = "The hidden log features of ns-slapd"
date = 2015-12-04
slug = "2015-12-04-The_hidden_log_features_of_ns-slapd"
# This is relative to the root!
aliases = [ "2015/12/04/The_hidden_log_features_of_ns-slapd.html" ]
+++
# The hidden log features of ns-slapd

This week I discovered (Or dug up: ns-slapd is old) that we have two
hidden logging features. In fact searching for one of them yields no
results, searching the other shows a document that says it\'s
undocumented.

This post hopes to rectify that.

In ns-slapd, during a normal operation you can see what a connected
client is searching in the access log, or what they are changing based
on the audit log.

If on a configuration for a plugin you need to diagnose these operations
you can\'t do this\... At least that\'s what the documentation tells
you.

You can enable logging for search operations on a plugin through the
value:

    nsslapd-logAccess: on

You can enabled logging for mod/modrdn/del/add operations on a plugin
through the value:

    nsslapd-logAudit: on

This will yield logs such as:

    time: 20151204143353
    dn: uid=test1,ou=People,dc=example,dc=com
    result: 0
    changetype: modify
    delete: memberOf
    -
    replace: modifiersname
    modifiersname: cn=MemberOf Plugin,cn=plugins,cn=config
    -
    replace: modifytimestamp
    modifytimestamp: 20151204043353Z
    -

    time: 20151204143353
    dn: cn=Test Managers,ou=Groups,dc=example,dc=com
    result: 0
    changetype: modify
    delete: member
    member: uid=test1,ou=People,dc=example,dc=com
    -
    replace: modifiersname
    modifiersname: cn=directory manager
    -
    replace: modifytimestamp
    modifytimestamp: 20151204043353Z
    -

Finally, a new option has been added that will enable both on all
plugins in the server.

    nsslapd-plugin-logging: on

All of these configurations are bound by and respect the following
settings:

    nsslapd-accesslog-logging-enabled
    nsslapd-auditlog-logging-enabled
    nsslapd-auditfaillog-logging-enabled
