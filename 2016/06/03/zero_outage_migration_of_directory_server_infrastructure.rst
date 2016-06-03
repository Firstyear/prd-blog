Zero Outage Migration Of Directory Server Infrastructure
========================================================

In my previous job I used to manage the Directory Servers for a University. People used to challenge me that while doing migrations, downtime was needed.

*They are all wrong*

It is very possible, and achievable to have zero outage migrations of Directory Servers. All it takes is some thought, planning, dedication and testing.

What will I need?
-----------------

* A basic understanding of DNS
* Some Directory Servers
* Probably a load balancer

If you don't have a load balancer, you should be asking yourself:

*Why don't I have a load balancer?*

The only answer I'll accept here, is that you are using ldap SRV records. If that's the case, some of these migrations are even easier.

What SHOULDN'T I do?
--------------------

Let's get this out the way. I've seen some pretty rough migration plans. Here are some "don'ts".

* DO NOT replace your hardware / virtual machines by downing the old machine, and bring up the new machine with the same IP and dns name.
* DO NOT think you can setup a new DS instance inside your change window and just magically replicate data into it. WITHOUT fail, you *will* mess this up, and something will break.

What SHOULD I do?
-----------------

* DO use CNAMEs. Lets have an example.

If I have directory server ldap01 and ldap02. There should NOT be A/AAAA records to my hosts. IE

::

    ldap01 IN A 10.0.0.1
    ldap02 IN A 10.0.0.2

Use cnames!

::

    ldap-private-a IN A 10.0.0.1
    ldap-private-b IN A 10.0.0.2
    ldap01 IN CNAME ldap-private-a
    ldap02 IN CNAME ldap-private-b

Why use cnames? Watch.

::

    ldap-private-a IN A 10.0.0.1
    ldap-private-b IN A 10.0.0.2
    ldap-private-c IN A 10.0.0.2
    ldap01 IN CNAME ldap-private-a
    ldap02 IN CNAME ldap-private-c

See how you replaced ldap02 with private-c with two record changes? You also can maintain your replication agreements without horrible renaming or changes to your DNS. You can then gradually, slowly, and controlled make changes with the ability to carefully and continually assess.

* DO use a load balancer.

Similar to the above with DNS, if you have:

::

         loadbalancer (ldap01)
       /       |
      /        |
   Host A    Host B

Now you can add a third machine:

::

         loadbalancer (ldap01)
       /       |       
      /        |        
   Host A    Host B    Host C

You can add all the replication agreements between A, B, C. Then when you are ready, pop it into the load balancer

::

         loadbalancer (ldap01)
       /       |       \
      /        |        \
   Host A    Host B    Host C

If something goes bad, you can just pull it immediately out. Easy as that!


* DO understand what a DNS TTL does.

You will see records like this in DNS

::

    ldap01 IN A 86400 10.0.0.1

The most important part here is the 86400. This is the TTL, the Time To Live. When a client queries this name, they are allowed to cache it for that many seconds before they have to refresh! In other words a client of ldap01 will only need to resolve the name once a day!

We can use this property to make changes ahead of a migration to enable us some flexibility.

::

    ldap01 IN A 300 10.0.0.1

This is now a 5 minute TTL, instead of a 1 day one as above. So every 5 minutes the client will "re-check" the name.


* DO setup your new Directory Server machines in Parallel to the existing infrastructure.

This is SUPER important. This allows you to test data imports, data validation, backups, SSL, TLS, replication .... basically, the whole thing. Before you even get *near* a change window, your new infrastructure should be established in parallel, and should be production like, heavily validated and tested. Without all of this due diligence and work, how are you meant to make sure that what you are upgrading to is even correct?


* DO test everything all the time.

Have a staging environment, and test everything. Test upgrades. Downgrades. Roll backs, restores. Make sure you know the system inside out. By the time you come to the real upgrade, it should be possible to do it in your sleep.

* DO engage other parts of your business or IT to ensure they test your new infrastructure.

Everything single business unit should have tested the new server, and signed off acknowledgement proceeding. Because of this process (which can take a month or more) many issues were solved. It make take time, but when you do the upgrade, you can be confident every applciation will work.

As well, resolving issues in DEV is not time critical, finance critical or anything else. You have time to research, test, and validate fixes. Work with other teams, and your upgrade will be smooth as silk.

* DO Document everything you do.

On your DEV environment copy all your commands and ldifs you apply.

Then, use that document, apply them to your stage environment. If they need changing, additions, etc, apply them.

Repeat the run through until you don't need to change anything at all anymore.

Now you literally have a "copy paste" guide to apply to your production infrastructure that is so good, you don't even need to research or panic. You have seen all the edge cases, you have the documented, you know what you need to do. You will love yourself for ever if you do this.

How would you do a migration?
-----------------------------

