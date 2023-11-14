+++
title = "Getting Started with PKCS11"
date = 2023-11-14
slug = "2023-11-14-pkcs11-getting-started"
# This is relative to the root!
+++

# Getting Started with PKCS11

PKCS11 is one of those horrible mystery technologies, that just seems to have no good starting place
or reference on how to make it work. But it's also a technology that you see commonly around for
hardware security modules (HSM), trusted platform modules (TPM) and other high impact cryptographic environments. This makes it
an annoying chasm to cross for developers and administrators alike who want to configure these
important tools for key security.

So I decided to spend some time to learn about how this all works - scouring a variety of sources
I hope to put together something that can help make it easier in future for others.

## Concepts

PKCS11 is a specification defined by OASIS. The [specification](https://docs.oasis-open.org/pkcs11/pkcs11-spec/v3.1/cs01/pkcs11-spec-v3.1-cs01.html)
isn't very informative for a new user.

What PKCS11 defines is an *abstraction* between an application and a security module. This allows
the security module to be swapped with an alternative and the application requires no changes.

```
┌─────────────────┐
│                 │
│   Application   │
│                 │
└─────────────────┘
         │         
         ▼         
┌─────────────────┐
│  PKCS11 Aware   │
│  Cryptographic  │
│     Library     │
└─────────────────┘
         │         
   Cryptoki API    
         │         
         ▼         
┌─────────────────┐
│                 │
│  PKCS11 Module  │
│                 │
└─────────────────┘
         │         
         ▼         
┌─────────────────┐
│                 │
│       HSM       │
│                 │
└─────────────────┘
```

Commonly PKCS11 modules will abstract over communication with a HSM or a TPM, but there are also software
HSM that are useful for testing. This also means that if you have a vendor who provides you a HSM they
will commonly also provide you a PKCS11 module to allow your application to communicate with it.

The PKCS11 module itself is just a dynamic library (so, dll, or dylib) which implements and exposes
the Cryptoki C API. This is how an application can dynamically load the module and use it with no
changes.

Since this is an abstraction it also means that the cryptographic material stored in our HSM has
a standard layout and structure that applications can expect.

```
                                                     ┌─────────────────┐
                                                   ┌─┴───────────────┐ │
                           ┌─────────────────┐    ┌┴────────────────┐│ │
                           │                 │    │                 ││ │
                      ┌───▶│  Token / Slot   │───▶│     Object      │├─┘
                      │    │                 │    │                 ├┘
┌─────────────────┐   │    └─────────────────┘    └─────────────────┘
│                 │   │
│  PKCS11 Module  │───┤                              ┌─────────────────┐
│                 │   │                            ┌─┴───────────────┐ │
└─────────────────┘   │    ┌─────────────────┐    ┌┴────────────────┐│ │
                      │    │                 │    │                 ││ │
                      └───▶│  Token / Slot   ├───▶│     Object      │├─┘
                           │                 │    │                 ├
                           └─────────────────┘    └─────────────────┘
```

Each module has a number of tokens (also called slots). Then for each token, these have many
objects associated which can be private keys, public keys, x509 certificates and more.

Authentication is performed from the application to the token. There are two authentication values:
the security officer PIN, and the user PIN. Generally this allows separation between the ability
to write/destroy objects, and the ability to use them in an application.

## Prerequisites

The easiest way to "test" this is with a virtual machine configured with a softtpm. You can add this
in libvirt with the xml:

```
<domain type='kvm'>
  <devices>
    <tpm model='tpm-crb'>
      <backend type='emulator' version='2.0'/>
    </tpm>
  </devices>
</domain>
```

If using virt-manager you can add a tpm under the add hardware menu. Ensure you set this to CRB (command
request buffer) and version 2.0.

If you are using OpenSUSE you will need the following packages:

* tpm2-pkcs11 - the module exposing TPMs via the cryptoki api
* opensc - a library for interacting with and administering pkcs11 modules
* openssl-3 - generic cryptographic library
* pkcs11-provider - a pkcs11 provider for openssl-3 allowing it to use our pkcs11 modules

```
zypper install openssl-3 pkcs11-provider tpm2-pkcs11 opensc
```

This certainly isn't an exhaustive or limited list - there are plenty of other tools that can
interact with pkcs11, for example p11-kit.

## Setting Up Our Device

pkcs11 modules are generally installed into `/usr/lib64/pkcs11`. opensc does not have a way to list
the module that are available. (p11-kit does with `p11-kit list-modules`)

For our example we're going to use the tpm pkcs11 provider at `/usr/lib64/pkcs11/libtpm2_pkcs11.so`

We can show info about the module with:

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --show-info
```

```
Cryptoki version 2.40
Manufacturer     tpm2-software.github.io
Library          TPM2.0 Cryptoki (ver 1.9)
Using slot 0 with a present token (0x1)
```

We can now list all the slots with:

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --list-slots
```

```
Available slots:
Slot 0 (0x1):
  token state:   uninitialized
```

We can see that we have a single slot and it's not initialised yet. So lets initialise it. You'll
notice that we use "--slot 1" even though the output above says "Slot 0". This is because we are
using the slot id in hex. Off by one errors are everywhere :)

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --init-token --slot 1 --label dev
```

You should be prompted to setup the security office (SO) PIN. At this point we can list our
slots again and see:

```
Available slots:
Slot 0 (0x1): dev
  token label        : dev
  token manufacturer : IBM
  token model        : SW   TPM
  token flags        : login required, rng, token initialized, PIN initialized
  hardware version   : 1.62
  firmware version   : 25.35
  serial num         : 0000000000000000
  pin min/max        : 0/128
