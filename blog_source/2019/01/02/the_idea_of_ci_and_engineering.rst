The idea of CI and Engineering
==============================

In software development I see and interesting trend and push towards continuous
integration, continually testing, and testing in production. These techniques
are designed to allow faster feedback on errors, use real data for application
testing, and to deliver features and changes faster.

But is that really how people use software on devices? When we consider an operation
like google or amazon, this always online technique may work, but what happens
when we apply a continous integration and "we'll patch it later" mindset
to devices like phones or internet of things?

What happens in other disciplines?
----------------------------------

In real engineering disciplines like aviation or construction, techniques like
this don't really work. We don't continually build bridges, then fix them when
they break or collapse. There are people who provide formal analysis of materials,
their characteristics. Engineers consider careful designs, constraints, loads
and situations that may occur. The structure is planned, reviewed and verified
mathematically. Procedures and oversight is applied to ensure correct building
of the structure. Lessons are learnt from past failures and incidents and are
applied into every layer of the design and construction process. Communication
between engineers and many other people is critical to the process. Concerns are
always addressed and managed.

The first thing to note is that if we just built lots of scale-model bridges and
continually broke them until we found their limits, this would waste many
resources to do this. Bridges are carefully planned and proven.

So whats the point with software?
---------------------------------

Today we still have a mindset that continually breaking and building is a reasonable
path to follow. It's not! It means that the only way to achieve quality is to have
a large test suite (requires people and time to write), which has to be further
derived from failures (and those failures can negatively affect real people),
then we have to apply large amounts of electrical energy to continually run
the tests. The test suites can't even guarantee complete coverage of all situations
and occurances!

This puts CI techniques out of reach of many application developers due to time
and energy (translated to dollars) limits. Services like travis on github
certainly helps to lower the energy requirement, but it doesn't stop the
time and test writing requirements.

No matter how many tests we have for a program, if that program is written in C
or something else, we continually see faults and security/stability issues
in that software.

What if we CI on ... a phone?
-----------------------------

Today we even have hardware devices that are approached as though they "test
in production" is a reasonable thing. It's not! People don't patch, telcos don't
allow updates out to users, and those that are aware, have to do custom rom
deployment. This creates an odd dichomtemy of "haves" and "haves not", of those
in technical know how who have a better experience, and the "haves not" who have
to suffer potentially insecure devices. This is especially terrifying given
how deeply personal phones are.

This is a reality of our world. People do not patch. They do not patch phones,
laptops, network devices and more. Even enterprises will avoid patching if
possible. Rather than trying to shift the entire culture of humans to "update
always", we need to write software that can cope in harsh conditions, for long
term. We only need to look to software in aviation to see we can absolutely
achieve this!

What should we do?
------------------

I believe that for software developers to properly become software engineers we
should look to engineers in civil and aviation industries. We need to apply:

* Regualation and ethics (Safety of people is always first)
* Formal verification
* Consider all software will run long term (5+ years)
* Improve team work and collaboration on designs and development

The reality of our world is people are deploying devices (routers, networks, phones,
lights, laptops more ...) where they may never be updated or patched in their
service life. Even I'm guilty (I have a modem that's been unpatched for about 6 years
but it's pretty locked down ...). As a result we need to rely on proof that the
device *can not* fail at build time, rather than *patch it later* which may
never occur! Putting formal verification first, and always considering user
safety and rights first, shifts a large burden to us in terms of time. But
many tools (Coq, fstar, rust ...) all make formal verification more accessible
to use in our industry. Verifying our software is a far stronger assertion of quality
than "throw tests at it and hope it works".

You're crazy William, and also wrong
------------------------------------

Am I? Looking at "critical" systems like iPhone encryption hardware, they are running
the formally verified Sel4. We also heard at Kiwicon in 2018 that Microsoft and XBox
are using formal verification to design their low levels of their system to
prevent exploits from occuring in the first place.

Over time our industry will evolve, and it will become easier and more cost
effective to formally verify than to operate and deploy CI. This doesn't mean we
don't need tests - it means that the first line of quality
should be in verification of correctness using formal techniques rather than
using tests and CI to prove correct behaviour. Tests are certainly still required
to assert further behavioural elements of software.

Today, if you want to do this, you should be looking at Coq and program extraction,
fstar and the kremlin (project everest, a formally verified https stack), Rust
(which has a subset of the safe language formally proven). I'm sure there are more,
but these are the ones I know off the top of my head.

Conclusion
----------

Over time our industry *must* evolve to put the safety of humans first. To achive
this we must look to other safety driven cultures such as aviation and civil
engineering. Only by learning from their strict disciplines and behaviours
can we start to provide software that matches behavioural and quality expectations
humans have for software.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
