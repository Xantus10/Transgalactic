# `dat` - Dynamic memory and data structures

Normally, this would not pose significant problems. I, however, wanted Transgalactic to be completely from scratch. This means I cannot use the libc `malloc`. In other words this module provides its own malloc with its own chunk management.

## `init`

```
init [SIZE]

int SIZE (optional) - Size to use for allocations

tags: syscall, regs[rax, rdi, rsi, rdx, r8, r9, r10], ret[rax]
```

The `init` function **must** be called before any other functions in the `dat` module.

This function internally calls `mc mmap` to allocate memory pages according to the desired `SIZE`. The `SIZE` should therefore align with the page size. Default value is `4096`.

**Important note**: The allocator is primitive. It **will not** allocate additional pages when it runs out of space. It is recommended to allocate more memory than you will use (Also the chunk metadata will take up a good portion of the page - `16 Bytes per chunk`)
