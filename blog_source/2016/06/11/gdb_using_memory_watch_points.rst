GDB: Using memory watch points
==============================

While programming, we've all seen it.

"Why the hell is that variable set to 1? It should be X!"

A lot of programmers would stack print statements around till the find the issue. Others, might look at function calls.

But in the arsenal of the programmer, is the debugger. Normally, the debugger, is really overkill, and too complex to really solve a lot of issues. But while trying to find an issue like this, it shines.

All the code we are about to discuss is `in the liblfdb git <https://github.com/Firstyear/liblfdb>`_

.. more::

First, we need a repeatable test case that triggers the fault. For me I am developing a B+Tree, and I was noticing that in the struct of a node, that the node id was being changed from 1 -> 0 incorrectly. Additionally, is_leaf was changing from 1 -> 0 also.

::

    #define B_FACTOR 3
    #define B_LINKS 4

    struct lfdb_bptree_node {
        uint64_t checksum;
        struct lfdb_bptree_node * nodes[B_LINKS];
        uint64_t keys[B_FACTOR];
        void * values[B_FACTOR];
        size_t value_sizes[B_FACTOR];
        uint64_t id;
        uint16_t is_leaf;
        uint16_t item_count;
    };

So we have to work out *why* the value of id and is_leaf is changing.

Looking at our code, the first place the root node of the B+Tree is created is here:

::

    lfdb_result
    lfdb_bptree_init(struct lfdb_bptree_instance **binst_ptr) {
        ....
        (*binst_ptr)->root = lfdb_malloc(sizeof(struct lfdb_bptree_node));


When we have that, at the "first" initialisation of the variable, we want to grab a pointer to it. We break on lfdb_bptree_init, and hit next a few times til after the malloc (you could break by line number also):

::

    (gdb) print &((*binst_ptr)->root->id)
    $45 = (uint64_t *) 0x60c00000baa8

Now with that address, we want to set a hardware watch on *any* change to that memory address:

::

    (gdb) watch *0x60c00000baa8
    Hardware watchpoint 8: *0x60c00000baa8

When the application is executing if any cpu alters the value of the address 0x60c00000baa8, it will trigger a break. Lo and behold:

::

    (gdb) cont
    Continuing.
    test_9_insert_fill_and_split: PASS: Created new binst
    Hardware watchpoint 8: *0x60c00000baa8

    Old value = 1
    New value = 0
    lfdb_bptree_copy_node_data (node=node@entry=0x60c00000ba40, target=3, source =source@entry=2) at src/lfdb_bptree.c:63
    63      }
    (gdb) bt
    #0  lfdb_bptree_copy_node_data (node=node@entry=0x60c00000ba40, target=3, source=source@entry=2) at src/lfdb_bptree.c:63
    #1  0x00007ffff6c69c16 in lfdb_bptree_insert_node (node=0x60c00000ba40, key=key@entry=1, value=value@entry=0x0, value_size=value_size@entry=0) at src/lfdb_bptree.c:102
    #2  0x00007ffff6c69cf8 in lfdb_bptree_insert (binst=binst@entry=0x60200000ef10, key=key@entry=1, value=value@entry=0x0, value_size=value_size@entry=0) at src/lfdb_bptree.c:128
    #3  0x0000000000400d51 in test_9_insert_fill_and_split (binst=0x60200000ef10) at test/test_bptree.c:201
    #4  0x0000000000400e54 in test_x_wrapper (test_name=test_name@entry=0x4012c0 "test_9_insert_fill_and_split", fn=fn@entry=0x400cd0 <test_9_insert_fill_and_split>, display=1) at test/test_bptree.c:67
    #5  0x0000000000400998 in main (argc=<optimized out>, argv=<optimized out>) at test/test_bptree.c:244


We can see that the value of 0x60c00000baa8, AKA binst_ptr->root was set from 1 to 0, at line 63 of src/lfdb_bptree.c.

At this point, we now try to determine *why* this occurs.

We can see that the change is in lfdb_bptree_copy_node_data, which is taking the contents of a key / values array from the node, and moving it to another key / values along inside the node.

::

    void
    lfdb_bptree_copy_node_data(struct lfdb_bptree_node *node, size_t target, size_t source)
    {
        node->keys[target] = node->keys[source];
        node->values[target] = node->values[source];
        node->value_sizes[target] = node->value_sizes[source];
    }

If we look at the call signature we can see the target and source within the node:

::

    lfdb_bptree_copy_node_data (node=node@entry=0x60c00000ba40, target=3, source=source@entry=2) at src/lfdb_bptree.c:63

But remember! Our keys / values array is only the size of B_FACTOR, which here is 3. given target is 3, and how C array addressing is 0 indexed, this means we are over-running the end of the array! But C will happily allow us to just keep writing to memory, which in this case, are the values of id and is_leaf.

Going up the frames we can see we are in the function lfdb_bptree_insert_node, and if we look there we see:

::

    lfdb_result
    lfdb_bptree_insert_node(struct lfdb_bptree_node *node, uint64_t key, void *value, size_t value_size) {
    ...
            for (size_t i = 0; i < node->item_count; i += 1) {
                if ( key < node->keys[i] ) {
                    // Push all other elements to the right, and insert here.
                    for (int j = (node->item_count + 1); j > i; j -= 1) {
                        lfdb_bptree_copy_node_data(node, j, j - 1);
                    }
                    lfdb_bptree_insert_node_data(node, i, key, value, value_size);



In this case, because of an off by one, allowing a write to an array to over-run to the next int in the struct. Here is the patch to fix it

::

    --- a/src/lfdb_bptree.c
    +++ b/src/lfdb_bptree.c
    @@ -98,7 +98,7 @@ lfdb_bptree_insert_node(struct lfdb_bptree_node *node, uint64_t key, void *value
             for (size_t i = 0; i < node->item_count; i += 1) {
                 if ( key < node->keys[i] ) {
                     // Push all other elements to the right, and insert here.
    -                for (int j = (node->item_count + 1); j > i; j -= 1) {
    +                for (int j = node->item_count; j > i; j -= 1) {
                         lfdb_bptree_copy_node_data(node, j, j - 1);
                     }
                     lfdb_bptree_insert_node_data(node, i, key, value, value_size);


Without the watchpoint, it would have taken much longer to isolate the potentially erroneous code. The debugger has allowed us to isolate a smaller scope to investigate, leading to a faster resolution.

Remember, not all issues are best solved with gdb: But there are times when gdb really does make life much easier to the developer.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
