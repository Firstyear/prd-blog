Getting Started Packaging A Rust CLI Tool in SUSE OBS
=====================================================

Distribution packaging always seems like something that is really difficult or hard to do, but the SUSE
`Open Build Service <https://build.opensuse.org>`_ makes it really easy to not only build
packages, but to then contribute them to Tumbleweed. Not only that, OBS can also build for
Fedora, CentOS and more.

Getting Started
---------------

You'll need to sign up to service - there is a sign up link on the front page of `OBS <https://build.opensuse.org>`_

To do this you'll need a SUSE environment. Docker is an easy way to create this without
having to commit to a full virtual machine / install.

::

    docker run \
        --security-opt=seccomp:unconfined --cap-add=SYS_PTRACE --cap-add=SYS_CHROOT --cap-add=SYS_ADMIN \
        -i -t opensuse/tumbleweed:latest /bin/sh

* NOTE: We need these extra privileges so that the osc build command can work due to how it uses chroots/mounts.

Inside of this we'll need some packages to help make the process easier.

::

    zypper install obs-service-cargo_vendor osc obs-service-tar obs-service-obs_scm \
        obs-service-recompress obs-service-set_version obs-service-format_spec_file cargo sudo

You should also install your editor of choice in this command (docker images tend not to come
with any editors!)

You'll need to configure osc, which is the CLI interface to OBS. This is done in the file `~/.config/osc/oscrc`.
A minimal starting configuration is:

::

    [general]
    # URL to access API server, e.g. https://api.opensuse.org
    # you also need a section [https://api.opensuse.org] with the credentials
    apiurl = https://api.opensuse.org
    [https://api.opensuse.org]
    user = <username>
    pass = <password>

You can check this works by using the "whois" command.

::

    # osc whois
    firstyear: "William Brown" <email here>

Optionally, you may install `cargo lock2rpmprovides <https://github.com/Firstyear/cargo-lock2rpmprovides>`_
to assist with creation of the license string for your package:

::

    cargo install cargo-lock2rpmprovides

Packaging A Rust Project
------------------------

In this example we'll use a toy Rust application I created called `hellorust <https://github.com/Firstyear/hellorust>`_.
Of course, feel free to choose your own project or Rust project you want to package!

* HINT: It's best to choose binaries, not libraries to package. This is because Rust can self-manage it's dependencies, so we don't need to package every library. Neat!

First we'll create a package in our OBS home project.

::

    osc co home:<username>
    cd home:<username>
    osc mkpac hellorust
    cd hellorust

OBS comes with a lot of useful utilities to help create and manage sources for our project. First
we'll create a skeleton RPM spec file. This should be in a file named `hellorust.spec`

::

    %global rustflags -Clink-arg=-Wl,-z,relro,-z,now -C debuginfo=2

    Name:           hellorust
    #               This will be set by osc services, that will run after this.
    Version:        0.0.0
    Release:        0
    Summary:        A hello world with a number of the day printer.
    #               If you know the license, put it's SPDX string here.
    #               Alternately, you can use cargo lock2rpmprovides to help generate this.
    License:        Unknown
    #               Select a group from this link:
    #               https://en.opensuse.org/openSUSE:Package_group_guidelines
    Group:          Amusements/Games/Other
    Url:            https://github.com/Firstyear/hellorust
    Source0:        %{name}-%{version}.tar.xz
    Source1:        vendor.tar.xz
    Source2:        cargo_config

    BuildRequires:  rust-packaging
    ExcludeArch:    s390 s390x ppc ppc64 ppc64le %ix86

    %description
    A hello world with a number of the day printer.

    %prep
    %setup -q
    %setup -qa1
    mkdir .cargo
    cp %{SOURCE2} .cargo/config
    # Remove exec bits to prevent an issue in fedora shebang checking
    find vendor -type f -name \*.rs -exec chmod -x '{}' \;

    %build
    export RUSTFLAGS="%{rustflags}"
    cargo build --offline --release

    %install
    install -D -d -m 0755 %{buildroot}%{_bindir}

    install -m 0755 %{_builddir}/%{name}-%{version}/target/release/hellorust %{buildroot}%{_bindir}/hellorust

    %files
    %{_bindir}/hellorust

    %changelog

There are a few commented areas you'll need to fill in and check. But next we will create a service
file that allows OBS to help get our sources and bundle them for us. This should go in a file called
`_service`

::

    <services>
      <service mode="disabled" name="obs_scm">
        <!-- ✨ URL of the git repo ✨ -->
        <param name="url">https://github.com/Firstyear/hellorust.git</param>
        <param name="versionformat">@PARENT_TAG@~git@TAG_OFFSET@.%h</param>
        <param name="scm">git</param>
        <!-- ✨ The version tag or branch name from git ✨ -->
        <param name="revision">v0.1.1</param>
        <param name="match-tag">*</param>
        <param name="versionrewrite-pattern">v(\d+\.\d+\.\d+)</param>
        <param name="versionrewrite-replacement">\1</param>
        <param name="changesgenerate">enable</param>
        <!-- ✨ Your email here ✨ -->
        <param name="changesauthor"> YOUR EMAIL HERE </param>
      </service>
      <service mode="disabled" name="tar" />
      <service mode="disabled" name="recompress">
        <param name="file">*.tar</param>
        <param name="compression">xz</param>
      </service>
      <service mode="disabled" name="set_version"/>
      <service name="cargo_vendor" mode="disabled">
          <!-- ✨ The name of the project here ✨ -->
         <param name="srcdir">hellorust</param>
         <param name="compression">xz</param>
      </service>
    </services>

Now this service file does a lot of the heavy lifting for us:

* It will fetch the sources from git, based on the version we set.
* It will turn them into a tar.xz for us.
* It will update the changelog for the rpm, and set the correct version in the spec file.
* It will download our rust dependencies, and then bundle them to vendor.tar.xz.

So our current work dir should look like:

::

    # ls -1 .
    .osc
    _service
    hellorust.spec

Now we can run `osc service ra`. This will run the services in our `_service` file as we mentioned.
Once it's complete we'll have quite a few more files in our directory:

::

    # ls -1 .
    _service
    _servicedata
    cargo_config
    hellorust
    hellorust-0.1.1~git0.db340ad.obscpio
    hellorust-0.1.1~git0.db340ad.tar.xz
    hellorust.obsinfo
    hellorust.spec
    vendor.tar.xz

Inside the `hellorust` folder (`home:username/hellorust/hellorust`), is a checkout of our source. If
you cd to that directory, you can run `cargo lock2rpmprovides` which will display your license
string you need:

::

    License: ( Apache-2.0 OR MIT ) AND ( Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT ) AND

Just add the license from the project, and then we can update our `hellorust.spec` with the correct
license.

::

    License: ( Apache-2.0 OR MIT ) AND ( Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT ) AND MPL-2.0

* HINT: You don't need to use the emitted "provides" lines here. They are just for fedora rpms to adhere to some of their policy requirements.

Now we can build our package on our local system to test it. This may take a while to get all its
build dependencies and other parts, so be patient :)

