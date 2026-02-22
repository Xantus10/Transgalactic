# `mc` - Macros

The `mc` module functions are the simplest you can find in TGL. They are basically just a fancy way of doing find + replace.

Here is the documentation for them

## .data section

## `defstr`

```
defstr NAME, STR_VALUE

label NAME - the name to define
string STR_VALUE - a string value to define
```

This macro deines the given string under the given label and should be used in `.data` and `.rodata` sections. It also defines an assembler constant in the format `NAME_len`, which holds the string length.

## .bss section

## `resstr`

```
resstr NAME, SIZE

label NAME - the name of the bss label
int SIZE - size to reserve (in bytes)
```

This macro reserves space for a string under the given label and should be used in `.bss` section. It also defines an assembler constant in the format `NAME_len`, which holds the given size.

## .text section

## `printdef`

Stands for *print and define* or *print already defined*. This macro can take different arguments.

### Just print string

```
printdef STR_VAL

string STR_VAL - the string to print
```

This will define the string under a random identifier and add ASM code to print it. This is for one-time prints of constant strings.

### Print and define

```
printdef NAME, STR_VAL

label NAME - the label to define the string under
string STR_VAL - the string to print
```

Useful when you want to re-use the string in other parts of the code.

Note: Consider using `defstr` for better readability and code structure.

### Print already defined

```
printdef NAME

label NAME - the defined label to print
```

This function ASSUMES that you defined a label `NAME` and now you want to use it.

Note: This function also assumes the existence of a `NAME_len` assembler constant which it uses for the string length. (If you wish to print a dynamic string, check out `std print`)
