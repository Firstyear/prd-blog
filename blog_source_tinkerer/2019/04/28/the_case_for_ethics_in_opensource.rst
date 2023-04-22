The Case for Ethics in OpenSource
=================================

For a long time there have been incidents in technology which have caused negative effects on people - from
leaks of private data, to interfaces that are not accessible, to even issues like UI's doing
things that may try to subvert a persons intent. I'm sure there are many more: and we could be here
all day listing the various issues that exist in technology, from small to great.

The theme however is that these issues continue to happen: we continue to make decisions in applications
that can have consequences to humans.

Software is pointless without people. People create software, people deploy software, people
interact with software, and even software indirectly can influence people's lives. At every layer
people exist, and all software will affect them in some ways.

I think that today, we have made a lot of progress in our communities around the deployment of
code's of conduct. These are great, and really help us to discuss the decisions and actions we
take within our communities - with the people who create the software. I would like this to go
further, where we can have a framework to discuss the effect of software on people that we write:
the people that deploy, interact with and are influenced by our work.

Disclaimers
-----------

I'm not a specialist in ethics or morality: I'm not a registered or certified engineer in the legal
sense. Finally, like all humans I am a product of my experiences which causes all my view points
to be biased through the lens of my experience.

Additionally, I specialise in Identity Management software, so many of the ideas and issues I have
encountered are really specific to this domain - which means I may overlook the issues in other areas.
I also have a "security" mindset which also factors into my decisions too.

Regardless I hope that this is a starting point to recieve further input and advice from others,
and a place where we can begin to improve.

The Problem
-----------

TODO: Discuss data handling practices

Let's consider some issues and possible solutions in work that I'm familiar with - identity
management software. Lets list a few "features". (Please don't email me about how these are
wrong, I know they are ...)

* Storing usernames as first and last name
* Storing passwords in cleartext.
* Deleting an account sets a flag to mark deletion
* Names are used as the primary key
* We request sex on signup
* To change account details, you have to use a command line tool

Now "technically", none of these decisions are incorrect at all. There is literally no bad
technical decision here, and everything is "technically correct" (not always the best kind
of correct).

What do we want to achieve?
---------------------------

There are lots of different issues here, but really want to prevent harm to a person. What is harm?
Well that's a complex topic. To me, it could be emotional harm, disrespect of their person, it
could be a feeling of a lack of control.

I don't believe it's correct to dictate a set of rules that people should follow. People will
be fatigued, and will find the process too hard. We need to trust that people can learn and
want to improve. Instead I believe it's important we provide important points that people should
be able to consider in a discussion around the development of software. The same way we discuss
technical implementation details, we should discuss potential human impact in every change we
have. To realise this, we need a short list of important factors that relate to humans.

I think the following points are important to consider when designing software. These relate
to general principles which I have learnt and researched.

People should be respected to have:

* Informed consent
* Choice over how they are identified
* Ability to be forgotten
* Individual Autonomy
* Free from Harmful Discrimination
* Privacy
* Ability to meaningfully access and use software

There is already some evidence in research papers to show that there are strong reasons for moral
positions in software. For example, to prevent harm to come to people, to respect peoples
autonomy and to conform to privacy legislation ( `source <https://plato.stanford.edu/entries/it-privacy/#MorReaForProPerDat>`_ ).

Let's apply these
-----------------

Given our set of "features", lets now discuss these with the above points in mind.

* Storing usernames as first and last name

This point clearly is in violation of the ability to choose how people are identified - some people
may only have a single name, some may have multiple family names. On a different level this also
violates the harmful discrimination rule due to the potential to disrespect individuals with
cultures that have different name schemes compared to western/English societies.

A better way to approach this is "displayName" as a freetext UTF8 case sensitive field, and to allow
substring search over the content (rather than attempting to sort by first/last name which also has
a stack of issues).

* Storing passwords in cleartext.

This one is a violation of privacy, that we risk the exposure of a password which *may* have been
reused (we can't really stop password reuse, we need to respect human behaviour). Not only that
some people may assume we DO hash these correctly, so we actually are violating informed consent
as we didn't disclose the method of how we store these details.

A better thing here is to hash the password, or at least to disclose how it will be stored and used.

* Deleting an account sets a flag to mark deletion

This violates the ability to be forgotten, because we aren't really deleting the account. It also
breaks informed consent, because we are being "deceptive" about what our software is actually doing
compared to the intent of the users request

A better thing is to just delete the account, or if not possible, delete all user data and leave
a tombstone inplace that represents "an account was here, but no details associated".

* Names are used as the primary key

This violates choice over identification, especially for women who have a divorce, or individuals
who are transitioning or just people who want to change their name in general. The reason for the
name change doesn't matter - what matters is we need to respect peoples right to identification.

A better idea is to use UUID/ID numbers as a primary key, and have name able to be changed at
any point in time.

* We request sex on signup

Violates a privacy as a first point - we probably have no need for the data unless we are a
medical application, so we should never ask for this at all. We also need to disclose why
we need this data to satisfy informed consent, and potentially to allow them to opt-out of
providing the data. Finally (if we really require this), to not violate self identification,
we need to allow this to
be a free-text field rather than a Male/Female boolean. This is not just in respect of
individuals who are LGBTQI+, but the reality that there are biologically people who
medically are neither. We also need to allow this to be changed at any time in the future.
This in mind Sex and Gender are different concepts, so we should be careful which we request - Sex
is the medical term of a person's genetics, and Gender is who the person identifies as.

Not only this, because this is a very personal piece of information, we must disclose how we
protect this information from access, who can see it, and if or how we'll ever share it with
other systems or authorities.

Generally, we probably don't need to know, so don't ask for it at all.

* To change account details, you have to use a command line tool

This violates a users ability to meaningfully access and use software - remember, people come from
many walks of life and all have different skill sets, but using command line tools is not something
we can universally expect.

A proper solution here is at minimum a web/graphical self management portal that is easy to access
and follows proper UX/UI design rules, and for a business deploying, a service desk with humans
involved that can support and help people change details on their account on their behalf if the
person is unable to self-support via the web service.


Proposal
--------

I think that OpenSource should aim to have a code of ethics - the same way we have a code of conduct
to guide our behaviour internally to a project, we should have a framework to promote discussion of
people's rights that use, interact with and are affected by our work. We should not focus on
technical matters only, but should be promoting people at the core of all our work. Every decision
we make is not just technical, but social.

I'm sure that there are more points that could be considere than what I have listed here: I'd
love to hear feedback to william at blackhats.net.au. Thanks!


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
