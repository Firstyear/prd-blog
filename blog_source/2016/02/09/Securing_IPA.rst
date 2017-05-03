Securing IPA
============
By default IPA has some weak security around TLS and anonymous binds.

We can improve this by changing the following options.

::
    
    nsslapd-minssf-exclude-rootdse: on
    nsslapd-minssf: 56
    nsslapd-require-secure-binds: on
    

The last one you may want to change is:

::
    
    nsslapd-allow-anonymous-access: on
    

I think this is important to have on, as it allows non-domain members to use ipa, but there are arguments to disabling anon reads too. 
