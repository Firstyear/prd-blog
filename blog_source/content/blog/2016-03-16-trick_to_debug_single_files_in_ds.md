+++
title = "Trick to debug single files in ds"
date = 2016-03-16
slug = "2016-03-16-trick_to_debug_single_files_in_ds"
# This is relative to the root!
aliases = [ "2016/03/16/trick_to_debug_single_files_in_ds.html", "blog/html/2016/03/16/trick_to_debug_single_files_in_ds.html" ]
+++
# Trick to debug single files in ds

I\'ve been debugging thread deadlocks in directory server. When you turn
on detailed tracing with

    ns-slapd -d 1

You slow the server down so much that you can barely function.

A trick is that defines in the local .c file, override from the .h. Copy
paste this to the file you want to debug. This allows the logs from this
file to be emitted at -d 0, but without turning it on everywhere, so you
don\'t grind the server to a halt.

    /* Do this so we can get the messages at standard log levels. */
    #define SLAPI_LOG_FATAL         0
    #define SLAPI_LOG_TRACE         0
    #define SLAPI_LOG_PACKETS       0
    #define SLAPI_LOG_ARGS          0
    #define SLAPI_LOG_CONNS         0
    #define SLAPI_LOG_BER           0
    #define SLAPI_LOG_FILTER        0
    #define SLAPI_LOG_CONFIG        0
    #define SLAPI_LOG_ACL           0
    #define SLAPI_LOG_SHELL         0
    #define SLAPI_LOG_PARSE         0
    #define SLAPI_LOG_HOUSE         0
    #define SLAPI_LOG_REPL          0
    #define SLAPI_LOG_CACHE         0
    #define SLAPI_LOG_PLUGIN        0
    #define SLAPI_LOG_TIMING        0
    #define SLAPI_LOG_BACKLDBM      0
    #define SLAPI_LOG_ACLSUMMARY    0

