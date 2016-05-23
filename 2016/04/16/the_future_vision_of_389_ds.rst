The future vision of 389-ds
===========================

Disclaimer: This is my vision and analysis of 389-ds and it's future. It is nothing about Red Hat's future plans or goals. Like all predictions, they may not even come true.

As I have said before I'm part of the 389-ds core team. I really do have a passion for authentication and identity management: I'm sure some of my friends would like to tell me to shut up about it sometimes.

389-ds, or rather, ns-slapd has a lot of history. Originally from the umich code base, it has moved through Netscape, SUN, Aol and, finally to Red Hat. It's quite something to find myself working on code that was written in 1996. In 1996 I was on a playground in Primary School, where my biggest life concerns was if I could see the next episode of [anime of choice] the next day at before school care. What I'm saying, is ns-slapd is old. Very old. There are many dark, untrodden paths in that code base.

You would get your nice big iron machine from SUN, you would setup the ns-slapd instance once. You would then probably setup one other ns-slapd master, then you would run them in production for the next 4 to 5 years with minimal changes. Business policy would ask developers to integrate with the LDAP server. Everything was great.

But it's not 1996 anymore. I have managed to complete schooling and acquire a degree in this time. ns-slapd has had many improvements, but the work flow and way that ns-slapd in managed really hasn't changed a lot.

While ns-slapd has stayed roughly the same, the world has evolved. We now have latte sipping code hipsters, sitting in trendy Melbourne cafes programming in go and whatever js framework of this week. They deploy to AWS, to GCE. (But not Azure, that's not cool enough). These developers have a certain mindset and the benefits of centralised business authentication isn't one of them. They want to push things to cloud, but no system administrator would let a corporate LDAP be avaliable on the internet. CIO's are all drinking the "cloud" "disruption" kool aid. The future of many technologies is certainly in question.

To me, there is no doubt that ns-slapd is still a great technology: Like the unix philosohpy, tools should do "one thing" and "one thing well". When it comes to secure authentication, user identification, and authorisation, LDAP is still king. So why are people not deploying it in their new fancy containers and cloud disruption train that they are all aboard?

ns-slapd is old. Our systems and installers, such as setup-ds.pl are really designed for the "pet" mentality of servers. They are hard to automate to replica groups, and they inist on having certain types of information avaliable before they can run. They also don't work with automation, and are unable to accept certain types of ldifs as part of the inf file that drives the install. You have to have at least a few years experience with ns-slapd before you could probably get this process "right".

Another, well, LDAP is ... well, hard. It's not json (which is apparently the only thing developers understand now). Developers also don't care about identifying users. That's just not *cool*. Why would we try and use some "hard" LDAP system, when I can just keep some json in a mongodb that tracks your password and groups you are in?

So what can we do? Where do I see 389-ds going in the future?

- We need to modernise our tooling, and installers. It needs to be easier than ever to setup an LDAP instance. Our administration needs to move away from applying ldifs, into robust, command line tools.

- Setting up replication groups and masters needs to be simpler. Replication topologies should be "self managing" (to an extent). Ie I should say "here is a new ldap server, join this replication group". The administration layer then determines all the needed replication agreements for robust and avaliable service.

- We need to get away from long lived static masters, and be able to have rapidly deployed, and destroyed, masters. With the changes above, this will lend itself to faster and easier deployment into containers and other such systems.

- During updates, we need to start to enable smarter choices by default: but still allow people to fix their systems on certain configurations to guarantee stability. For example, we add new options and improvements to DS all the time: but we cannot always enable them by default. This makes our system look dated, when really a few configurations would really modernise and help improve deployments. Having mechanisms to push the updates to clients who want it, and enable them by default on new installs will go a long way.

- Out of the box we need smarter settings: The *default* install should need almost *no changes* to be a strong, working LDAP system. It should not require massive changes or huge amounts of indepth knowledge to deploy. I'm the LDAP expert: You're the coffee sipping developer. You should be able to trust the defaults we give you, and know that they will be well engineered and carefully considered.

- Finally I think what is also going to be really important is Web Based authentication. We need to provide ways to setup and provision SAML and OAuth systems that "just work" with our LDAP. With improvements on the way like `this draft rfc <https://tools.ietf.org/html/draft-wibrown-ldapssotoken-00>`_ will even allow fail over between token systems, backed by the high security and performance guarantees of LDAP.

This is my vision of the future for 389-ds: Simplification of setup. Polish of the configuration. Ability to automate and tools to empower administrators. Integration with what developers want.


Lets see how much myself and the team can achieve by the end of 2016.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
