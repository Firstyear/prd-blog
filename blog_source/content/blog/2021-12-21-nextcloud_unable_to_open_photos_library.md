+++
title = "Nextcloud - Unable to Open Photos Library"
date = 2021-12-21
slug = "2021-12-21-nextcloud_unable_to_open_photos_library"
# This is relative to the root!
aliases = [ "2021/12/21/nextcloud_unable_to_open_photos_library.html" ]
+++
# Nextcloud - Unable to Open Photos Library

I noticed since macos 11.6.2 that Nextcloud has been unable to sync my
photos library. Looking into this error in Console.app I saw:

    error   kernel  System Policy: Nextcloud(798) deny(1) file-read-data /Users/william/Pictures/Photos Library.photoslibrary

It seems that Nextcloud is not *sandboxed* which means that macos
enforces stricter permissions on what this can or can not access, which
is what prevented the photos library from syncing.

To resolve this you can go to System Preferences -\> Security and
Privacy -\> Privacy -\> Full Disk Access and then grant Nextcloud.app
full disk access which will allow it to read the filesystem.

I tried to allow this via the files and folders access but I was unable
to add/remove new items to this list.

