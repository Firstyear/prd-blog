+++
title = "Starting with Rage on OpenSUSE"
date = 2023-05-26
slug = "2023-05-26-starting-with-rage-on-opensuse"
# This is relative to the root!
+++
# Starting with Rage on OpenSUSE

Rage is a rust implementation of Age, a modern, simple and secure file encryption tool. It
is easier to use than other tools like GPG, and being written in a memory safe language it
avoids many of the exploits that may occur in C based tools.

## Installing Rage

You can install rage on leap or tumbleweed from zypper

    zypper install rage-encryption

Alternately you can install from cargo with

    cargo install rage

## Key management

The recipient must generate a key. This can be either a rage key, or an ssh key which is of the
form `ssh-rsa` or `ssh-ed25519`.

    # The public key is displayed.
    rage-keygen -o ~/rage.key
    # age1y2lc7x59jcqvrpf3ppmnj3f93ytaegfkdnl5vrdyv83l8ekcae4sexgwkg

To use ssh keys, you can generate a key with:

    ssh-keygen -t ed25519
    # cat /root/.ssh/id_ed25519.pub
    ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIE1kWXiYIn/VWzo0DlnIp3cRx/kZd6d9WbwehKJpPx1R

## Encrypting to a public key

You encrypt a file to the owner of the public key with:

    rage -e -r <pub key> -o <encrypted output> <input>
    # With their rage public key.
    rage -e -r age1y2lc7x59jcqvrpf3ppmnj3f93ytaegfkdnl5vrdyv83l8ekcae4sexgwkg -o ~/encyrpted.age data

Alternately, if you want to allow the content of the encrypted file to be base64 for emailing (note the -a):

    rage -e -a -r <pub key> -o <encrypted output> <input>
    # With their rage public key.
    rage -e -a -r age1y2lc7x59jcqvrpf3ppmnj3f93ytaegfkdnl5vrdyv83l8ekcae4sexgwkg \
        -o ~/encyrpted.age data

    # cat /tmp/encrypted
    -----BEGIN AGE ENCRYPTED FILE-----
    YWdlLWVuY3J5cHRpb24ub3JnL3YxCi0+IFgyNTUxOSByaDNTNHR0dlI5RkRudmpH
    NEUrT1RrQ3pZdjM5alRVYThDeG5xdTBxd1EwCjYxVGkwV05ibXlWeUN3MWVuNTBC
    Qk1SdEwyd3J1RjgrNVkxem5pbHJscVEKLT4gTyI7WFQtZ3JlYXNlIEZDXyBiICFV
    NgpoTlJ5ME95azMycE5GbS9oS0h6a280RlRTRHNKbE9mMGZjTmFCUjB6aWEwZGxU
    Rjg1RkZmdkhBSkU4Y1dZdEM3CjV0VXl4dE5Qd3E0SU1GSXNIejQKLS0tIFhscDBn
    MlBiTmxPekthY1RabVcxN0JkQnJsd3RKUkpTKzRkelZ1eDFXSk0KHzCOyBZHPe/P
    cV3Fez6yusycXcm83Bt+N2yHTG2utOGxfmIxb5c=
    -----END AGE ENCRYPTED FILE-----

The ssh public key can be encrypted to if the public key is in a file

    rage -e -a -R <path to public key> -o <encrypted output> <input>
    # Using the ssh public key in a file
    rage -e -a -R ~/id_ed25519.pub -o /tmp/ssh-encrypted data

## Decrypting a file

The recipient can then decrypt with:

    rage -d -i <path to private key> -o <decrypted output> <encrypted input>

    rage -d -i ~/rage.key -o /tmp/decrypted /tmp/encrypted

    # cat /tmp/decrypted
    hello

With an ssh private key

    rage -d -i <path to ssh private key> -o <decrypted output> <encrypted input>

    rage -d -i ~/.ssh/id_ed25519 -o /tmp/ssh-decrypted /tmp/ssh-encrypted

## Encrypt to multiple recipients

Rage can encrypt to multiple identities at a time.

    rage -e -a -R <first ssh pub key> -R <second pub key> ... -o <encrypted output> <input>
    rage -e -a -r <first pub key> -r <second pub key> ... -o <encrypted output> <input>
    rage -e -a -R <first ssh pub key> -r <first rage pub key> ... -o <encrypted output> <input>

    rage -e -a -R /root/.ssh/id_ed25519.pub \
        -r age1h8equ4vs5pyp8ykw0z8m9n8m3psy6swme52ztth0v66frgu65ussm8gq0t \
        -r age1y2lc7x59jcqvrpf3ppmnj3f93ytaegfkdnl5vrdyv83l8ekcae4sexgwkg \
        -o /tmp/ssh-encrypted hello

*all* of the associated keys can decrypt this file.

    rage -d -i /root/.ssh/id_ed25519 -o /tmp/ssh-decrypted /tmp/ssh-encrypted

    rage -d -i ~/rage.key -o /tmp/decrypted /tmp/ssh-encrypted

## Using a passphrase instead of a key

Rage can encrypt with a passphrase:

    rage -e -p -o <encrypted output> <input>

    rage -e -p -o /tmp/passphrase-encrypted data

Decrypted with (passphrase is detected and prompted for):

    rage -d -o <decrypted output> <encrypted input> 

    rage -d -o /tmp/decrypted /tmp/passphrase-encrypted


