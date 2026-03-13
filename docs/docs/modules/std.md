# `std` - Standard lib functions

The `std` module features reusable functions which it defines at the beginning of your .text section as you would with any normal procedures.

Here is the documentation for them

## Format

Format is basically the same as with mc. These modules really differ just in the reusability of `std` functions.

```
{name_of_fun} ARG1, ARG2

type ARG1 - First arg
type ARG2 - Second arg

tags: {List of tags}
```

### Tags

Tags are used to convey some sort of information.

The tags feature these:

 - `syscall` - this function performs a syscall
 - `regs[rdi, rsi, ...]` - this tag marks the used registers
 - `ret[rax]` - this tag marks the registers used to return values from macro


## `strlen`

```
strlen NAME

label NAME - the name of a string label

tags: regs[al, rdi, rsi], ret[rax]
```

This function will output the length of a **NULL terminated** string on the address specified by `NAME` and save the len in the RAX register.
