Usability of software: The challenges facing projects
=====================================================

I have always desired the usability of software like Directory Server to improve. As a former system administrator,
usabilty and documentation are very important for me. Improvements to usability can eliminate load on documentation,
support services and more.

Consider a microwave. No one reads the user manual. They unbox it, plug it in, and turn it on. You punch in a time and
expect it to "make cold things hot". You only consult the manual if it blows up.

Many of these principles are rooted in the field of design. Design is an important and often over looked part of
software development - All the way from the design of an API to the configuration, and even the user interface
of software.

.. more::

I have seen this distiction made in the grades of a programmer. The distinction is not about their familiarity with
language or systems, but their views on design and usability. When a programmer encounters an issue, they say "this
is just how it is" and work around it. The software engineer will say "we should document this issue". The senior
engineer says "how can we redesign this to make it not a problem at all?"

The goal of the engineer should not be to make a piece of software that is in your face, it is to make a system
that like many objects, is invisible when it works.

So few people consider the design and engineering time spent to make objects like zippers, velcro, even wallets, chairs,
tables and more. When you have a well designed object, you feel it is barely there. But a poorly designed one irritates
and irks rather than improving your view of it. For example, when I sit on a chair, I want to feel comfortable, but without thinking
of the presence of the chair. Were I to feel the presence of the chair, it's likely due to some discomfort - this means the
chair has failed.

Another aspect of this is configuration. Most people, even technical ones in computing do not want complex
configuration or manuals. They want simple. Coffee machines are a great parallel to this. Some people enjoy
a machine where you can configure the temperature, pressure, grind, and more. But the majority do not care. They
want their pod machine that allows you to press the button and move on.

What does this have to do with software?
========================================

Lets take a project like Directory Server. Admins *do not* read the manual and they *do not* want to know or learn
about the intricate details of LDAP. They want to install an instance, add some users, and that's it.

Historically we have defaulted to a system where the admin is a highly informed subject expert, who is willing to
invest time in building and learning expertise in our system. But our world is changing. We will always have those
few who invest time and energy, but they are the minority.

This means that we need to design DS and others not to be in your face, but to correct out of the box. We should be
*removing* unused parts, *correcting* defaults to be fit for the majority, *dynamically*
responding and adapting to the environment our software is deployed in. Our aim should be to reduce the size of
our documentation manual - not enlarge it. In summary:

We should aim to be invisible for 99% of cases, but allow the 1% of experts to have the configuration they want.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
