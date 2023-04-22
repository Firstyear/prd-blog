+++
title = "Deploying sccache on SUSE"
date = 2020-11-19
slug = "2020-11-19-deploying_sccache_on_suse"
# This is relative to the root!
aliases = [ "2020/11/19/deploying_sccache_on_suse.html", "blog/html/2020/11/19/deploying_sccache_on_suse.html" ]
+++
# Deploying sccache on SUSE

sccache is a ccache/icecc-like tool from Mozilla, which in addition to
working with C and C++, is also able to help with Rust builds.

## Adding the Repo

A submission to Factory (tumbleweed) has been made, so check if you can
install from zypper:

    zypper install sccache

If not, sccache is still part of
[devel:tools:building](https://build.opensuse.org/package/show/devel:tools:building/sccache)
so you will need to add the repo to use sccache.

    zypper ar -f obs://devel:tools:building devel:tools:building
    zypper install sccache

It\'s also important you *do not* have ccache installed. ccache
intercepts the gcc command so you end up \"double caching\" potentially.

    zypper rm ccache

## Single Host

To use sccache on your host, you need to set the following environment
variables:

    export RUSTC_WRAPPER=sccache
    export CC="sccache /usr/bin/gcc"
    export CXX="sccache /usr/bin/g++"
    # Optional: This can improve rust caching
    # export CARGO_INCREMENTAL=false

This will allow sccache to wrap your compiler commands. You can show
your current sccache status with:

    sccache -s

There is more information about using cloud/remote storage for the cache
on the sccache [project
site](https://github.com/mozilla/sccache/blob/master/README.md)

## Distributed Compiliation

sccache is also capable of distributed compilation, where a number of
builder servers can compile items and return the artificats to your
machine. This can save you time by allowing compilation over a cluster,
using a faster remote builder, or just to keep your laptop cool.

Three components are needed to make this work. A scheduler that
coordinates the activities, one or more builders that provide their CPU,
and a client that submits compilation jobs.

The sccache package contains the required elements for all three parts.

Note that the client does *not* need to be the same version of SUSE or
even the same distro as the scheduler or builder. This is because the
client is able to bundle and submit it\'s toolchains to the workers on
the fly. Neat! sccache is capacble of also compiling for macos and
windows, but in these cases the toolchains can-not be submitted on the
fly and requires extra [work to
configure.](https://github.com/mozilla/sccache/blob/master/docs/DistributedQuickstart.md)

## Scheduler

The scheduler is configured with
[/etc/sccache/scheduler.conf]{.title-ref}. You need to define the
listening ip, client auth, and server (builder) auth methods. The
example configuration is well commented to help with this:

    # The socket address the scheduler will listen on. It's strongly recommended
    # to listen on localhost and put a HTTPS server in front of it.
    public_addr = "127.0.0.1:10600"
    # public_addr = "[::1]:10600"

    [client_auth]
    # This is how a client will authenticate to the scheduler.
    # # sccache-dist auth generate-shared-token --help
    type = "token"
    token = "token here"
    #
    # type = "jwt_hs256"
    # secret_key = ""

    [server_auth]
    # sccache-dist auth --help
    # To generate the secret_key:
    # # sccache-dist auth generate-jwt-hs256-key
    # To generate a key for a builder, use the command:
    # # sccache-dist auth generate-jwt-hs256-server-token --config /etc/sccache/scheduler.conf --secret-key "..." --server "builderip:builderport"
    type = "jwt_hs256"
    secret_key = "my secret key"

You can start the scheduler with:

    systemctl start sccache-dist-scheduler.service

If you have issues you can increase logging verbosity with:

    # systemctl edit sccache-dist-scheduler.service
    [Service]
    Environment="RUST_LOG=sccache=trace"

## Builder

Similar to the scheduler, the builder is configured with
[/etc/sccache/builder.conf]{.title-ref}. Most of the defaults should be
left \"as is\" but you will need to add the token generated from the
comments in [scheduler.conf - server_auth]{.title-ref}.

    # This is where client toolchains will be stored.
    # You should not need to change this as it is configured to work with systemd.
    cache_dir = "/var/cache/sccache-builder/toolchains"
    # The maximum size of the toolchain cache, in bytes.
    # If unspecified the default is 10GB.
    # toolchain_cache_size = 10737418240
    # A public IP address and port that clients will use to connect to this builder.
    public_addr = "127.0.0.1:10501"
    # public_addr = "[::1]:10501"

    # The URL used to connect to the scheduler (should use https, given an ideal
    # setup of a HTTPS server in front of the scheduler)
    scheduler_url = "https://127.0.0.1:10600"

    [builder]
    type = "overlay"
    # The directory under which a sandboxed filesystem will be created for builds.
    # You should not need to change this as it is configured to work with systemd.
    build_dir = "/var/cache/sccache-builder/tmp"
    # The path to the bubblewrap version 0.3.0+ `bwrap` binary.
    # You should not need to change this as it is configured for a default SUSE install.
    bwrap_path = "/usr/bin/bwrap"

    [scheduler_auth]
    type = "jwt_token"
    # This will be generated by the `generate-jwt-hs256-server-token` command or
    # provided by an administrator of the sccache cluster. See /etc/sccache/scheduler.conf
    token = "token goes here"

Again, you can start the builder with:

    systemctl start sccache-dist-builder.service

If you have issues you can increase logging verbosity with:

    # systemctl edit sccache-dist-builder.service
    [Service]
    Environment="RUST_LOG=sccache=trace"

You can configure many hosts as builders, and compilation jobs will be
distributed amongst them.

## Client

The client is the part that submits compilation work. You need to
configure your machine the same as single host with regard to the
environment variables.

Additionally you need to configure the file
[\~/.config/sccache/config]{.title-ref}. An example of this can be found
in [/etc/sccache/client.example]{.title-ref}.

    [dist]
    # The URL used to connect to the scheduler (should use https, given an ideal
    # setup of a HTTPS server in front of the scheduler)
    scheduler_url = "http://x.x.x.x:10600"
    # Used for mapping local toolchains to remote cross-compile toolchains. Empty in
    # this example where the client and build server are both Linux.
    toolchains = []
    # Size of the local toolchain cache, in bytes (5GB here, 10GB if unspecified).
    # toolchain_cache_size = 5368709120

    cache_dir = "/tmp/toolchains"

    [dist.auth]
    type = "token"
    # This should match the `client_auth` section of the scheduler config.
    token = ""

You can check the status with:

    sccache --stop-server
    sccache --dist-status

If you have issues, you can increase the logging with:

    sccache --stop-server
    SCCACHE_NO_DAEMON=1 RUST_LOG=sccache=trace sccache --dist-status

Then begin a compilation job and you will get the extra logging. To undo
this, run:

    sccache --stop-server
    sccache --dist-status

In addition, sccache even in distributed mode can still use cloud or
remote storage for items, using it\'s cache first, and the distributed
complitation second. Anything that can\'t be remotely complied will be
run locally.

## Verifying

If you compile something from your client, you should see messages like
this appear in journald in the builder/scheduler machine:

    INFO 2020-11-19T22:23:46Z: sccache_dist: Job 140 created and will be assigned to server ServerId(V4(x.x.x.x:10501))
    INFO 2020-11-19T22:23:46Z: sccache_dist: Job 140 successfully assigned and saved with state Ready
    INFO 2020-11-19T22:23:46Z: sccache_dist: Job 140 updated state to Started
    INFO 2020-11-19T22:23:46Z: sccache_dist: Job 140 updated state to Complete

