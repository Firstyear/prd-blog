+++
title = "GSoC 2017 - Mentor Report from 389 Project"
date = 2017-08-24
slug = "2017-08-24-gsoc_2017_mentor_report_from_389_project"
# This is relative to the root!
aliases = [ "2017/08/24/gsoc_2017_mentor_report_from_389_project.html" ]
+++
# GSoC 2017 - Mentor Report from 389 Project

This year I have had the pleasure of being a mentor for the Google
Summer of Code program, as part of the Fedora Project organisation. I
was representing the [389 Directory Server
Project](http://www.port389.org/) and offered students the oppurtunity
to [work on our command line
tools](https://fedoraproject.org/wiki/Summer_coding_ideas_for_2017#389_Directory_Server:_developing_administrative_tools)
written in python.

## Applications

From the start we have a large number of really talented students apply
to the project. This was one of the hardest parts of the process was to
choose a student, given that I wanted to mentor all of them. Sadly I
only have so many hours in the day, so we chose Ilias, a student from
Greece. What really stood out was his interest in learning about the
project, and his desire to really be part of the community after the
project concluded.

## The project

The project was very deliberately \"loose\" in it\'s specification.
Rather than giving Ilias a fixed goal of you will implement X, Y and Z,
I chose to set a \"broad and vague\" task. Initially I asked him to
investigate a single area of the code (the MemberOf plugin). As he
investigated this, he started to learn more about the server, ask
questions, and open doors for himself to the next tasks of the project.
As these smaller questions and self discoveries stacked up, I found
myself watching Ilias start to become a really complete developer, who
could be called a true part of our community.

Ilias\' work was exceptional, and he has documented it in his [final
report
here](https://iliaswrites.wordpress.com/2017/08/23/final-gsoc-2017-report/)
.

Since his work is complete, he is now free to work on any task that
takes his interest, and he has picked a good one! He has now started to
dive deep into the server internals, looking at part of our backend
internals and how we dump databases from id2entry to various output
formats.

## What next?

I will be participating next year - Sadly, I think the python project
oppurtunities may be more limited as we have to finish many of these
tasks to release our new CLI toolset. This is almost a shame as the
python components are a great place to start as they ease a new
contributor into the broader concepts of LDAP and the project structure
as a whole.

Next year I really want to give this oppurtunity to an under-represented
group in tech (female, poc, etc). I personally have been really inspired
by Noriko and I hope to have the oppurtunity to pass on her lessons to
another aspiring student. We need more engineers like her in the world,
and I want to help create that future.

## Advice for future mentors

Mentoring is not for everyone. It\'s not a task which you can just send
a couple of emails and be done every day.

Mentoring is a process that requires engagement with the student, and
communication and the relationship is key to this. What worked well was
meeting early in the project, and working out what community worked best
for us. We found that email questions and responses worked (given we are
on nearly opposite sides of the Earth) worked well, along with irc
conversations to help fix up any other questions. It would not be
uncommon for me to spend at least 1 or 2 hours a day working through
emails from Ilias and discussions on IRC.

A really important aspect of this communication is how you do it. You
have to balance positive communication and encouragement, along with
critcism that is constructive and helpful. Empathy is a super important
part of this equation.

My number one piece of advice would be that you need to create an
environment where questions are encouraged and welcome. You can never be
dismissive of questions. If ever you dismiss a question as \"silly\" or
\"dumb\", you will hinder a student from wanting to ask more questions.
If you can\'t answer the question immediately, send a response saying
\"hey I know this is important, but I\'m really busy, I\'ll answer you
as soon as I can\".

Over time you can use these questions to help teach lessons for the
student to make their own discoveries. For example, when Ilias would ask
how something worked, I would send my response structured in the way I
approached the problem. I would send back links to code, my thoughts,
and how I arrived at the conclusion. This not only answered the question
but gave a subtle lesson in how to research our codebase to arrive at
your own solutions. After a few of these emails, I\'m sure that Ilias
has now become self sufficent in his research of the code base.

Another valuable skill is that overtime you can help to build confidence
through these questions. To start with Ilias would ask \"how to
implement\" something, and I would answer. Over time, he would start to
provide ideas on how to implement a solution, and I would say \"X is the
right one\". As time went on I started to answer his question with
\"What do you think is the right solution and why?\". These exchanges
and justifications have (I hope) helped him to become more confident in
his ideas, the presentation of them, and justification of his solutions.
It\'s led to this [excellent
exchange](https://lists.fedoraproject.org/archives/list/389-devel@lists.fedoraproject.org/thread/5VDPWUZ3E67UMEWVCATU6LEIQ5QGBGEM/)
on our mailing lists, where Ilias is discussing the solutions to a
problem with the broader community, and working to a really great
answer.

## Final thoughts

This has been a great experience for myself and Ilias, and I really look
forward to helping another student next year. I\'m sure that Ilias will
go on to do great things, and I\'m happy to have been part of his
journey.

