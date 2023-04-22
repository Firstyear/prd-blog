+++
title = "Transactional Operations in Rust"
date = 2021-11-14
slug = "2021-11-14-transactional_operations_in_rust"
# This is relative to the root!
aliases = [ "2021/11/14/transactional_operations_in_rust.html" ]
+++
# Transactional Operations in Rust

Earlier I was chatting to Yoshua, the author of this [async
cancellation](https://blog.yoshuawuyts.com/async-cancellation-1/) blog
about the section on halt-safety. The blog is a great read so I highly
recommend it! The section on halt-safety is bang on correct too, but I
wanted to expand on this topic further from what they have written.

## Memory Safety vs Application Safety

Yoshua provides the following code example in their blog:

    // Regardless of where in the function we stop execution, destructors will be
    // run and resources will be cleaned up.
    async fn do_something(path: PathBuf) -> io::Result<Output> {
                                            // 1. the future is not guaranteed to progress after instantiation
        let file = fs::open(&path).await?;  // 2. `.await` and 3. `?` can cause the function to halt
        let res = parse(file).await;        // 4. `.await` can the function to halt
        res                                 // 5. execution has finished, return a value
    }

In the example, we can see that at each await point the async behaviour
could cause the function to return. This would be similar to the
non-async code of:

    fn do_something(path: PathBuf) -> io::Result<Output> {
        let file = fs::open(&path)?;  // 1. `?` will return an Err if present
        let res = parse(file);        //
        res                           // 2. res may be an Err at this point.
    }

In this example we can see that both cancelation *or* and Err condition
could both cause our function to return, regardless of async or not. In
this example, since there are no side-effects, it\'s not a big deal, but
let\'s consider a different example that does have side-effects:

    fn do_something(path: PathBuf, files_read_counter: &Mutex<u64>) -> io::Result<Output> {
        let mut guard = files_read_counter.lock();
        let file = fs::open(&path)?;  // 1. `?` will return an Err if present
        guard += 1;                   //
        let res = parse(file);        //
        res                           // 2. res may be an Err at this point.
    }

This is a nonsensical example, but it illustrates the point. The files
read is incremented *before* we know that the success occured. Even
though this is memory safe, it\'s created an inconsistent data point
that is not reflective of the true state. It\'s trivial to resolve when
we look at this (relocation of the guard increment), but in a larger
example it may not be as easy:

    // This is more psuedo rust vs actual rust for simplicities sake.
    fn do_something(...) -> Result<..., ...> {
        let mut guard = map.lock();
        guard
            .values_mut()
            .try_for_each(|(k, v)| {
                v.update(...)
            })
    }

In our example we have a fallible value update function, which is inside
our locked datastructure. It would be very simple to see a situation
where while updating some values, an error is encountered somewhere into
the set, and then an Err returned. But what happens to the entries we
*did* update? Since we return from the Err here, the guard will be
dropped, and the lock successfully released, meaning that we have only
partially updated our map in this situation. This kind of behaviour can
still be defended against as a programmer, but it requires us as humans
to bear this cognitive load to ensure our application is behaving
safely. This is the difference between memory and application safety.

## Databases

Databases have confronted this problem for many decades now, and a key
logical approach is ACID compliance:

-   Atomicity - each operation is a single unit that fails or succeeds
    together
-   Consistency - between each unit, the data always moves from a valid
    state to another valid state
-   Isolation - multiple concurrent operations should behave as though
    they are executed in serial
-   Durability - the success of a unit is persisted in the event of
    future errors IE power-loss

For software, we tend to care more for ACI in this example, but of
course if we are writing a database in Rust, it would be important to
consider D.

When we look at our examples from before, these both fail the atomicity
and consistency checks (but they are correctly isolated due to the mutex
which enforces serialisation).

## ACID in Software

If we treat a top level functional call as our outer operation, and the
inner functions as the units comprising this operation, then we can
start to look at calls to functions as a transactional entity, where the
call to a single operation either succeeds or fails, and the functions
within that are [unsafe]{.title-ref} (aka [spicy]{.title-ref} 🌶 ) due to
the fact they can create inconsistent states. We want to write our
functions in a way that [spicy]{.title-ref} functions can only be
contained within operations and creates an environment where either the
full operation succeeds or fails, and then ensures that consistency is
maintained.

An approach that can be used is software transactional memory. There are
multiple ways to structure this, but copy-on-write is a common technique
to achieve this. An example of a copy-on-write cell type is in
[concread](https://crates.io/crates/concread). This type allows for ACI
(but not D) compliance.

Due to the design of this type, we can seperate functions that are
acquiring the guard (operations) and the functions that comprise that
operation as they are a passed a transaction that is in progress. For
example:

    // This is more psuedo rust vs actual rust for simplicities sake.
    fn update_map(write_txn: &mut WriteTxn<Map<..., ...>>) -> Result<..., ...> {
        write_txn
            .values_mut()
            .try_for_each(|(k, v)| {
                v.update(...)
            })
    }

    fn do_something(...) -> Result<..., ...> {
        let write_txn = data.write();
        let res = update_map(write_txn)?;
        write_txn.commit();
        Ok(res)
    }

Here we can already see a difference in our approach. We know that for
update_map to be called we must be within a transaction - we can not
\"hold it wrong\", and the compiler checks this for us. We can also see
that we invert drop on the write_txn guard from \"implicit commit\" to a
drop being a rollback operation. The commit only occurs *explicitly* and
takes ownership of the write_txn preventing it being used any further
without a new transaction. As a result in our example, if update_map
were to fail, we would implicitly rollback our data.

Another benefit in this example is async, thread and concurrency safety.
While the write_txn is held, no other writes can proceed (serialised).
Readers are also isolated and guaranteed that their data will not
chainge for the duration of that operation (until a new read is
acquired). Even in our async examples, we would be able to correctly
rollback during an async cancelation or error condition.

## Future Work

At the moment the copy on write structures in concread only can protect
single datastructures, so for more complex data type you end up with a
struct containing many transactional cow types. There is some work going
on to allow the creation of a manager that can allow arbitary structures
of multiple datatypes to be protected under a single transaction
manager, however this work is extremely [unsafe]{.title-ref} though due
to the potential for memory safety violations with incorrect
construction of the structures. For more details see the [concread
internals](https://docs.rs/concread/0.2.19/concread/internals/index.html)
, [concread linear
cowcell](https://docs.rs/concread/0.2.19/concread/internals/lincowcell/trait.LinCowCellCapable.html)
and, [concread impl
lincowcell](https://github.com/kanidm/concread/blob/master/src/internals/bptree/cursor.rs#L76)

## Conclusion

Within async and sync programming, we can have cancellations or errors
at any time - ensuring our applications are consistent in the case of
errors which *will* happen, is challenging. By treating our internal
APIs as a transactional interface, and applying database techniques we
can create systems that are \"always consistent\". It is possible to
create these interfaces in a way that the Rust compiler can support us
through it\'s type system to ensure we are using the correct
transactional interfaces as we write our programs - helping us to move
from just memory safety to broader application safety.