Slot 1 (0x2):
  token state:   uninitialized
```

GThe number of slots will keep growing as we add more slots.

> TIP: `libtpm2_pkcs11` is actually storing it's keys in an sqlite database on your system and
> dynamically loading and unloading them from the TPM as required. These keys are stored sealed
> with a TPM internal key so that only this TPM can use the keys. This means you don't have to
> worry about running out of space on your TPM.

We can now also setup our user pin, using the SO to trigger the PIN change.

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --slot 1 --login --login-type so --init-pin
```

## Managing Objects

We can show the objects in our slot with:

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --login --slot 1 --list-objects
```

Initially this output should be empty - we haven't made anything yet!

We can create a new ECDSA key. This key will have a label and an ID associated so that we can
reference the key uniquely.

> NOTE: If you don't set --id here, then some pkcs11 providers will fail to use your key. Ensure
> you set both a label and an ID!

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --login --slot 1 --keypairgen \
    --key-type EC:prime256v1 --label "my_key" --usage-sign --id 01
```

Now we can see our objects with `list-objects`

```
Public Key Object; EC  EC_POINT 256 bits
  EC_POINT:   04410430bb3c90d2caae1a848e99e3cfb265bfcc969274d478a57050fff94749cc04c23e84aa11a86b500d0c888da331c20abecf8cc1b4ed15ef5535561f0678cc580f
  EC_PARAMS:  06082a8648ce3d030107
  label:      my_key
  ID:         01
  Usage:      encrypt, verify
  Access:     local
Private Key Object; EC
  label:      my_key
  ID:         01
  Usage:      decrypt, sign
  Access:     sensitive, always sensitive, never extractable, local
  Allowed mechanisms: ECDSA,ECDSA-SHA1,ECDSA-SHA256,ECDSA-SHA384,ECDSA-SHA512
```

We have two objects - An ECDSA public key, and the ECDSA private key. We can also see what the key
can be used for and allowed algorithms. Finally we have some attributes that defined properties
of the key.

* local - the content of the key was generated inside a HSM
* sensitive - means that the content of the key can not be disclosed in plaintext
* always sensitive - the key has never been disclosed outside of a HSM
* extractable - the key can be extracted from this device in an encrypted manner
* never extractable - the key has never been extracted from this device

These properties allow us to see useful things:

* A local, always sensitive and never extractable key shows us that this key was generated and used only in this HSM
* A sensitive only key that is extractable may have been shared between other HSMs with a wrapping key
* A sensitive key that does NOT have the always sensitive and local properties was likely imported from an external source

If we wanted now we could delete these objects:

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --login --slot 1 --delete-object \
    --label my_key --type privkey
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --login --slot 1 --delete-object \
    --label my_key --type pubkey
