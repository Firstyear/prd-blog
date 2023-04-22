+++
title = "Results from the OpenSUSE 2021 Rust Survey"
date = 2021-10-08
slug = "2021-10-08-results_from_the_opensuse_2021_rust_survey"
# This is relative to the root!
aliases = [ "2021/10/08/results_from_the_opensuse_2021_rust_survey.html" ]
+++
# Results from the OpenSUSE 2021 Rust Survey

From September the 8th to October the 7th, OpenSUSE has helped me host a
survey on how developers are using Rust in their environments. As the
maintainer of the Rust packages in SUSE and OpenSUSE it was important
for me to get a better understanding of how people are using Rust so
that we can make decisions that match how the community is working.

First, to every single one of the 1360 people who responded to this
survey, thank you! This exceeded my expectations and it means a lot to
have had so many people take the time to help with this.

All the data can be [found
here](https://github.com/Firstyear/rust-survey/tree/main/2021)

## What did you want to answer?

I had assistance from a psychology researcher at a local university to
construct the survey and her help guided the structure and many of the
questions. An important element of this was that the questions provided
shouldn\'t influence people into a certain answer, and that meant
questions were built in a way to get a fair response that didn\'t lead
people into a certain outcome or response pattern. As a result, it\'s
likely that the reasons for the survey was not obvious to the
participants.

What we wanted to determine from this survey:

-   How are developers installing rust toolchains so that we can attract
    them to OpenSUSE by reducing friction?
-   In what ways are people using distribution rust packages in their
    environments (contrast to rustup)?
-   Should our rust package include developer facing tools, or is it
    just another component of a build pipeline?
-   When people create or distribute rust software, how are they
    managing their dependencies, and do we need to provide tools to
    assist?
-   Based on the above, how can we make it easier for people to
    distribute rust software in packages as a distribution?
-   How do developers manage security issues in rust libraries, and how
    can this be integrated to reduce packaging friction?

## Lets get to the data

As mentioned there were 1360 responses. Questions were broken into three
broad categories.

-   Attitude
-   Developers
-   Distributors

### Attitude

This section was intended to be a gentle introduction to the survey,
rather than answering any specific question. This section had 413
non-answers, which I will exclude for now.

We asked three questions:

-   Rust is important to my work or projects (1 disagree - 5 agree)
-   Rust will become more important in my work or projects in the
    future.  (1 disagree - 5 agree)
-   Rust will become more important to other developers and projects in
    the future (1 disagree - 5 agree)

![image](/_static/rsurvey/1.png)

![image](/_static/rsurvey/2.png)

![image](/_static/rsurvey/3.png)

From this there is strong support that rust is important to individuals
today. It\'s likely this is biased as the survey was distributed mainly
in rust communities, however, we still had 202 responses that were less
than 3. Once we look at the future questions we see strong belief that
rust will become more important. Again this is likely to be biased due
to the communities the survey was distributed within, but we still see
small numbers of people responding that rust will not be important to
others or themself in the future.

As this section was not intended to answer any questions, I have chosen
not to use the responses of this section in other areas of the analysis.

### Developers

This section was designed to help answer the following questions:

-   How are people installing rust toolchains so that we can attract
    them to OpenSUSE by reducing friction?
-   In what ways are people using distribution rust packages in their
    environments (contrast to rustup)?
-   Should our rust package include developer facing tools, or is it
    just another component of a build pipeline?

We asked the following questions:

-   As a developer, I use Rust on the following platforms while
    programming.

-   On your primary development platform, how did you install your Rust
    toolchain?

-   

    The following features or tools are important in my development environment (do not use 1 - use a lot 5)

    :   -   Integrated Development Environments with Language Features
            (syntax highlight, errors, completion, type checking
        -   Debugging tools (lldb, gdb)
        -   Online Documentation (doc.rust-lang.org, docs.rs)
        -   Offline Documentation (local)
        -   Build Caching (sccache)

Generally we wanted to know what platforms people were using so that we
could establish what people on linux were using *today* vs what people
on other platforms were using, and then knowing what other platforms are
doing we can make decisions about how to proceed.

![image](/_static/rsurvey/4.png)

There were 751 people who responded that they were a developer in this
section. We can see Linux is the most popular platform used while
programming, but for \"Linux only\" (derived by selecting responses that
only chose Linux and no other platforms) this number is about equal to
Mac and Windows. Given the prevalence of containers and other online
linux environments it would make sense that developers access multiple
platforms from their preferred OS, which is why there are many responses
that selected multiple platforms for their work.

![image](/_static/rsurvey/5.png)

From the next question we see overwhelming support of rustup as the
preferred method to install rust on most developer machines. As we did
not ask \"why\" we can only speculate on the reasons for this decision.

![image](/_static/rsurvey/6.png)

When we isolate this to \"Linux only\", we see a slight proportion
increase in package manager installed rust environments, but there
remains a strong tendancy for rustup to be the preferred method of
installation.

This may indicate that even within Linux distros with their package
manager capabilities, and even with distributions try to provide rapid
rust toolchain updates, that developers still prefer to use rust from
rustup. Again, we can only speculate to why this is, but it already
starts to highlight that distribution packaged rust is unlikely to be
used as a developer facing tool.

![image](/_static/rsurvey/7.png)

![image](/_static/rsurvey/8.png)

![image](/_static/rsurvey/9.png)

Once we start to look at features of rust that developers rely on we see
a very interesting distribution. I have not included all charts here.
Some features are strongly used (IDE rls, online docs) where others seem
to be more distributed in attitude (debuggers, offline docs, build
caching). From the strongly supported features when we filter this by
linux users using distribution packaged rust, we see a similar (but not
as strong) trend for importance of IDE features. The other features like
debuggers, offline docs and build caching all remain very distributed.
This shows that tools like rls for IDE integration are very important,
but with only a small number of developers using packaged rust as
developers versus rustup it may not be an important area to support with
limited packaging resources and time. It\'s very likely that developers
who are on other distributions, mac or windows are more comfortable with
a rustup based installation process.

### Distributors

This section was designed to help answer the following questions:

-   Should our rust package include developer facing tools, or is it
    just another component of a build pipeline?
-   When people create or distribute rust software, how are they
    managing their dependencies, and do we need to provide tools to
    assist?
-   Based on the above, how can we make it easier for people to
    distribute rust software in packages as a distribution?
-   How do developers manage security issues in rust libraries, and how
    can this be integrated to reduce packaging friction?

We asked the following questions:

-   Which platforms (operating systems) do you target for Rust software
-   How do you or your team/community build or provide Rust software for
    people to use?
-   In your release process, how do you manage your Rust dependencies?
-   In your ideal workflow, how would you prefer to manager your Rust
    dependencies?
-   How do you manage security updates in your Rust dependencies?

![image](/_static/rsurvey/10.png)

Our first question here really shows the popularity of Linux as a target
platform for running rust with 570 out of 618 responses indicating they
target Linux as a platform.

![image](/_static/rsurvey/11.png)

Once we look at the distribution methods, both building projects to
packages and using distribution packaged rust in containers fall well
behind the use of rustup in containers and locally installed rust tools.
However if we observe container packaged rust and packaged rust binaries
(which likely use the distro rust toolchains) we have 205 uses of the
rust package out of 1280 uses, where we see 59 out of 680 from
developers. This does indicate a tendancy that the rust package in a
distribution is more likely to be used in a build pipeline over
developer use - but rustup still remains most popular. I would speculate
that this is because developers want to recreate the same process on
their development systems as their target systems which would likely
involve rustup as the method to ensure the identical toolchains are
installed.

The next questions were focused on rust dependencies - as a staticly
linked language, this changes the approach to how libraries can be
managed. To answer how we as a distribution should support people in the
way they want to manage libraries, we need to know how they use it
today, and how they would ideally prefer to manage this in the future.

![image](/_static/rsurvey/12.png)

![image](/_static/rsurvey/13.png)

In both the current process and ideal processes we see a large tendancy
to online library use from crates.io, and in both cases vendoring
(pre-downloading) comes in second place. Between the current process and
ideal process, we see a small reduction in online library use to the
other options. As a distribution, since we can not provide online access
to crates, we can safely assume most online crates users would move to
vendoring if they had to work offline for packaging as it\'s the most
similar process available.

![image](/_static/rsurvey/14.png)

![image](/_static/rsurvey/15.png)

We can also look at some other relationships here. People who provide
packages still tend to ideally prefer online crates usage, with
distribution libraries coming in second place here. There is still
significant momentum for packagers to want to use vendoring or online
dependencies though. When we look at ideal management strategies for
container builds, we see distribution packages being much less popular,
and online libraries still remaining at the top.

![image](/_static/rsurvey/16.png)

Finally, when we look at how developers are managing their security
updates, we see a really healthy statistic that many people are using
tools like cargo audit and cargo outdated to proactively update their
dependencies. Very few people rely on distribution packages for their
updates however. But it remains that we see 126 responses from users who
aren\'t actively following security issues which again highlights a need
for distributions who do provide rust packaged software to be proactive
to detect issues that may exist.

## Outcomes

By now we have looked at a lot of the survey and the results, so it\'s
time to answer our questions.

-   How are people installing rust toolchains so that we can attract
    them to OpenSUSE by reducing friction?

Developers are preferring the use of rustup over all other sources.
Being what\'s used on linux and other platforms, we should consider
packaging and distributing rustup to give options to users (who may wish
to avoid the [curl \| sh]{.title-ref} method.) I\'ve already started the
process to include this in OpenSUSE tumbleweed.

-   In what ways are people using distribution rust packages in their
    environments (contrast to rustup)?
-   Should our rust package include developer facing tools, or is it
    just another component of a build pipeline?

Generally developers tend strongly to rustup for their toolchains, where
distribution rust seems to be used more in build pipelines. As a result
of the emphasis on online docs and rustup, we can likely remove offline
documentation and rls from the distribution packages as they are either
not being used or have very few users and is not worth the distribution
support cost and maintainer time. We would likely be better to encourage
users to use rustup for developer facing needs instead.

To aid this argument, it appears that rls updates have been not
functioning in OpenSUSE tumbleweed for a few weeks due to a packaging
mistake, and no one has reported the issue - this means that the
\"scream test\" failed. The lack of people noticing this again shows
developer tools are not where our focus should be.

-   When people create or distribute rust software, how are they
    managing their dependencies, and do we need to provide tools to
    assist?
-   Based on the above, how can we make it easier for people to
    distribute rust software in packages as a distribution?

Distributors prefer cargo and it\'s native tools, and this is likely an
artifact of the tight knit tooling that exists in the rust community.
Other options don\'t seem to have made a lot of headway, and even within
distribution packaging where you may expect stronger desire for packaged
libraries, we see a high level of support for cargo directly to manage
rust dependencies. From this I think it shows that efforts to package
rust crates have not been effective to attract developers who are
currently used to a very different workflow.

-   How do developers manage security issues in rust libraries, and how
    can this be integrated to reduce packaging friction?

Here we see that many people are proactive in updating their libraries,
but there still exists many who don\'t actively manage this. As a
result, automating tools like cargo audit inside of build pipelines will
likely help packagers, and also matches their existing and known tools.
Given that many people will be performing frequent updates of their
libraries or upstream releases, we\'ll need to also ensure that the
process to update and commit updates to packages is either fully
automated or at least has a minimal hands on contact as possible. When
combined with the majority of developers and distributors prefering
online crates for dependencies, encouraging people to secure these
existing workflows will likely be a smaller step for them. Since rust is
staticly linked, we can also target our security efforts at leaf
(consuming) packages rather than the libraries themself.

## Closing

Again, thank you to everyone who answered the survey. It\'s now time for
me to go and start to do some work based on this data!