::

    osc build

If that completes successfully, you can now test these rpms:

::

    # zypper in /var/tmp/build-root/openSUSE_Tumbleweed-x86_64/home/abuild/rpmbuild/RPMS/x86_64/hellorust-0.1.1~git0.db340ad-0.x86_64.rpm
    (1/1) Installing: hellorust-0.1.1~git0.db340ad-0.x86_64  ... [done]
    # rpm -ql hellorust
    /usr/bin/hellorust
    # hellorust
    Hello, Rust! The number of the day is: 68

Next you can commit to your project. Add the files that we created:

::

    # osc add _service cargo_config hellorust-0.1.1~git0.db340ad.tar.xz hellorust.spec vendor.tar.xz
    # osc status
    A    _service
    ?    _servicedata
    A    cargo_config
    ?    hellorust-0.1.1~git0.db340ad.obscpio
    A    hellorust-0.1.1~git0.db340ad.tar.xz
    ?    hellorust.obsinfo
    A    hellorust.spec
    A    vendor.tar.xz

HINT: You DO NOT need to commit _servicedata OR hellorust-0.1.1~git0.db340ad.obscpio OR hellorust.obsinfo

::

    osc ci

From here, you can use your packages from your own respository, or you can forward them to OpenSUSE Tumbleweed (via Factory).
You likely need to polish and add extra parts to your package for it to be accepted into Factory, but this should at least
make it easier for you to start!

For more, see the `how to contribute to Factory <https://en.opensuse.org/openSUSE:How_to_contribute_to_Factory>`_ document. To submit
to Leap, the package must be in Factory, then you can request it to be `submitted to Leap <https://en.opensuse.org/openSUSE:Packaging_for_Leap>`_ as well.

Happy Contributing! 🦎🦀

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
