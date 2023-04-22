+++
title = "Using a TPM for SSH keys on OpenSUSE Tumbleweed"
date = 2023-04-20
slug = "2023-04-20-using_a_tpm_for_ssh_keys_on_opensuse_tumbleweed"
# This is relative to the root!
aliases = [ "2023/04/20/using_a_tpm_for_ssh_keys_on_opensuse_tumbleweed.html", "blog/html/2023/04/20/using_a_tpm_for_ssh_keys_on_opensuse_tumbleweed.html" ]
+++
# Using a TPM for SSH keys on OpenSUSE Tumbleweed

In some environments it is required to store ssh private keys in a way
where they can not be extracted from the machine. Trusted Platform
Modules (TPM) are an excellent way to achieve this. While other guides
exist online for how to configure this for other distributions, this
will focus on OpenSUSE Tumbleweed.

## Install Packages

The following is required to be installed.

    zypper install tpm2-pkcs11 tpm2.0-tools tpm2-0-tss libtpm2_pkcs11-0

-   tpm2-pkcs11 - tools to configure the ssh key in the TPM
-   tpm2.0-tools - tools for TPM introspection
-   tpm2-0-tss - udev rules and tss group
-   libtpm2_pkcs11-0 - library for ssh to access TPM via pkcs

## Check the TPM exists

You can check the TPM exists and is working with:

    ls -l /dev/tpm*
    # crw-rw---- 1 tss root  10,   224 Apr 19 18:39 /dev/tpm0

To check the supported algorithms on the TPM:

    tpm2_getcap algorithms

If this command errors, your TPM may be misconfigured or you may not
have access to the TPM.

*HINT*: You can add a TPM to a KVM virtual machine with virt-install
with the line:

    --tpm backend.type=emulator,backend.version=2.0,model=tpm-tis

From virt-manager you can add the TPM via \"Add Hardware\", \"TPM\".

Editing the virtual machine xml directly a TPM can be defined with:

    <domain type='kvm'>
      <devices>
        <tpm model='tpm-tis'>
          <backend type='emulator' version='2.0'/>
        </tpm>
      </devices>
    </domain>

## Allow User Access

Add your user to the tss group

    usermod -a -G tss username

## Configure the SSH key

*NOTE* Be sure to perform these steps as your user - not as root!

Initialise the tpm pkcs store - note the id in the output.

    tpm2_ptool init
    # action: Created
    # id: 1

Using the id from the above output, you can use that to create a new
token. Note here that the userpin is the pin for using the ssh key. The
sopin is the recovery password incase you lose the pin and need to reset
it.

    tpm2_ptool addtoken --pid=1 --label=ssh --userpin="" --sopin=""
    tpm2_ptool addkey --label=ssh --userpin="" --algorithm=ecc256

If you want to use a different key algorithm, other choices are rsa2048,
rsa3072, rsa4096, ecc256, ecc384, ecc521.

Now you can view the public key with:

    ssh-keygen -D /usr/lib64/pkcs11/libtpm2_pkcs11.so.0

It\'s a good idea to store this into a file for later:

    ssh-keygen -D /usr/lib64/pkcs11/libtpm2_pkcs11.so.0 | tee ~/.ssh/id_ecdsa_tpm.pub

## Using the SSH Key

You can modify your ssh configuration to always use the key. You will be
prompted for the userpin to access the ssh key as required.

    # ~/.ssh/config

    PKCS11Provider /usr/lib64/pkcs11/libtpm2_pkcs11.so.0
    PasswordAuthentication no

