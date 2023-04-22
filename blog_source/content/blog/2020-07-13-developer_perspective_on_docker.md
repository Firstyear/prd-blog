+++
title = "Developer Perspective on Docker"
date = 2020-07-13
slug = "2020-07-13-developer_perspective_on_docker"
# This is relative to the root!
aliases = [ "2020/07/13/developer_perspective_on_docker.html" ]
+++
# Developer Perspective on Docker

A good mate of mine [Ron Amosa](https://ronamosa.io/) put a question up
on twitter about what do developers think Docker brings to the table.
I\'m really keen to see what he has to say (his knowledge of CI/CD and
Kubernetes is amazing by the way!), but I thought I\'d answer his
question from my view as a software engineer.

*Docker provides resource isolation and management to applications*

Lets break that down.

## What is a resource? What is an application?

It doesn\'t matter what kind of application we write: A Rust command
line tool, an embedded database in C, or a webserver or website with
Javascript. Every language and that program requires resources to run.
Let\'s focus on a Python webserver for this thought process.

Our webserver (which is an application) requires a lot of things to be
functional! It needs to access a network to open listening sockets, it
needs access to a filesystem to read pages or write to a database (like
sqlite). It needs CPU time to process requests, and memory to create a
stack/heap to work through those requests. But as well our application
also needs to be seperated and isolated from other programs too, so that
they can not disclose our data - but so that faults in our application
do not affect other services. It probably needs a seperate user and
group, which is a key idea in unix process isolation and security. Maybe
also there are things like SELinux or AppArmor that also provide extra
enhancements.

But why stop here there are many more. We might need system controls
(sysctls) that define networking stack behaviour like how TCP performs.
We may need specific versions of python libraries for our application.
Perhaps we also want to limit the system calls that our python
application can perform to our OS.

I hope we can see that the resources we have, really is more than simply
CPU and Memory here! Every application is really quite involved.

## A short view back to the past \...

In the olden days, as developers we had to be responsible for these
isolations. For example on a system, we\'d have to select a bind address
so that we could be configured to only use a single network device for
listening on. This not only meant that our applications had to support
this behaviour, but that a person had to read our documentation, and
find out how to configure that behaviour to isolate the networking
resource.

And of course many others. To limit the amount of CPU or RAM that was
available required you to configure ulimits for the user, and to select
which user was going to run our application.

Many problems have been seen too with a language like python where
libraries are not isolated and there are conflicts between which
[version different
applications](/blog/html/2019/12/18/packaging_vendoring_and_how_it_s_changing.html)
require. Is it the fault of python? The application developer? It\'s
hard to say \...

What about system calls? With an interpretted language like python, you
can\'t just set the capabilities flags or other hardening options
because they have to be set on the interpretter (python) which is used
in many places. An example where the resource (python) is shared between
many applications preventing us from creating isolated python runtimes.

Even things like SELinux and AppArmor required complex, hand created
profiles, that were cryptic at best, or led to being disabled in the
common case (It can\'t be secure if it\'s not usable! People will always
take the easy option \...).

And that\'s even before we look at init scripts - bash scripts that had
to be invoked in careful ways, and were all hand rolled, each adding
different mistakes or issues. It was a time where to \"package\" and
application and deploy it, required huge amounts of knowledge of a broad
range of topics.

In many cases, I have seen another way this manifested. Rather than
isolated applications (which was too hard), every application was
installed on a dedicated virtual machine. The resource management then
came as an artifact of every machine being seperate and managed by a
hypervisor.

## Systemd

Along came systemd though, and it got us much further. It provided
consistent application launch tools, and has done a lot of work to
manage and provide resource management such as cgroups (cpu, mem),
dynamic users, some types of filesystem isolation and some more. Systemd
as an init system has done some really good stuff.

But still problems exist. Applications still require custom SELinux or
AppArmor profiles, and systemd can\'t help managing network interfaces
(that still falls on the application).

It also still relies on you to put the files in place, or a distribution
package to get the file content into the system.

## Docker

Docker takes this even further. Docker manages and arbitrates every
resource your application requires, even the filesystem and install
process. For example, a very complex topic like CPU or memory limit\'s
on Linux, becomes quite simple in docker which exposes CPU and memory
tunables. Docker allows sysctls per container. You assign and manage
storage.

    docker run -v db:/data/db -v config:/data/config --network private_net \
        --memory 1024M --shm-size 128M -P 80:8080 --user isolated \
        my/application:version

From this command we can see what resources are involved. We know that
we mount two storage locations. We can see that we confine the network
to a private network, and that we want to limit memory to 1024M. We also
can see we\'ll be listening on port 80 which remaps to the container
internally. We even know what user we\'ll run as so we can assign
permissions to the volumes. Our application is also defined as is it\'s
version.

Not only can we see what resources we are using there are a lot of other
benefits. Docker can dynamically generate selinux/apparmor isolation
profiles, so we get stronger process isolation between containers and
host processes. We know that the filesystem of this container is
isolated from others, so they can have and bundle the correct versions
of dependencies. We know how to start, stop, and even monitor the
application. It can even have health checks. Logs will (should?) go to
stdout/err which docker will forward to a log collector we can define.
In the future each application may even be in it\'s own virtual memory
space (IE seperate vm\'s).

Docker provides a level of isolation to resources that is still hard to
achieve in systemd, and not only that it makes very advanced or complex
configurations easy to access and use. Accesibility of these features is
vitally important to allow all people to create robust applications in
their environments. But it also allows me as a developer to know what
resources *can* exist in the container and how to interact with these in
a way that will respect the wishes of the deploying administrator.

## Docker Isn\'t Security Isolation

It\'s worth noting that while Docker can provide SELinux and AppArmor
profiles, Docker is not an effective form of security isolation. It
certainly makes the bar much much higher than before yes! And that\'s
great! And I hope that bar continues to rise. However today we do live
in an age where there are many attacks still locally on linux kernels
and the fix delay in these is still long. We also still see CPU
sidechannels, and these will never be resolved [while we rely on
asynchronous CPU
behaviour](/blog/html/2020/01/20/there_are_no_root_causes.html).

If you have high value data, it is always best to have seperated
physical machines for these applications, and to always patch
frequently, have a proper CI/CD pipeline, and centralised logging, and
much much more. Ask your security team! I\'m sure they\'d love to help
:)

## Conclusion

For me personally, docker is about resource management and isolation. It
helps me to define an interface that an admin can consume and interact
with, making very advanced concepts easy to use. It gives me trust that
applications will run in a way that is isolated and known all the way
from development and testing through to production under high load. By
making this accessible, it means that anyone - from a single docker
container to a giant kubernetes cluster, can have really clear knowledge
of how their applications are operating.

