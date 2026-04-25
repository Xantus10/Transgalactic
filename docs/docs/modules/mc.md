# `mc` - Macros

The `mc` module functions are the simplest you can find in TGL. They are basically just a fancy way of doing find + replace.

Here is the documentation for them

## Format

```
{name_of_macro} ARG1, ARG2

type ARG1 - First arg
type ARG2 - Second arg

tags: {List of tags}
```

### Tags

Tags are used to convey some sort of information.

The tags feature these:

 - `syscall` - this macro performs a syscall
 - `regs[rdi, rsi, ...]` - this tag marks the used registers (`wr1/2/3/4` marks a dynamic register you define with `--work-regs-set`)
 - `ret[rax]` - this tag marks the registers used to return values from macro


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

tags: syscall, regs[rax, rdi, rsi, rdx]
```

This will define the string under a random identifier and add ASM code to print it. This is for one-time prints of constant strings.

### Print and define

```
printdef NAME, STR_VAL

label NAME - the label to define the string under
string STR_VAL - the string to print

tags: syscall, regs[rax, rdi, rsi, rdx]
```

Useful when you want to re-use the string in other parts of the code.

Note: Consider using `defstr` for better readability and code structure.

### Print already defined

```
printdef NAME

label NAME - the defined label to print

tags: syscall, regs[rax, rdi, rsi, rdx]
```

This function ASSUMES that you defined a label `NAME` and now you want to use it.

Note: This function also assumes the existence of a `NAME_len` assembler constant which it uses for the string length. (If you wish to print a dynamic string, check out `mc print`)

## `exit`

```
exit CODE

int CODE - Exit code of the program

tags: syscall, regs[rax, rdi]
```

Make a syscall to SYS_EXIT with the corresponding return code.

## `print`

```
print NAME

label NAME - Label pointing to a NULL terminated string

tags: syscall, regs[rax, rdi, rsi, rdx], uses[std strlen]
```

Print a dynamic string. This function dynamically determines the length using the `std strlen` function (The string needs to be NULL terminated).

## `println`

```
println NAME

label NAME - Label pointing to a NULL terminated string

tags: syscall, regs[rax, rdi, rsi, rdx], uses[std strlen]
```

Print a dynamic string. This function dynamically determines the length using the `std strlen` function (The string needs to be NULL terminated). This function automatically appends a `\n` at the end of the string. (The original string is not changed)

## `inpdef`

```
inpdef NAME, SIZE

label NAME - the name of the bss variable
int SIZE - size to reserve and input (in bytes)

tags: syscall, regs[rax, rdi, rsi, rdx]
```

This macro defines a `.bss` variable with the label `NAME` and defines the asm constant `NAME_len` with the value of `SIZE`. Then calls the stdin syscall and appends a NULL byte at the end + strips the trailing `\n`.

## `inp`

```
inp NAME

label NAME - the name of the bss variable

tags: syscall, regs[rax, rdi, rsi, rdx]
```

This macro assumes the existence of the `.bss` variable `NAME` and the asm constant `NAME_len`. Then calls the stdin syscall and appends a NULL byte at the end + strips the trailing `\n`.

## `strcp`

```
strcp FROM, TO

label FROM - the source string
label TO - the destination string

tags: regs[wr1, wr2, wr3]
```

This macro will copy the contents of the `FROM` string into the `TO` string.

Note: **The FROM string must be NULL terminated**

## `strncp`

```
strcp FROM, TO, LEN

label FROM - the source string
label TO - the destination string
int LEN - max characters to copy

tags: regs[wr1, wr2, wr3, wr4]
```

This macro will copy the contents of the `FROM` string into the `TO` string. It can also safeguard agains overflow with the LEN parameter.

Note: **The FROM string must be NULL terminated**

## `time`

```
time

tags: syscall, regs[rax, rdi], ret[rax]
```

Get the current UNIX timestamp in the RAX register.

Note: The value in RAX will be overwritten!

## `fopen`

```
fopen FILENAME, MODE

string FILENAME - Filename/path to open
label MODE - Filemode (accepts values R / W / A)

tags: syscall, regs[rax, rdi, rsi, rdx], ret[rax]
```

Open the specified file and return a file descriptor in RAX.

Note: The mode is a literal value, not string (notice the absence of `""`): `! mc fopen "file.txt", RW`

## `fwrite`

```
fwrite FD, CONTENT

register FD - The register currently containing the file descriptor
label/string CONTENT - The string content to write

tags: syscall, regs[rax, rdi, rsi, rdx]
```

Perform a `SYS_WRITE` call to write to the file descriptor. If using the label for `CONTENT`, the string must be NULL terminated (since its length is determined dynamically using strlen).

## `fread`

```
fread FD, DEST, LEN

register FD - The register currently containing the file descriptor
label DEST - The destination label
int LEN - How many bytes to read

tags: syscall, regs[rax, rdi, rsi, rdx], ret[rax]
```

Read content from a file and return the number of bytes read in RAX. This macro does NOT create the buffer.

## `fclose`

```
fread FD

register FD - The register currently containing the file descriptor

tags: syscall, regs[rax, rdi]
```

Close the file descriptor.

## `fclear`

```
fclear FILENAME

string FILENAME - Filename/path to open

tags: syscall, regs[rax, rdi, rsi, rdx]
```

Clear the desired file.

Note: Just calls `fopen(filename, W)`, followed by `fclose()`.
