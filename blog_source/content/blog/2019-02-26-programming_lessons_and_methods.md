+++
title = "Programming Lessons and Methods"
date = 2019-02-26
slug = "2019-02-26-programming_lessons_and_methods"
# This is relative to the root!
aliases = [ "2019/02/26/programming_lessons_and_methods.html" ]
+++
# Programming Lessons and Methods

Everyone has their own lessons and methods that they use when they
approaching programming. These are the lessons that I have learnt, which
I think are the most important when it comes to design, testing and
communication.

## Comments and Design

Programming is the art of writing human readable code, that a machine
will eventually run. Your program needs to be reviewed, discussed and
parsed by another human. That means you need to write your program in a
way they can understand first.

Rather than rushing into code, and hacking until it works, I find it\'s
great to start with comments such as:

    fn data_access(search: Search) -> Type {
        // First check the search is valid
        //  * No double terms
        //  * All schema is valid

        // Retrieve our data based on the search

        // if debug, do an un-indexed assert the search matches

        // Do any need transform

        // Return the data
    }

After that, I walk away, think about the issue, come back, maybe tweak
these comments. When I eventually fill in the code inbetween, I leave
all the comments in place. This really helps my future self understand
what I was thinking, but it also helps other people understand too.

## State Machines

State machines are a way to design and reason about the states a program
can be in. They allow exhaustive represenations of all possible outcomes
of a function. A simple example is a microwave door.

    /----\            /----- close ----\          /-----\
    |     \          /                 v         v      |
    |    -------------                ---------------   |
    open   | Door Open |                | Door Closed |  close
    |    -------------                ---------------   |
    |    ^          ^                  /          \     |
    \---/            \------ open ----/            \----/

When the door is open, opening it again does nothing. Only when the door
is open, and we close the door (and event), does the door close (a
transition). Once closed, the door can not be closed any more (event
does nothing). It\'s when we open the door now, that a state change can
occur.

There is much more to state machines than this, but they allow us as
humans to reason about our designs and model our programs to have all
possible outcomes considered.

## Zero, One and Infinite

In mathematics there are only three numbers that matter. Zero, One and
Infinite. It turns out the same is true in a computer too.

When we are making a function, we can define limits in these terms. For
example:

    fn thing(argument: Type)

In this case, argument is \"One\" thing, and must be one thing.

    fn thing(argument: Option<Type>)

Now we have argument as an option, so it\'s \"Zero\" or \"One\".

    fn thing(argument: Vec<Type>)

Now we have argument as vec (array), so it\'s \"Zero\" to \"Infinite\".

When we think about this, our functions have to handle these cases
properly. We don\'t write functions that take a vec with only two items,
we write a function with two arguments where each one must exist. It\'s
hard to handle \"two\" - it\'s easy to handle two cases of \"one\".

It also is a good guide for how to handle data sets, assuming they could
always be infinite in size (or at least any arbitrary size).

You can then apply this to tests. In a test given a function of:

    fn test_me(a: Option<Type>, b: Vec<Type>)

We know we need to test permutations of:

-   a is \"Zero\" or \"One\" (Some, None)
-   b is \"Zero\", \"One\" or \"Infinite\" (.len() == 0, .len() == 1,
    .len() \> 0)

Note: Most languages don\'t have an array type that is \"One to
Infinite\", IE non-empty. If you want this condition (at least one
item), you have to assert it yourself ontop of the type system.

## Correct, Simple, Fast

Finally, we can put all these above tools together and apply a general
philosophy. When writing a program, first make it correct, then simpify
the program, then make it fast.

If you don\'t do it in this order you will hit barriers - social and
technical. For example, if you make something fast, simple, correct, you
will likely have issues that can be fixed without making a decrease in
performance. People don\'t like it when you introduce a patch that drops
performance, so as a result correctness is now sacrificed. (Spectre
anyone?)

If you make something too simple, you may never be able to make it
correctly handle all cases that exist in your application - likely
facilitating a future rewrite to make it correct.

If you do correct, fast, simple, then your program will be correct, and
fast, but hard for a human to understand. Because programming is the art
of communicating intent to a person sacrificing simplicity in favour of
fast will make it hard to involve new people and educate and mentor them
into development of your project.

-   Correct: Does it behave correctly, handle all states and inputs
    correctly?
-   Simple: Is it easy to comprehend and follow for a human reader?
-   Fast: Is it performant?

