Disabling journald support
==========================

Some people may have noticed that there is a feature open for Directory Server to support journald.

As of April 13th, we have decided to disable support for this in Directory Server.

This isn't because anyone necesarrily hates or dislikes systemd. All too often people discount systemd due to a hate reflex.

This decision came about due to known, hard, technical limitations of journald. This is not hand waving opinion, this is based on testing, numbers, business requirements and experience.


So lets step back for a second. Directory Server is an LDAP server. On a network, LDAP is deployed typically to be responsible for authentication and authorisation of users to services. This is a highly security sensitive role. This leads to an important facet of security being auditability. For example, the need to track when and who has authenticated to a network. The ability to audit what permisions were requested and granted. Further more, the ability to audit and identify *changes* to Directory Server data which may represent a compromise or change of user credential or authorisation rights.

Being able to audit these is of vital importance, from small buisinesses to large enterprise. As a security system, this audit trail must have guarantees of *correctness* and *avaliablility*. Often a business will have internal rules around the length of time auditing information must be retained for. In other businesses there are legal requirements for auditing information to be retained for long periods. Often a business will keep in excess of 2 weeks of authentication and authorisation data for the purposes of auditing.

Directory Server provides this auditing capability through it's logging functions. Directory Server is configured to produce 3 log types.

* errors - Contains Directory Server operations, plugin data, changes. This is used by administrators to identify service behaviour and issues.
* access - Contains a log of all search and bind (authentication) operations.
* audit - Contains a log of all modifications, additions and deletions of objects within the Directory Server.

For the purpose of auditing in a security context the access and audit logs are of vital importance, as is their retention times.


So why is journald not fit for purpose in this context? It seems to be fine for many other systems?

Out of the box, journald has a *hardcoded* limit on the maximum capacity of logs. This is 4GB of on disk capacity. Once this is exceeded, the journal rotates, and begins to overwrite entries at the beginging of the log. Think circular buffer. After testing and identifying the behaviours of Directory Server, and the size of journald messages, I determined that a medium to large site will cause the journal to begin a rotation in 3 hours or less during high traffic periods.

3 hours is a far smaller number than the "weeks" of retention that is required for auditing purposes of most businesses.


Additionally, by default journald is configured to drop events if they enter the log to rapidly. This is a "performance" enhancement. However, during my tests I found that 85% of Directory Server events were being dropped. This violates the need for correct and complete audit logs in a security system.

This *can* be reconfigured, but the question should be asked. Why are log events dropped at all? On a system, log events are the basis of auditing and accountability, forming a historical account of evidence for an Administrator or Security personel to trace in the event of an incident. Dropping events from Directory Server *is unacceptable*. As I stated, this can be reconfigured.

But it does begin to expose the third point. Performance. Journald is slow, and caused an increase of 15% cpu and higher IO on my testing environments. For a system such as Directory Server, this overhead is unacceptable. We consider performance impacts of 2% to be signifigant: We cannot accept 15%.


As an API journald is quite nice, and has many useful features. However, we as a team cannot support journald with these three limitations above.

If journald support is to be taken seriously by security and performance sensitive applications the following changes are recomended.

* Remove the 4G log size limit. It can either be configurable by a user, or there should be no limits.
* Log events should either not be dropped by default, or a method to have per systemd unit file overrides to prevent dropping of certain services events should be added.
* The performance of journald should be improved as to reduce the impact upon applications consuming the journald api.

I hope that this explains why we have decided to remove systemd's journald support from Directory Server at this time.


Before I am asked: No I will not reverse my stance on this matter, and I will continue to advise my team of the same. Systemd needs to come to the table and improve their api before we can consider it for use.


The upstream issue can be seen here `389 ds trac 47968 <https://fedorahosted.org/389/ticket/47968>`_. All of my calculations are in this thread too.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
