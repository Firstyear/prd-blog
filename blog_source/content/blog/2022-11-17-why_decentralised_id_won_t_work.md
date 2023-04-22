+++
title = "Why Decentralised ID Won't Work"
date = 2022-11-17
slug = "2022-11-17-why_decentralised_id_won_t_work"
# This is relative to the root!
aliases = [ "2022/11/17/why_decentralised_id_won_t_work.html", "blog/html/2022/11/17/why_decentralised_id_won_t_work.html" ]
+++
# Why Decentralised ID Won\'t Work

Thanks to a number of [high
profile](https://www.abc.net.au/news/2022-09-27/optus-data-breach-cyber-attack-hacker-ransom-sorry/101476316)
and damaging [security
incidents](https://www.abc.net.au/news/2022-11-09/medibank-data-release-dark-web-hackers/101632088)
in Australia people have once again been discussing Decentralised ID
(DID). As someone who has spent most of the career working on identity
management, I\'m here to tell you why *it will not work*.

## What Is Decentralised ID Trying To Do?

To understand what DID is trying to achieve we have to look at what a
\"centralised\" system is doing.

Lets consider an account holder like Google. You create an account with
them, and you store your name and some personal data, as well as a
method of authentication, such as a password and OTP, or Webauthn.

Now you go to some other website and it says \"login with Google\". That
site redirects to Google, who authenticates you, and then the website
trusts Google to say \"yes or no\" that \"you are who you say you are\".
You can consent to this website seeing details about you like an email
address or name.

A decentralised system works differently. You present a signed metadata
statement about yourself to the website, and that cryptograhic signature
can be traced back to your signing private key. This cryptograhic proof
attests that you are the profile/account holder.

## What Does DID Claim To Achieve?

-   That you are the only authority who can modify your own identity and
    data.
-   You control who can access (view) that data.
-   Cryptographic verification that an identity is who they claim to be.

## This Will Never Work

### No Consideration Of Human Behaviour

DID systems do not consider human behaviour in their design.

I can not put it better, than [Don Norman, in his paper \"The Truth
about
Unix\"](https://bradleymonk.com/w/images/9/91/The_truth_about_Unix_Don_Norman.pdf).

*System designers take note. Design the system for the person, not for
the computer, not even for yourself. People are also information
processing systems, with varying degrees of knowledge, varying degrees
of experience. Friendly systems treat users as intelligent adults who,
like normal adults, are forgetful, distracted, thinking of other things,
and not quite as knowledgeable about the world as they themselves would
like to be.*

People are not \"stupid\". They are distracted and busy. This means they
will lose their keys. They will be affected by [events out of their
control](https://www.abc.net.au/news/2022-02-28/qld-flood-brisbane-residents-assess-damage/100869034).

In a centralised system there are ways to recover your account when you
lose your password/keys. There are systems to verify you, and help you
restore from damage.

In a DID system, if you lose your key, you lose everything. There is no
recovery process.

### GPG Already Failed

DID is effectively a modern rehash of GPG - including it\'s problems.
[Many others
have](https://latacora.micro.blog/2019/07/16/the-pgp-problem.html)
lamented [at length
about](https://words.filippo.io/giving-up-on-long-term-pgp/). These
people have spent their lives studying cryptograhpic systems, and they
have given up on it. Pretty much every issue they report here, applies
to DID and all it\'s topics.

### Long Term Keys

One of the biggest issues in DID is that the identity is rooted in a
private key that is held by an individual. This encourages long-term
keys, which have a large blast radius (complete take over of your
identity). This causes dramatic failure modes. To further this, it also
prevents improvement of the cryptograhic quality of the key. When I
started in IT RSA 1024 bit was secure. Now it\'s not. Keys need to be
short lived and disposable.

### You Won\'t Own Your Own Data

When you send a DID signed document to a provider, lets say your Bank to
open a new account, what do you think they will do with that data?

They won\'t destroy it and ask you for it every time you need it. They
will store a copy on their servers for their records. There are often
*extremely good reasons* they need to store that data as well.

Which means that your signed document of data is performative, and the
data will just be used and extracted as usual.

DID does not solve the problem of data locality or retention. Regulation
and oversight does.

### Trust Is A Social Problem

You can\'t solve social problems with technology.

The whole point of DID is about solving *trust*. Who do you *trust* to
store (modify) or view your personal information?

In a DID world, you need to be \"your own personal central data
authority\" (because apparently you can\'t trust anyone else). That
means you need to store your data, protect it from destruction and
secure it from compromise.

In the current world, for all of Google\'s and many other companies
flaws, they still have dedicated security teams, specialists in risk
analysis, and people who have dedicated themselves to protecting your
accounts and your data.

The problem is that most software engineers fall into the fallacy that
because they are an expert in their subject matter, they are now an
expert on identity and computer security. They are likely not security
experts (the same people love to mansplain authentication to me
frequently, and generally this only serves to inform me that they
actually do not understand authentication).

Why should anyone trust your DID account, when you likely have no data
hygiene and insecure key storage? Why should a Bank? Why should Google?
Your workplace? No one has a reason to trust you and your signatures.

Yes there are problems with centralised identity systems - but DID does
not address them, and actually may make them significantly worse.

### Your Verification Mark Means Nothing

Some DID sites claim things like \"being able to prove ownership of an
account\".

How does this proof work? Can people outside of the DID community
explain these proofs? Can your accountant? You Taxi driver?

What this will boil down to a green tick that people will trust. It
doesn\'t take a lot of expertise to realise that the source code for
this tick can be faked pretty easily since it\'s simply a boolean check.

These verification marks come back to \"trust\", which DID does not
solve. You need to *trust* the site you are viewing to render things in
a certain way, the same way you have to *trust* them not to go and
impersonate you.

Even if you made a DID private key with ED25519 and signed some toots,
Mastodon instance owners could still impersonate you if they wanted.

And to further this, how is the average person expected to verify your
signatures? HTTPS has already shown that the majority of the public does
not have the specific indepth knowledge to assess the legitimacy of a
certificate authority. How are we expecting people to now verify every
other person as their own CA?

The concept of web of trust is a performative act.

Even [XKCD nailed this](https://xkcd.com/1181/).

## Conclusion

DID won\'t work.

There are certainly issues with central authorities, and DID solves none
of them.

It is similar to [bootstraping
compilers](/blog/html/2021/05/12/compiler_bootstrapping_can_we_trust_rust.html).
It is a problem that is easy to articulate, emotionally catchy, requires
widespread boring social solutions, but tech bros try to solve it
unendingly with hyper-complex-technical solutions that won\'t work.

You\'re better off just adding FIDO2 keys to your accounts and moving
on.

