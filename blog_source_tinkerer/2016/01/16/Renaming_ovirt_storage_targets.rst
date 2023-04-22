Renaming ovirt storage targets
==============================
I run an ovirt server, and sometimes like a tinker that I am, I like to rename things due to new hardware or other ideas that come up.

Ovirt makes it quite hard to change the nfs target or name of a storage volume. Although it's not supported, I'm more than happy to dig through the database.

NOTE: Take a backup before you start, this is some serious unsupported magic here.

First, we need to look at the main tables that are involved in nfs storage:

::
    
    engine=# select id,storage,storage_name from storage_domain_static;
                      id                  |               storage                |   storage_name    
    --------------------------------------+--------------------------------------+-------------------
     6bffd537-badb-43c9-91b2-a922cf847533 | 842add9e-ffef-44d9-bf6d-4f8231b375eb | def_t2_nfs_import
     c3aa02d8-02fd-4a16-bfe6-59f9348a0b1e | 5b8ba182-7d05-44e4-9d64-2a1bb529b797 | def_t2_nfs_iso
     a8ac8bd0-cf40-45ae-9f39-b376c16b7fec | d2fd5e4b-c3de-4829-9f4a-d56246f5454b | def_t2_nfs_lcs
     d719e5f2-f59d-434d-863e-3c9c31e4c02f | e2ba769c-e5a3-4652-b75d-b68959369b55 | def_t1_nfs_master
     a085aca5-112c-49bf-aa91-fbf59e8bde0b | f5be3009-4c84-4d59-9cfe-a1bcedac4038 | def_t1_nfs_sas
    
    engine=# select id,connection from storage_server_connections;
                      id                  |                           connection                            
    --------------------------------------+-----------------------------------------------------------------
     842add9e-ffef-44d9-bf6d-4f8231b375eb | mion.ipa.example.com:/var/lib/exports/t2/def_t2_nfs_import
     5b8ba182-7d05-44e4-9d64-2a1bb529b797 | mion.ipa.example.com:/var/lib/exports/t2/def_t2_nfs_iso
     d2fd5e4b-c3de-4829-9f4a-d56246f5454b | mion.ipa.example.com:/var/lib/exports/t2/def_t2_nfs_lcs
     e2ba769c-e5a3-4652-b75d-b68959369b55 | mion.ipa.example.com:/var/lib/exports/t1/def_t1_nfs_master
     f5be3009-4c84-4d59-9cfe-a1bcedac4038 | mion.ipa.example.com:/var/lib/exports/t1/def_t1_nfs_sas
    

So we are going to rename the def_t2_nfs targets to def_t3_nfs. First we need to update the mount point:

::
    
    update storage_server_connections set connection='mion.ipa.example.com:/var/lib/exports/t3/def_t3_nfs_import' where id='842add9e-ffef-44d9-bf6d-4f8231b375eb';
    
    update storage_server_connections set connection='mion.ipa.example.com:/var/lib/exports/t3/def_t3_nfs_iso' where id='5b8ba182-7d05-44e4-9d64-2a1bb529b797';
    
    update storage_server_connections set connection='mion.ipa.example.com:/var/lib/exports/t2/def_t2_nfs_lcs' where id='d2fd5e4b-c3de-4829-9f4a-d56246f5454b';
    

Next we are going to replace the name in the storage_domain_static table.

::
    
    update storage_domain_static set storage_name='def_t3_nfs_lcs' where storage='d2fd5e4b-c3de-4829-9f4a-d56246f5454b';
    
    update storage_domain_static set storage_name='def_t3_nfs_iso' where storage='5b8ba182-7d05-44e4-9d64-2a1bb529b797';
    
    update storage_domain_static set storage_name='def_t3_nfs_import' where storage='842add9e-ffef-44d9-bf6d-4f8231b375eb';
    

That's it! Now check it all looks correct and restart.

::
    
    engine=# select id,storage,storage_name from storage_domain_static;
                      id                  |               storage                |   storage_name    
    --------------------------------------+--------------------------------------+-------------------
     a8ac8bd0-cf40-45ae-9f39-b376c16b7fec | d2fd5e4b-c3de-4829-9f4a-d56246f5454b | def_t3_nfs_lcs
     c3aa02d8-02fd-4a16-bfe6-59f9348a0b1e | 5b8ba182-7d05-44e4-9d64-2a1bb529b797 | def_t3_nfs_iso
     6bffd537-badb-43c9-91b2-a922cf847533 | 842add9e-ffef-44d9-bf6d-4f8231b375eb | def_t3_nfs_import
     d719e5f2-f59d-434d-863e-3c9c31e4c02f | e2ba769c-e5a3-4652-b75d-b68959369b55 | def_t1_nfs_master
     a085aca5-112c-49bf-aa91-fbf59e8bde0b | f5be3009-4c84-4d59-9cfe-a1bcedac4038 | def_t1_nfs_sas
    (5 rows)
    
    engine=# select id,connection from storage_server_connections;
                      id                  |                           connection                            
    --------------------------------------+-----------------------------------------------------------------
     e2ba769c-e5a3-4652-b75d-b68959369b55 | mion.ipa.example.com:/var/lib/exports/t1/def_t1_nfs_master
     f5be3009-4c84-4d59-9cfe-a1bcedac4038 | mion.ipa.example.com:/var/lib/exports/t1/def_t1_nfs_sas
     842add9e-ffef-44d9-bf6d-4f8231b375eb | mion.ipa.example.com:/var/lib/exports/t3/def_t3_nfs_import
     5b8ba182-7d05-44e4-9d64-2a1bb529b797 | mion.ipa.example.com:/var/lib/exports/t3/def_t3_nfs_iso
     d2fd5e4b-c3de-4829-9f4a-d56246f5454b | mion.ipa.example.com:/var/lib/exports/t3/def_t3_nfs_lcs
    (5 rows)

