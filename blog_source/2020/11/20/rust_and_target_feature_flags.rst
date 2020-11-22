Rust, SIMD and target-feature flags
===================================

This year I've been working on `concread <https://github.com/kanidm/concread>`_ and one of the ways
that I have improved it is through the use of `packed_simd <https://github.com/rust-lang/packed_simd>`_
for parallel key lookups in hashmaps. During testing I saw a ~10% speed up in Kanidm which heavily
relies on concread, so great, pack it up, go home.

...?
====

Or so I thought. Recently I was learning to use Ghidra with a friend, and as a thought exercise
I wanted to see how Rust decompiled. I put the concread test suite into Ghidra and took a look.
Looking at the version of concread with `simd_support` enabled, I saw this in the disassembly
(truncated for readability).

::

         **************************************************************
         *                          FUNCTION                          *
         **************************************************************
         Simd<[packed_simd_2--masks--m64;8]> __stdcall eq(Simd<[p
        ...
       100114510 55              PUSH       RBP
       100114511 48 89 e5        MOV        RBP,RSP
       100114514 48 83 e4 c0     AND        RSP,-0x40
       100114518 48 81 ec        SUB        RSP,0x100
                 00 01 00 00
       10011451f 48 89 f8        MOV        RAX,__return_storage_ptr__
       100114522 0f 28 06        MOVAPS     XMM0,xmmword ptr [self->__0.__0]
        ...
       100114540 66 0f 76 c4     PCMPEQD    XMM0,XMM4
       100114544 66 0f 70        PSHUFD     XMM4,XMM0,0xb1
                 e0 b1
       100114549 66 0f db c4     PAND       XMM0,XMM4
        ...
       100114574 0f 29 9c        MOVAPS     xmmword ptr [RSP + local_90],XMM3
                 24 b0 00 
                 00 00
       1001145b4 48 89 7c        MOV        qword ptr [RSP + local_c8],__return_storage_pt
                 24 78
        ...
       1001145be 0f 29 44        MOVAPS     xmmword ptr [RSP + local_e0],XMM0
                 24 60
        ...
       1001145d2 48 8b 44        MOV        RAX,qword ptr [RSP + local_c8]
                 24 78
       1001145d7 0f 28 44        MOVAPS     XMM0,xmmword ptr [RSP + local_e0]
                 24 60
       1001145dc 0f 29 00        MOVAPS     xmmword ptr [RAX],XMM0
        ...
       1001145ff 48 89 ec        MOV        RSP,RBP
       100114602 5d              POP        RBP
       100114603 c3              RET


Now, it's been a long time since I've had to look at x86_64 asm, so I saw this and went "great, it's
not using a loop, those aren't simple `TEST/JNZ` instructions, they have a lot of letters, awesome
it's using HW accel.

Time passes ...
===============

Coming back to this, I have been wondering how we could enable SIMD in concread at SUSE, since
389 Directory Server has just merged a change for 2.0.0 that uses concread as a cache. For this
I needed to know what minimum CPU is supported at SUSE. After some chasing internally, knowing
what we need I asked in the Rust Brisbane group about how you can define in `packed_simd` to
only emit instructions that work on a minimum CPU level rather than *my* cpu or the builder
cpu.

The response was "but that's already how it works".

I was helpfully directed to the `packed_simd perf guide <https://rust-lang.github.io/packed_simd/perf-guide/target-feature/rustflags.html>`_
which discusses the use of target features and target cpu. At that point I realised that for this
whole time I've only been using the default:

::

    # rustc --print cfg | grep -i target_feature
    target_feature="fxsr"
    target_feature="sse"
    target_feature="sse2"

The `PCMPEQD` is from sse2, but my cpu is much newer and should support AVX and AVX2. Retesting
this, I can see my CPU has much more:

::

    # rustc --print cfg -C target-cpu=native | grep -i target_feature
    target_feature="aes"
    target_feature="avx"
    target_feature="avx2"
    target_feature="bmi1"
    target_feature="bmi2"
    target_feature="fma"
    target_feature="fxsr"
    target_feature="lzcnt"
    target_feature="pclmulqdq"
    target_feature="popcnt"
    target_feature="rdrand"
    target_feature="rdseed"
    target_feature="sse"
    target_feature="sse2"
    target_feature="sse3"
    target_feature="sse4.1"
    target_feature="sse4.2"
    target_feature="ssse3"
    target_feature="xsave"
    target_feature="xsavec"
    target_feature="xsaveopt"
    target_feature="xsaves"

All this time, I haven't been using my native features!

For local builds now, I have .cargo/config set with:

::

    [build]
    rustflags = "-C target-cpu=native"

I recompiled concread and I now see in Ghidra:

::

        00198960 55              PUSH       RBP
        00198961 48 89 e5        MOV        RBP,RSP
        00198964 48 83 e4 c0     AND        RSP,-0x40
        00198968 48 81 ec        SUB        RSP,0x100
                 00 01 00 00
        0019896f 48 89 f8        MOV        RAX,__return_storage_ptr__
        00198972 c5 fc 28 06     VMOVAPS    YMM0,ymmword ptr [self->__0.__0]
        00198976 c5 fc 28        VMOVAPS    YMM1,ymmword ptr [RSI + self->__0.__4]
                 4e 20
        0019897b c5 fc 28 12     VMOVAPS    YMM2,ymmword ptr [other->__0.__0]
        0019897f c5 fc 28        VMOVAPS    YMM3,ymmword ptr [RDX + other->__0.__4]
                 5a 20
        00198984 c4 e2 7d        VPCMPEQQ   YMM0,YMM0,YMM2
                 29 c2
        00198989 c4 e2 75        VPCMPEQQ   YMM1,YMM1,YMM3
                 29 cb
        0019898e c5 fc 29        VMOVAPS    ymmword ptr [RSP + local_a0[0]],YMM1
                 8c 24 a0 
                 00 00 00
        ...
        001989e7 48 89 ec        MOV        RSP,RBP
        001989ea 5d              POP        RBP
        001989eb c5 f8 77        VZEROUPPER
        001989ee c3              RET


`VPCMPEQQ` is the AVX2 compare instruction (You can tell it's AVX2 due to the register YMM, AVX uses
XMM). Which means now I'm getting the SIMD comparisons I wanted!

These can be enabled with `RUSTFLAGS='-C target-feature=+avx2,+avx'` for selected builds, or in your
.cargo/config. It may be a good idea for just local development to do `target-cpu=native`.

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
