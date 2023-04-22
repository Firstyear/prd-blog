+++
title = "Using SUSE Leap Enterprise with Docker"
date = 2020-08-26
slug = "2020-08-26-using_suse_leap_enterprise_with_docker"
# This is relative to the root!
aliases = [ "2020/08/26/using_suse_leap_enterprise_with_docker.html" ]
+++
# Using SUSE Leap Enterprise with Docker

It\'s a little bit annoying to connect up all the parts for this. If you
have a SLE15 system then credentials for SCC are automatically passed
into containers via secrets.

But if you are on a non-SLE base, like myself with MacOS or OpenSUSE
you\'ll need to provide these to the container in another way. The
documentation is a bit tricky to search and connect up what you need but
in summary:

-   Get [/etc/SUSEConnect]{.title-ref} and
    [/etc/zypp/credentials.d/SCCcredentials]{.title-ref} from an SLE
    install that has been registered. The SLE version does not matter.
-   Mount them into the image:

```{=html}
<!-- -->
```
    docker ... -v /scc/SUSEConnect:/etc/SUSEConnect \
        -v /scc/SCCcredentials:/etc/zypp/credentials.d/SCCcredentials \
        ...
        registry.suse.com/suse/sle15:15.2

Now you can use the images from [the SUSE
registry](https://registry.suse.com/). For example [docker pull
registry.suse.com/suse/sle15:15.2]{.title-ref} and have working zypper
within them.

If you want to add extra modules to your container (you can list what\'s
available with container-suseconnect from an existing SLE container of
the same version), you can do this by adding environment variables at
startup. For example, to add dev tools like gdb:

    docker ... -e ADDITIONAL_MODULES=sle-module-development-tools \
        -v /scc/SUSEConnect:/etc/SUSEConnect \
        -v /scc/SCCcredentials:/etc/zypp/credentials.d/SCCcredentials \
        ...
        registry.suse.com/suse/sle15:15.2

This also works during builds to add extra modules.

HINT: SUSEConnect and SCCcredentials and not version dependent so will
work in any image version.

