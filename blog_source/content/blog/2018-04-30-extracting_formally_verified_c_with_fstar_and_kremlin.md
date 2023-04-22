+++
title = "Extracting Formally Verified C with FStar and KreMLin"
date = 2018-04-30
slug = "2018-04-30-extracting_formally_verified_c_with_fstar_and_kremlin"
# This is relative to the root!
aliases = [ "2018/04/30/extracting_formally_verified_c_with_fstar_and_kremlin.html" ]
+++
# Extracting Formally Verified C with FStar and KreMLin

As software engineering has progressed, the correctness of software has
become a major issue. However the tools that exist today to help us
create correct programs have been lacking. Human\'s continue to make
mistakes that cause harm to others (even I do!).

Instead, tools have now been developed that allow the verification of
programs and algorithms as correct. These have not gained widespread
adoption due to the complexities of their tool chains or other social
and cultural issues.

The Project Everest research has aimed to create a formally verified
webserver and cryptography library. To achieve this they have developed
a language called F\* (FStar) and KreMLin as an extraction tool. This
allows an FStar verified algorithm to be extracted to a working set of C
source code - C source code that can be easily added to existing
projects.

## Setting up a FStar and KreMLin environment

Today there are a number of undocumented gotchas with opam - the OCaml
package manager. Most of these are silent errors. I used the following
steps to get to a working environment.

    # It's important to have bzip2 here else opam silently fails!
    dnf install -y rsync git patch opam bzip2 which gmp gmp-devel m4 \
            hg unzip pkgconfig redhat-rpm-config

    opam init
    # You need 4.02.3 else wasm will not compile.
    opam switch create 4.02.3
    opam switch 4.02.3
    echo ". /home/Work/.opam/opam-init/init.sh > /dev/null 2> /dev/null || true" >> .bashrc
    opam install batteries fileutils yojson ppx_deriving_yojson zarith fix pprint menhir process stdint ulex wasm

    PATH "~/z3/bin:~/FStar/bin:~/kremlin:$PATH"
    # You can get the "correct" z3 version from https://github.com/FStarLang/binaries/raw/master/z3-tested/z3-4.5.1.1f29cebd4df6-x64-ubuntu-14.04.zip
    unzip z3-4.5.1.1f29cebd4df6-x64-ubuntu-14.04.zip
    mv z3-4.5.1.1f29cebd4df6-x64-ubuntu-14.04 z3

    # You will need a "stable" release of FStar https://github.com/FStarLang/FStar/archive/stable.zip
    unzip stable.zip
    mv FStar-stable Fstar
    cd ~/FStar
    opam config exec -- make -C src/ocaml-output -j
    opam config exec -- make -C ulib/ml

    # You need a master branch of kremlin https://github.com/FStarLang/kremlin/archive/master.zip
    cd ~
    unzip master.zip
    mv kremlin-master kremlin
    cd kremlin
    opam config exec -- make
    opam config exec -- make test

## Your first FStar extraction