You need to assess all of your current infrastructure. You must plan what your new infrastructure will look like, and you must understand the ways that clients connect to that infrastructure. Are there hardcoded IPs? DNS names? What is your replication like?

Once you have assessed this, we'll make a mock scenario like one that I had. We were migrating from our old load balancer to the new load balancer, and adding some more servers.

Before:

::

          Old LB
         /     \
    Host A     Host B

After:

::

         /-----New LB-----\
        /      |    |      \
       /       |    |       \
    Host A  Host B  Host C  Host D

This plan was carried out in DEV, UAT, and PRD. But the steps were the same.

THIS SECTION IS ALL DONE BEFORE A CHANGE WINDOW.

First, build all the new servers we are adding. Your network should look like this.

::

          Old LB
         /     \
    Host A     Host B

    Host C     Host D

          New LB (un connected)

Join C and D into a replication agreement. Load a production backup into them. Test everything. TLS, SSL, changing data, load test them. Everything. Make sure C and D and ready.

Next, we want to join Host C and D to the new load balancer. This way we can test the new load balancer is ready, and configured correctly. This includes having other teams and users validate the new environment for functionality and correctness.

Your system should look like this:

::


          Old LB
         /     \
    Host A     Host B

         New LB----\
             |      \
             |       \
             Host C  Host D


Now, we want to find *all* our DNS records. We had:

::

    ldap01 IN A 86400 <Old LB IP>
    ldap02 IN CNAME 86400 ldap01

Drop the TTL on the ldap01 record, which is what all your clients connect to.

::

    ldap01 IN A 300 <Old LB IP>
    ldap02 IN CNAME 86400 ldap01


You must wait for the ZONE ttl to expire as well to be sure of these change. Basically, leave it ttl x 2 to be safe. (IE 2 days)


You are now ready to migrate. The New LB is a production replica, is well tested, you have replication between C and D working, and it's all great.

DURING YOUR CHANGE WINDOW

Now the fun begins!

First, connect *all* of our Directory Servers to the same replication group. A, B, C, D should all be replicating now.

Complete a full initialisation from A *or* B to C *and* D. This must be done so that the data in C and D is correct, and can be replicated.

Now, change your DNS records for ldap01.

::

    ldap01 IN A 300 <New LB Ip>
    ldap02 IN CNAME 86400 ldap01

Wait ttl * 2, IE 10 minutes. During this time, most clients dns caches will expire ldap01, and they will gradually begin to connect to and consume the New LB. If there are issues, you can revert to the Old LB ip for ldap01. The maximum outage window possible here is 5 minutes in an error case. But that's why you have tested and made the new env previously, and tested everything in your business against it right!


Once you know the DNS ttl has expired, and you are seeing traffic on the New LB, shutdown the Old LB. This will force the remaining connected clients to start to move to the New LB. Ldap is pretty good for reconnection, so don't expect any outages as a result of this.

THIS IS THE DECISION POINT. If there are issues, now is the time to roll back. If everything is working continue. Sometimes you need to leave this for say 30 minutes to really see what's going on. Coordinate with application teams and other business units to make sure everything is working correctly!

Once you have decided to COMMIT to finishing this, you should now move the remaining two hosts to the new LB.

At this stage your network is this:

::

          Old LB
              
    Host A     Host B

         New LB----\
             |      \
             |       \
             Host C  Host D

The final step to complete the migration is to add Host A and Host B to the new LB.

::

            Old LB 


         /-----New LB-----\
        /      |    |      \
       /       |    |       \
    Host A  Host B  Host C  Host D

That's it!

Once you leave this to settle for a day or so, you can turn your DNS TTLs back up to their previous value.

Well done, you moved production ldap servers without no outage.


But my network is different?
----------------------------

Many of these ideas transfer. If you are adding new hardware and want to decom old hardware, just don't move the old systems to the new load balancer.

If you rely on DNS, just change A/AAAA to cnames, then use the TTL changes to make the move.

If you want to do inplace upgrades, use the load balancer to pull machines in and out of service to validate.

If you are stuck on certain IP's, instead of making that IP the primary on the system, use vlans. Have your front ends on one vlan with the "unchanging" IP, and add a second VLAN with internal DNS names for replication. Then you can just up/down interfaces as needed on your hosts.

There are so many variants you can use here, but the main thing is to know that changing the DNS TTL is really important, and can allow you to make many changes otherwise possible.

It takes planning, thought, coordination and discipline to make a change like this, to critical business infrastructure. Not only is this possible, but *I have made changes like this*. The exact migration above, was done, with no outage at a large business serving thousands of users simultaneously. Not a single service desk issue was raised during the process.


If you want some advice on *your* migration, feel free to drop me an email.



.. author:: default
.. categories:: none
.. tags:: none
.. comments::
