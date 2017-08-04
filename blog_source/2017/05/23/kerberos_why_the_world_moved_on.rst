Kerberos - why the world moved on
=================================

For a long time I have tried to integrate and improve authentication technologies in my own environments. I have advocated the use of GSSAPI, IPA, AD, and others. However, the more I have learnt, the further I have seen the world moving away. I want to explore some of my personal experiences and views as to why this occured, and what we can do.

.. more::

What is kerberos and gssapi?
----------------------------

This is a completely valid question! Most modern application developers or users would never have heard of kerberos. Kerberos was developed by MIT in the 1980s to allow secure authentication of services. A key focus was that your password was never transmitted over the next. Kerberos relies on exchange of "tickets" to prove the identity, relying on strong cryptography to protect the tickets from theft. In 1993 kerberos protocol version 5 was released and is the current basis of all kerberos implementations.

Prominent uses of kerberos are Microsoft's Active Directory and Red Hat's FreeIPA (through MIT krb5).

GSSAPI is a standard for authentication between a client and a service that may use kerberos as the authentication mechanism. In this document, you can assume that GSSAPI/KRB are semi-interchangeable as they are tightly bound.

Single Sign On? Secure tickets? This sounds great!
--------------------------------------------------

And it should! The promise of kerberos is a lofty one - passwords are never transmitted, you get single sign on to all network resources, and tickets can be revoked.

The issues with kerberos are not a *techincal* one, but a *human* one.

Kerberos is notoriously difficult to setup and administer, use, and when it breaks, it explodes in a glorious mess.

Integration with applications
-----------------------------

For kerberos to function, services (such as websites, fileshares) need to provide kerberos or GSSAPI to negotiate the authentication. Because of the complexity of kerberos as a library, developers don't want to integrate with it. I have attemped a number of times, and it's a confusing mess of "steps" and "credentials", that is nigh impossible to understand or use. If someone as passionate about authentication such as myself can't make it work, others will not be invested in utilising it. This is before we get to ...

Debugging kerberos
------------------

When kerberos breaks, it generally does so with a generic and unhelpful message. As a result, it's highly demotivating to integrate with. It took me 3 years to find the largely undocumented KRB5_TRACE environment variable, and even then, it still is very complex to resolve issues. Throw in extreme sensitivity to clock accuracy (and ntp's inability to sync time on linux) and you have a recipe for broken services. Because of the lack of usability to resolve issues *no one wants to integrate with it*. If you look at modern software applications nearly *none* of them offer GSSAPI options, because it's just too hard (contrast this to SAML, Oauth or LDAP, which almost everything interacts with correctly).

House of cards
--------------

Every single application stack that internally relies on kerberos is extremely fragile. There is nothing worse then when your AD keytabs get out of sync due to a machine password reset issue, or when your IPA server stops functioning because it stuffed up your ldap server's keytab. All of these applications end up being like a fragile house of cards. This is because kerberos is fundamentally *difficult* for a human to configure and utilise correctly.

Modern deployment strategies
----------------------------

With the rise of containers, application developers have moved to stateless, fast deploying applications. Because of the way they work, you push state to the boundaries. On one edge, databases for content, the other load balancers for network and security state such as TLS keys.

Because of how GSSAPI and kerberos operate, you can't push this state outwards - every container needs kerberos ticket material built in. This means your build systems need access to the highly privileged ability to deploy tickets (though it is possible to have policies constraint who can issue what tickets). It adds another moving part in a complex system, and when we go back to debugging, it's adding a very fragile authentication component to a distributed system. It's a risk that many want to avoid (if they even care about GSSAPI/kerberos at all).

A challenger appears
--------------------

To make matters worse for kerberos the once king of SSO, we have seen the rise of oauth and saml. With the migration of many applications to the web, kerberos with it's strong "desktop" and thick application focus has lost out to the simpler oauth and saml. Most application developers would rather integrate with these protocols than kerberos. Sure you can allow SAML to issue tokens based on a GSSAPI negotiation: but who configures their machine to use kerberos?

Ignorance of modern threats
---------------------------

Kerberos is so focused on cryptographic threats and mitm, that they have forgotten that kerberos itself opens up the gateway to many other vulnerabilites. From MS AD kerberoasting, to straight up stealing ticket caches. Kerberos is `like this xkcd <https://www.xkcd.com/538/>`_ comic - no one attacks kerberos, we attack and steal passwords or the already created tickets. I would argue that kerberos has enabled signifigant damage on compromised windows (and soon linux) networks due to trivially enabling lateral movement. Pop one box with a domain admin cred, it's game over.

The user experience just sucks
------------------------------

As a kerberos client, the experience just *sucks*. Even at a work place that highly integrates with kerberos, I prefer to never use it in favour of SSH keys + saml portal. Most of our new staff are never on boarded to use it. It still involves arcane command line interactions, many services don't integrate with it at all, and it breaks regularly. Less and less staff rely on it, and we see it eroding daily. You only have one credential cache on a machine, so when I ran kerberos at home, it would conflict with my work tickets (you can't have more than one ticket at a time), so I would have to choose - home or work. The documentation is generally not there, and the user interaction is really poor. Users *don't want* to use kerberos, when it actively confuses them and makes their daily work harder.


Right - what would you suggest instead then?
--------------------------------------------

* TLS certificates for identity
* SSH keys for access to servers
* SAML portals for web applications (with TLS auth for bonus marks)
* Back these to LDAP.

Because LDAP is a database, containerised applications treat it like another database. SSH keys don't enable the same lateral movement risk. TLS certificates are still a pain to use, but they are still better than KRB for authentication today. Ultimately, we are watching TLS, SAML and Oauth take over SSO. So lets invest in those.

In my view, I'm seeing Microsoft, one of the real pioneers of KRB, strongly pushing ADFS (their SAML system) over GSSAPI/Kerberos - make of this what you will.

Conclusion
----------

Modern software has to be well designed, according to real human interaction design principles - not an engineers ideas of what is "acceptable" design.

Kerberos has lost. No one wants to integrate with it. The client experience is poor. Lets leave it to die naturally, and move on to architectures that match modern software and usage.


PS
--

Before anyone who works on kerberos or related project gets up an says "Ohh but just look at ..." - no, no, stop. Stop. This is a description of the *user experience* with kerberos today. Even if *you* know how it works, or know of all the documentation that does *NOT* mean that *I* know about it, or the rest of the world does. The evidence is there, and the developers of the opensource world have voted to "move on" from kerberos on GSSAPI. No amount of "ohh but you can just do ..." will change that. It's done.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