```

Notice we have to do this twice? Once for the public key, once for the private key.

## Using Our Keys with OpenSSL

At this point we may wish to use our key with openssl, perhaps we want to request a certificate to
be signed or some other operation.

First we need to configure openssl to understand where our pkcs11 modules are:

```
# provider.conf
openssl_conf = openssl_init

[openssl_init]
providers = provider_sect

[provider_sect]
default = default_sect
pkcs11 = pkcs11_sect

[default_sect]
activate = 1

[pkcs11_sect]
module = /usr/lib64/ossl-modules/pkcs11.so
pkcs11-module-path = /usr/lib64/pkcs11/libtpm2_pkcs11.so
activate = 1
```

We can check this worked with:

```
OPENSSL_CONF=provider.conf openssl list -providers -provider pkcs11
```

```
Providers:
  default
    name: OpenSSL Default Provider
    version: 3.1.4
    status: active
  pkcs11
    name: PKCS#11 Provider
    version: 3.1.3
    status: active
```

We can now show details about our key with:

```
OPENSSL_CONF=provider.conf openssl pkey -provider pkcs11 -noout -text \
    -in "pkcs11:token=dev;label=my_key"
```

```
PKCS11 EC Private Key (256 bits)
[Can't export and print private key data]
URI pkcs11:model=SW%20%20%20TPM;manufacturer=IBM;serial=0000000000000000;token=dev;id=%01;object=my_key;type=private
```

You'll notice a new concept here - pkcs11 supports URI's to reference specific objects. This allows you
to have many providers, with many slots and objects, and still uniquely interact with specific objects.

As you can see from our URI of `pkcs11:token=dev;label=my_key` we are referencing our key by
its token name `dev` and the `label` we gave it earlier during key creation. The openssl display
shows a number of other possible elements in the URI that we could use. For a full list
see [rfc7512 section 2.3](https://www.rfc-editor.org/rfc/rfc7512#section-2.3).

At this point openssl can see our key and so now we can make a CSR.

```
OPENSSL_CONF=provider.conf openssl req -provider pkcs11 \
    -new -days 1 -subj '/CN=my_key/' -out csr.pem
    -key "pkcs11:token=dev;label=my_key"
```

Once this is signed we can load this into our pkcs11 module:

```
pkcs11-tool --module  /usr/lib64/pkcs11/libtpm2_pkcs11.so --write-object cert.pem \
    --label "my_key" --id 01 --type cert --login --login-type so
```

Notice we use the same label and id as the key and public key? This way the URI only needs to change
to specify the type of the object to find the correct associated key and public key.

Now when we list our objects we can see:

```
Public Key Object; EC  EC_POINT 256 bits
  EC_POINT:   04410430bb3c90d2caae1a848e99e3cfb265bfcc969274d478a57050fff94749cc04c23e84aa11a86b500d0c888da331c20abecf8cc1b4ed15ef5535561f0678cc580f
  EC_PARAMS:  06082a8648ce3d030107
  label:      my_key
  ID:         01
  Usage:      encrypt, verify
  Access:     local
Private Key Object; EC
  label:      my_key
  ID:         01
  Usage:      decrypt, sign
  Access:     sensitive, always sensitive, never extractable, local
  Allowed mechanisms: ECDSA,ECDSA-SHA1,ECDSA-SHA256,ECDSA-SHA384,ECDSA-SHA512
Certificate Object; type = X.509 cert
  label:      my_key
  subject:    DN: CN=my_key
  serial:     57812D09A3503723F038BA407CD7D2E965289FC1
  ID:         01
```

## Application Integration

Once we have our key and certificate in the TPM, most applications that use openssl require very
little modification.

* Ensure that we have the `OPENSSL_CONF=` with the pkcs11 provider in the environment of the application
* Change the private key file to a pkcs11 url

Over time I'll add more examples here as I work on them.

## Using a Wrap Key to Move Objects

TBD

## DEBUGGING

As with anything, these tools can break and we need to be able to debug them.

* `TPM2_PKCS11_LOG_LEVEL=1` - set the log level of the `tpm2_pkcs11` module. Values are 0, 1, 2
* `PKCS11_PROVIDER_DEBUG=file:/dev/stderr,level:1` - set the log level of the openssl pkcs11 provider. Values are 0, 1, 2

