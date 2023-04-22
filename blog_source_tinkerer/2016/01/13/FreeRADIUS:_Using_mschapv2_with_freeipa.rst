FreeRADIUS: Using mschapv2 with freeipa
=======================================

`I no longer recommend using FreeIPA - Read more here! </blog/html/2019/07/10/i_no_longer_recommend_freeipa.html>`_

Wireless and radius is pretty much useless without mschapv2 and peap. This is because iPhones, androids, even linux have fundamental issues with ttls or other 802.1x modes. mschapv2 "just works", yet it's one of the most obscure to get working in some cases without AD.

If you have an active directory environment, it's pretty well a painless process. But when you want to use anything else, you are in a tight spot.

The FreeRADIUS team go on *a lot* about how mschapv2 doesn't work with ldap: and they are correct. mschapv2 is a challenge response protocol, and you can't do that in conjunction with an ldap bind. 

However it *IS* possible to use mschapv2 with an ldap server: It's just not obvious or straight forwards.

The way that this works is you need freeradius to look up a user to an ldap dn, then you read (not bind) the nthash of the user from their dn. From there, the FreeRADIUS server is able to conduct the challenge response component.

So the main things here to note:

* nthash are pretty much an md4. They are broken and terrible. But you need to use them, so you need to secure the access to these.
* Because you need to secure these, you need to be sure your access controls are correct.

We can pretty easily make this setup work with freeipa in fact.

First, follow the contents of `my previous blog post </blog/html/2015/07/06/FreeIPA:_Giving_permissions_to_service_accounts..html>`_ on how to setup the adtrust components and the access controls. 

You don't actually need to complete the trust with AD, you just need to run the setup util, as this triggers IPA to generate and store nthashes in ipaNTHash on the user account.

Now armed with your service account that can read these hashes, and the password, we need to configure FreeRADIUS.


FreeRADIUS is EXTREMELY HARD TO CONFIGURE. You can mess it up VERY QUICKLY.

Thankfully, the developers provide an excellent default configuration that should only need minimal tweaks to make this configuration work.

first, symlink ldap to mods-enabled

::
    
    cd /etc/raddb/mods-enabled
    ln -s ../mods-available/ldap ./ldap
    

Now, edit the ldap config in mods-available (That way if a swap file is made, it's not put into mods-enabled where it may do damage)

You need to change the parameters to match your site, however the most important setting is:

::
    
    
        identity = krbprincipalname=radius/host.ipa.example.net.au@IPA.EXAMPLE.NET.AU,cn=services,cn=accounts,dc=ipa,dc=example,dc=net,dc=au
        password = SERVICE ACCOUNT BIND PW
    
        ....snip.....
    
        update {
              ....snip......
              control:NT-Password··   := 'ipaNTHash'
        }
    
         .....snip ....
    
        user {
               base_dn = "cn=users,cn=accounts,dc=ipa,dc=example,dc=net,dc=au"
               filter = "(uid=%{%{Stripped-User-Name}:-%{User-Name}})"
                ....snip....
        }
    

Next, you want to edit the mods-available/eap 

you want to change the value of default_eap_type to:

::
    
        default_eap_type = mschapv2
    

Finally, you need to update your sites-available, most likely inner-tunnel and default to make sure that they contain:

::
    
    authorize {
    
          ....snip .....
          -ldap
    
    }
    

That's it! Now you should be able to test an ldap account with radtest, using the default NAS configured in /etc/raddb/clients.conf.

::
    
    radtest -t mschap william password 127.0.0.1:1812 0 testing123
    	User-Name = 'william'
    	NAS-IP-Address = 172.24.16.13
    	NAS-Port = 0
    	Message-Authenticator = 0x00
    	MS-CHAP-Challenge = 0x642690f62148e238
            MS-CHAP-Response = ....
    Received Access-Accept Id 130 from 127.0.0.1:1812 to 127.0.0.1:56617 length 84
    	MS-CHAP-MPPE-Keys = 0x
    	MS-MPPE-Encryption-Policy = Encryption-Allowed
    	MS-MPPE-Encryption-Types = RC4-40or128-bit-Allowed
    
Why not use KRB?
----------------

I was asked in IRC about using KRB keytabs for authenticating the service account. Now the configuration is quite easy - but I won't put it hear.

The issue is that it opens up a number of weaknesses. Between FreeRADIUS and LDAP you have communication. Now FreeIPA/389DS doesn't allow GSSAPI over LDAPS/StartTLS. When you are 
doing an MSCHAPv2 authentication this isn't so bad: FreeRADIUS authenticates with GSSAPI with encryption layers, then reads the NTHash. The NTHash is used inside FreeRADIUS to 
generate the challenge, and the 802.1x authentication suceeds or fails.

Now what happens when we use PAP instead? FreeRADIUS can either read the NTHash and do a comparison (as above), or it can *directly bind* to the LDAP server. This means in the direct 
bind case, that the transport *may not be encrypted* due to the keytab. See, the keytab when used for the service account, will install encryption, but when the simple bind occurs, 
we don't have GSSAPI material, so we would send this clear text. 

Which one will occur ... Who knows! FreeRADIUS is a complex piece of software, as is LDAP. Unless you are willing to test all the different possibilities of 802.1x types and LDAP 
interactions, there is a risk here.

Today the only secure, guaranteed way to protect your accounts is TLS. You should use LDAPS, and this guarantees all communication will be secure. It's simpler, faster, and better.

That's why I don't document or advise how to use krb keytabs with this configuration.


Thanks to *moep* for helping point out some of the issues with KRB integration.

