+++
title = "SSH Key Storage Comparison"
date = 2023-10-24
slug = "2023-10-24-ssh-key-storage-comparisons"
# This is relative to the root!
+++

# SSH Key Storage

A kind reader asked me an interesting question the other day. "What do you think of the choice
of ssh sk keys between ecdsa and ed25519?". At the same time, within Kanidm we have actually been
discussing the different approaches we could take with ssh key handling in the future between
ssh cas and ssh sk key attestation, especially once we consider service accounts.

As with anything in security we always need to balance the technology with the risks and threats
that we are trying to mitigate or prevent.

Compared to the use of a username and password, using ssh keys to authenticate to a remote server
is significantly more secure. This is especially true if you disable password authentication
methods.

## Cryptographic Considerations

Of course, just using cryptographic authentication isn't free. While we no longer have the risks
of passwords, the threats that exist against cryptographic keys are quite different. This means
we now need to ensure that we follow and keep up to date with developments in crytpgraphy.

There are many sites that can assist with key requirements such as [keylength.com](https://www.keylength.com).
The following table was generated on 2023-09-25 with the year set to 2030 (meaning these key sizes values are
*predicted* to be safe until 2030).

> |Method           |Date     |Symmetric| FM      |DL Key| DL Group|Elliptic Curve|Hash|
> |   ---           |   ---   |   ---   |   ---   | ---  |   ---   |  ---         | ---|
> |Lenstra / Verheul|2030     |  93     |2493^2016|165   | 2493    |  176         | 186|
> |Lenstra Updated  |2030     |  88     |1698^2063|176   | 1698    |  176         | 176|
> |ECRYPT           |2029-2068|  256    |15360    |512   | 15360   |  512         | 512|
> |NIST             |2019-2030|  112    |2048     |224   | 2048    |  224         | 224|
> |ANSSI            |> 2030   |  128    |3072     |200   | 3072    |  256         | 256|
> |NSA              |-        |  256    |3072     |-     | -       |  384         | 384|
> |RFC3766          |-        |  -      |   -     | -    |   -     |   -          |  - |
> |BSI              |-        |  -      |   -     | -    |   -     |   -          |  - |
>
> * DL - Discrete Logarithm
> * FM - Factoring Modulus

The values here that are important for ssh key generation is the Factoring Modulus (FM) and
Elliptic Curve.Each of these sources is assuming different risks and requirements. You will need to
make your own informed choices about these but reading between the values here your minimum key
size should be at least RSA 2048 and ECDSA P256 / ED25519, or if you wish to future proof
you may wish to choose RSA 3072, ECDSA P512 / ED448.

## P-256 vs ED25519

Our dear reader asked if you should choose ED25519 over ECDSA P-256 as there are two attacks (LadderLeak, Minerva)
that affect ECDSA. I am not a cryptographer, so my view here should be taken with caution, but reading
both papers the authors indicate that these attacks require a large number of signatures to conduct
meaning that outside of research conditions, these may not be viable against ssh keys. The authors
themself validate that these attacks may not be possible outside of research conditions.

## SSH Key Storage

Since we now have cryptographic keys for authentication we need to care about how we store these.
Storage of keys is just as important as the type of key we use.

### Files on Disk

Most peoples first introduction to ssh keys is storing them as files in their home directory.
If during the generation you entered a passphrase, then this stores the private keys as
encrypted files. If you do not specify a passphrase these are stored unencrypted. Generally it's
a good idea to store these with a passphrase so that theft of the private key means an attacker
can not immediately use this for nefarious purposes.

### Security Keys

Rather than storing ssh keys in files, they can be generated in the secure enclave of
a security key such as a yubikey. Because these are stored in the secure enclave, malware or an
attacker can not take the keys from the machine. Additionally, because of how these keys work, they
will not operate without physical interaction with the key.

Another unique property of these keys is they can strictly enforce that userverification (such as
a PIN or biometric) is validated as well as physical interaction before they can proceed.
This verification requirement is baked into the key at creation time and enforced by the secure unclave so that it can not be bypassed, adding an extra
level of security - changing the key from something you have to something you have and are/know.

These keys can also attest (cryptographically prove) that they are in a secure enclave at creation time,
so that for higher security environments they can assert that keys *must* be hardware backed.

So far we have mentioned these keys are in the secure enclave. By default the actual
private key is stored in a file, encrypted by a secret master key inside the security key. This
is what allows these keys to have "unlimited storage" as keys are loaded and unloaded as needed (the
same way that a TPM works).

However for the most secure environments, they may wish that the key never leaves the enclave even if in a secure encrypted form. Security
keys have extremely limited storage (generally 8 keys, some models up to 25), so this limits the use
of these resident keys. But if they are required, you can create a resident, attested, user verified
key for the highest levels of assurance.

### Certificate Authorities

ssh keys normally rely on the public key being transferred to the machine to authenticate too. This
leads to strategies like ssh key distribution in kanidm so that a central server can be consulted
for which authorised keys are valid for authentication.

However a ssh certificate authority functions more like TLS where a certificate authority's key
is trusted by the servers, and then users are issued an ssh key *signed* by that authority. When
authenticating to the server since the user certificate is signed by a trusted authority it can be
allowed to proceed.

Since these keys are issued as files they carry some of the same risks as our previous files. However
because there is an authority that can issue the keys, they can be created with a short expiration
as required. This leads to some interesting configurations where an external tool can be used to
issue certificates as required, limited to specific hosts and commands.

## Comparison

As with anything, all of these approaches have pros and cons. It's up to you to decide what will be
best in your scenario.

> | Key Type | Strict Enforcement | Exfiltration Possible | Expiration          | Hardware Bound | User Verification |
> |----------|:------------------:|:---------------------:|:-------------------:|:--------------:|:-----------------:|
> | ssh key  | no                 | yes                   | no                  | no             | no                |
> | encrypted ssh key  | no       | yes                   | no                  | no             | yes-ish           |
> | sk key   | no                 | no                    | no                  | yes            | yes               |
> | attested sk key   | yes       | no                    | no                  | yes            | yes               |
> | ca key   | yes                | yes                   | yes                 | possible       | yes*              |

\* If you use ca keys with sk keys, or your issuing ca provides a form of verification

For some example use cases:

_I am a home user logging into my server_
* Use what ever makes you happy
* Any ssh key auth is better than a password

_I am logging into production servers_
* Use ssh key files with passphrases
* sk keys with enforce user verification

_I am a business looking to enforce secure keys for admins/developers_
* Use attested sk keys with enforced user verification
* Deploy an ssh ca that requires authentication to issue certificates

_I am a three letter agency that ..._
* Ask your security team, that's what they're there for.
* But also, use attested resident sk keys with enforced user verification

There is no perfect answer here, but you need to consider the risks you face and how you want
to mitigate them. The biggest problem of all of this is *proof*. Once you move from "I want an ssh
key" to "we want to enforce our requirements" this adds extra challenges that only an ssh ca or attested
sk keys can fufil. While it's nice to trust our users, strictly enforced requirements are far better
when it comes to security.

## Things Not To Do

### SSHFP DNS Records

Using SSHFP DNS records is insecure. This is because even if you have DNSSEC, it [does nothing to protect you.](https://sockpuppet.org/blog/2015/01/15/against-dnssec/)

This approaches leaves you open to MITM attacks which is effectively a path to remote unauthorised access.

### SSH Key Distribution with LDAP StartTLS

When distributing keys with LDAP, you must always use LDAPS. This is because [LDAP with StartTLS is insecure.](/2021/08/12/starttls_in_ldap.html)

## SSH Key Creation Reference

### Files on Disk

```
ssh-keygen -t [rsa | ecdsa | ed25519] -b <bits>
ssh-keygen -t ed25519
ssh-keygen -t ecdsa -b 512
ssh-keygen -t rsa -b 3072
```

### Security Keys (Basic)

```
ssh-keygen -t [ecdsa-sk | ed25519-sk]
ssh-keygen -t ecdsa-sk
// Note: Not all keys support ed25519
ssh-keygen -t ed25519-sk
```

### Security Keys (User Verified)

```
ssh-keygen -t [ecdsa-sk | ed25519-sk] -O verify-required
ssh-keygen -t ecdsa-sk -O verify-required
```

### Certificate Authority
