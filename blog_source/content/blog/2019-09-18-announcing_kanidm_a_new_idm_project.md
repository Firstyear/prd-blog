+++
title = "Announcing Kanidm - A new IDM project"
date = 2019-09-18
slug = "2019-09-18-announcing_kanidm_a_new_idm_project"
# This is relative to the root!
aliases = [ "2019/09/18/announcing_kanidm_a_new_idm_project.html", "blog/html/2019/09/18/announcing_kanidm_a_new_idm_project.html" ]
+++
# Announcing Kanidm - A new IDM project

Today I\'m starting to talk about my new project - Kanidm. Kanidm is an
IDM project designed to be correct, simple and scalable. As an IDM
project we should be able to store the identities and groups of people,
authenticate them securely to various other infrastructure components
and services, and much more.

You can find the source for [kanidm on
github](https://github.com/Firstyear/kanidm/blob/master/README.md).

For more details about what the project is planning to achieve, and what
we have already implemented please see the github.

## What about 389 Directory Server

I\'m still part of the project, and working hard on making it the best
LDAP server possible. Kanidm and 389-ds have different goals. 389
Directory Server is a globally scalable, distributed database, that can
store huge amounts of data and process thousands of operations per
second. 389-ds let\'s you build a system ontop, in any way you want. If
you want an authentication system today, use 389-ds. We are even working
on a self-service web portal soon too (one of our most requested
features!). Besides my self, no one on the (amazing) 389 DS team has any
association with kanidm (yet?).

Kanidm is an opinionated IDM system, and has strong ideas about how
authentication and users should be processed. We aim to be scalable, but
that\'s a long road ahead. We also want to have more web integrations,
client tools and more. We\'ll eventually write a kanidm to 389-ds sync
tool.

## Why not integrate something with 389? Why something new?

There are a lot of limitations with LDAP when it comes to modern
web-focused auth processes such as webauthn. Because of this, I wanted
to make something that didn\'t have the same limitations, and had
different ideas about data storage and apis. That\'s why I wanted to
make something new in parallel. It was a really hard decision to want to
make something outside of 389 Directory Server (Because I really do love
the project, and have great pride in the team), but I felt like it was
going to be more productive to build in parallel, than ontop.

## When will it be ready?

I think that a single-server deployment will be usable for small
installations early 2020, and a fully fledged system with replication
would be late 2020. It depends on how much time I have and what parts I
implement in what order. Current rough work order (late 2019) is
indexing, RADIUS integration, claims, and then self-service/web ui.

