Can I cycle through operators in C?
===================================

A friend of mine who is learning to program asked me the following:

*"""
How do i cycle through operators in c?
If I want to try every version of + - * / on an equation, so printf("1 %operator 1", oneOfTheOperators);
Like I'd stick them in an array and iterate over the array incrementing on each iteration, but do you define an operator as? They aren't ints, floats etc
"""*

He's certainly on the way to the correct answer already. There are three key barriers to an answer.

.. more::

If you want to print literally:

::

    "1 + 1"
    "1 - 1"
    "1 / 1"
    "1 * 1"

This is the easy version. The operators here serve no purpose, they are merely characters.

First barrier:

My friend listed a python syntax for loop. We don't have these in C! In C we must iterate over a loop using the syntax:

::

    for (assignment; condition; action) {
    }

We need to know the size of the array, and we need to create a counter to loop over it. We need to iterate over an array of characters, until we have displayed them all. Here is my code to do this.

::

    #include <stdio.h>
    #include <stdint.h>

    int64_t
    main(size_t argc, char **argv)
    {
        /* Create the array of characters */
        char *ops[4] = {
            "+",
            "-",
            "/",
            "*",
        };
        int64_t x = 1;

        /* Because we know the array has 4 elements, we can iterate easily over this */
        for(size_t i = 0; i < 4; i++) {
            printf("%d %s %d\n", x, ops[i], x);
        }

    }

If we build and run this:

::

    # gcc -std=gnu99 -o test test.c
    # ./test

    1 + 1
    1 - 1
    1 / 1
    1 * 1

Now for the HARD version.

Say that we *literally* wanted to print the RESULTS of these 4 operations. 

The second barrier is that in C, we cannot easily convert a "string" into an executable unit of code. We cannot take "x + y", and then run eval on it, and have working code. So formatting the chars into a piece of code, then executing it won't work! We cannot use the printf style that was questioned here.

The third barrier is that because the operaters +,-,/,\* are not functions, they are key words, we cannot easily make an "array of operators". The compiler won't know what to do with them! However, C does allow us to make *fuction pointers*. These *can* be iterated over, just like our chars.

So for this version, we will make an array of function pointers, that each call one of the required operators.

::

    #include <stdio.h>
    #include <stdint.h>

    static int64_t
    add(const int64_t a, const int64_t b)
    {
        return a + b;
    }

    static int64_t
    sub(const int64_t a, const int64_t b)
    {
        return a - b;
    }

    static int64_t
    div(const int64_t a, const int64_t b)
    {
        return a / b;
    }

    static int64_t
    mult(const int64_t a, const int64_t b)
    {
        return a * b;
    }

    int64_t
    main(size_t argc, char **argv)
    {
        /*
         * The syntax for array of fptrs is not obvious at first.
         * int64_t  <<-- The return type
         * (*ops_ptrs <<-- the * signals this array will container pointers
         * [4]  <<-- allocate space for 4 elements.
         * (const int64_t a, const int64_t b) <<-- The signature of the
         *     arguments to the function pointers. All of them must have the
         *     same signature, else it will not compile!
         */
        int64_t (*ops_ptrs[4]) (const int64_t a, const int64_t b) = {
            add,
            sub,
            div,
            mult,
        };
        int64_t x = 1;

        /* Because we know the array has 4 elements, we can iterate easily over this */
        for(size_t i = 0; i < 4; i++) {
            /* The addition of the () invokes the call to the function pointer */
            uint64_t res = ops_ptrs[i](x, x);
            printf("%d -> %d\n", x, res);
        }

    }

Our output from this is:

::

    # gcc -std=gnu99 -o test test.c
    # ./test

    1 -> 2
    1 -> 0
    1 -> 1
    1 -> 1

There are probably improvements to make here in terms of making the output clearer, but that's an exercise for the reader. Happy coding!

PS:

Because this is C, any mistake with pointers will cause HORRIBLE things to happen.

::

    int64_t
    main(size_t argc, char **argv)
    {
        /* Create the array of function pointers, reffering to our above wrappers */
        int64_t (*ops_ptrs[4]) (const int64_t a, const int64_t b) = {
            add,
            NULL,
            NULL,
            NULL,
        };
        int64_t x = 1;
    ...

::

    # ./test
    1 -> 2
    zsh: segmentation fault (core dumped)

Pointers are powerful but it's EASY to shoot yourself in the foot!

.. author:: default
.. categories:: none
.. tags:: none
.. comments::
