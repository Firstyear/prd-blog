+++
title = "docker buildx for multiarch builds"
date = 2020-08-06
slug = "2020-08-06-docker_buildx_for_multiarch_builds"
# This is relative to the root!
aliases = [ "2020/08/06/docker_buildx_for_multiarch_builds.html", "blog/html/2020/08/06/docker_buildx_for_multiarch_builds.html" ]
+++
# docker buildx for multiarch builds

I have been previously building Kanidm with plain docker build, but
recently a community member wanted to be able to run kanidm on arm64.
That meant that I needed to go down the rabbit hole of how to make this
work \...

## What not to do \...

There is a previous method of using manifest files to allow multiarch
uploads. It\'s pretty messy but it works, so this is an option if you
want to investigate but I didn\'t want to pursue it.

Bulidx exists and I got it working on my linux machine with the steps
from
[here](https://www.docker.com/blog/getting-started-with-docker-for-arm-on-linux/)
but the build took more than 3 hours, so I don\'t recommend it if you
plan to do anything intense or frequently.

## Buildx cluster

Docker has a cross-platform building toolkit called buildx which is
currently tucked into the experimental features. It can be enabled on
docker for mac in the settings (note: you only need experimental support
on the coordinating machine aka your workstation).

Rather than follow the [official
docs](https://docs.docker.com/buildx/working-with-buildx/) this will
branch out. The reason is that buildx in the official docs uses
qemu-aarch64 translation which is very slow and energy hungry, taking a
long time to produce builds. As mentioned already I was seeing in excess
of 3 hours for aarch64 on my builder VM or my mac.

Instead, in this configuration I will use my mac as a coordinator, and
an x86_64 VM and a rock64pro as builder nodes, so that the builds are
performed on native architecture machines.

First we need to configure our nodes. In
[/etc/docker/daemon.json]{.title-ref} we need to expose our docker
socket to our mac. I have done this with the following:

    {
      "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2376"]
    }

*WARNING*: This configuration is HIGHLY INSECURE. This exposes your
docker socket to the network with no authentication, which is equivalent
to un-authenticated root access. I have done this because my builder
nodes are on an isolated and authenticated VLAN of my home network. You
should either do similar or use TLS authentication.

NOTE: The [ssh://]{.title-ref} transport does not work for docker
buildx. No idea why but it don\'t.

Once this is done restart docker on the two builder nodes.

Now we can configure our coordinator machine. We need to check buildx is
present:

    docker buildx --help

We then want to create a new builder instance and join our nodes to it.
We can use the DOCKER_HOST environment variable for this:

    DOCKER_HOST=tcp://x.x.x.x:2376 docker buildx create --name cluster
    DOCKER_HOST=tcp://x.x.x.x:2376 docker buildx create --name cluster --append

We can then startup and bootstrap the required components with:

    docker buildx use cluster
    docker buildx inspect --bootstrap

We should see output like:

    Name:   cluster
    Driver: docker-container

    Nodes:
    Name:      cluster0
    Endpoint:  tcp://...
    Status:    running
    Platforms: linux/amd64, linux/386

    Name:      cluster1
    Endpoint:  tcp://...
    Status:    running
    Platforms: linux/arm64, linux/arm/v7, linux/arm/v6

If we are happy with this we can make this the default builder.

    docker buildx use cluster --default

And you can now use it to build your images such as:

    docker buildx build --push --platform linux/amd64,linux/arm64 -f Dockerfile -t <tag> .

Now I can build my multiarch images much quicker and efficently!

