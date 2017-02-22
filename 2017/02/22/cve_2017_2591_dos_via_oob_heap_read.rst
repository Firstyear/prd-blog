CVE-2017-2591 - DoS via OOB heap read
=====================================

On 18 of Jan 2017, the following `email found it's way to my notifications <http://seclists.org/oss-sec/2017/q1/129>`_ .

::

    This is to disclose the following CVE:

    CVE-2017-2591 389 Directory Server: DoS via OOB heap read

    Description :

    The "attribute uniqueness" plugin did not properly NULL-terminate an array
    when building up its configuration, if a so called 'old-style'
    configuration, was being used (Using nsslapd-pluginarg<X> parameters) .

    A attacker, authenticated, but possibly also unauthenticated, could
    possibly force the plugin to read beyond allocated memory and trigger a
    segfault.

    The crash could also possibly be triggered accidentally.

    Upstream patch :
    https://fedorahosted.org/389/changeset/ffda694dd622b31277da07be76d3469fad86150f/
    Affected versions : from 1.3.4.0

    Fixed version : 1.3.6

    Impact: Low
    CVSS3 scoring : 3.7 -- CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:L

    Upstream bug report : https://fedorahosted.org/389/ticket/48986

So I decided to pull this apart: Given I found the issue and wrote the fix, I didn't deem it security worthy, so why was a CVE raised?

.. more::

The bug
-------

The bug was a `simple overflow <https://pagure.io/389-ds-base/issue/48986>`_ I found while running Directory Server with address sanitisation enabled. I find and fix these quite regularly, so why was this turned up as a CVE?

In order to see this, we need to look into the `uiduniq code <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c>`_ .

Analysis
--------

Our issue starts here when we create `the buffer <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c#_305>`_ .

::

        /* Store attrName in the config */
        tmp_config->attrs = (const char **) slapi_ch_calloc(1, sizeof(char *));
        tmp_config->attrs[0] = slapi_ch_strdup(attrName);
        argc--;
        argv++; /* First argument was attribute name and remaining are subtrees */


tmp_config->attrs is an array of strings, where the last element of the array should be NULL. How do we know this? `This check <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c#_376>`_ which copies the attributes out for "friendly debugging".

::

        for (i = 0; tmp_config->attrs && (tmp_config->attrs)[i]; i++) {
            strcpy(fp, (tmp_config->attrs)[i] );
            fp += strlen((tmp_config->attrs)[i]);
            strcpy(fp, " ");
            fp++;
        }

This means that because tmp_config->attrs is only of size [1], not [2], there is no NULL element at the end. As a result, the `loop to build <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c#_376>`_ is going to keep running adding more data past the end into tmp_config->attr_friendly.

This is not so dangerous, because the buffer for tmp_config->attr_friendly is correctly sized: We `already checked <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c#_370>`_ how big the "overrun" is, so the buffer for attr_friendly will be able to accomodate the leaked information.

::

        /* If the config is valid, prepare the friendly string for error messages */
        for (i = 0; tmp_config->attrs && (tmp_config->attrs)[i]; i++) {
            attrLen += strlen((tmp_config->attrs)[i]) + 1;
        }
        tmp_config->attr_friendly = (char *) slapi_ch_calloc(attrLen + 1, sizeof(char));
        fp = tmp_config->attr_friendly;

Right, so we have our buffer of memory that's being leaked. To trigger the actual disclosure to the client, we need to cause a LDAP_CONSTRAINT_VIOLATION (by adding a duplicated attribute to an object which matches this configuration). At this point the `bytes are now sent <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c#_1058>`_ in the error message to the client.

So what's the catch here?

The buffer overrun is only run *once*. The function affected is `uniqueness_attr_to_config <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c#_160>`_ which is only called *once* at `plugin start up <https://pagure.io/389-ds-base/blob/04a9c896a99be843e531f989352f39687518c4e8/f/ldap/servers/plugins/uiduniq/uid.c#_1407>`_

::

    static int
    uiduniq_start(Slapi_PBlock *pb)
    {
        Slapi_Entry *plugin_entry = NULL;
        struct attr_uniqueness_config *config = NULL;
        if (slapi_pblock_get(pb, SLAPI_ADD_ENTRY, &plugin_entry) == 0){
            /* load the config into the config list */
            if ((config = uniqueness_entry_to_config(pb, plugin_entry)) == NULL) {
                return SLAPI_PLUGIN_FAILURE;
            }
            slapi_pblock_set(pb, SLAPI_PLUGIN_PRIVATE, (void*) config);
        }
        return 0;
    }

The fix
-------

Simply make the `buffer bigger <https://pagure.io/389-ds-base/issue/raw/files/9b9e42bf9bb69d0f4265a918f433078bbf20322bc20bde65874e6f97bab0316d-0001-Ticket-48986-47808-triggers-overflow-in-uiduniq.c.patch>`_ to accomodate the required NULL byte at the end to terminate the array loop

::

    tmp_config->attrs = (const char **) slapi_ch_calloc(2, sizeof(char *));

So what do you think?
---------------------

This CVE is not actually very dangerous at all. It relies on:

* Having the ability to trigger a uniqueness violation (most users in a Directory have no rights)
* The administrator using a deprecated configuration style
* Restarting the Directory Server instance to actually get more bytes
* OR being the cn=Directory Manager (root) user and enabling/disabling the plugin repeatedly

So why was it raised at all? Well my original `bug report <https://pagure.io/389-ds-base/issue/48986>`_ has lots of scary words like *heap-buffer-overflow* and *trigger* and *ERROR*. As a result, someone trawling the bug tracker saw this and took a cheap shot: They never actually did the analysis of the execution path to determine that in most cases you *leak no data to a client anyway*. They classified it as a "Denial Of Service" (The server does not crash). They did not analyse the access vectors "A attacker, authenticated, but possibly also unauthenticated, could possibly force the plugin to read beyond allocated memory and trigger a segfault.". This is incorrect, you must be authenticated, and you can not force the plugin to read beyond the memory: The memory was read at startup, so you keep retrieving the same bytes!

Finally, in most cases no bytes are leaked anyway due to the layout of the memory in the plugin and the allocation series.

There was a lot of noise for something that is not even a really dangerous issue!

Conclusion
----------

Always investigate an issue thoroughly, and with care, to give the proper analysis and reasoning as to how a vulnerability is exploitable.

Always engage the developers of the software: They know it better than you, and can help guide your analysis. Don't just drop public CVE's without consultation!


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
