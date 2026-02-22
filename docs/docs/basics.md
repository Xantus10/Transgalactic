# Basics of transgalactic

## Syntax in code

Transgalactic (TGL) works on a single line basis (Do not attempt to split a single command over multiple lines). You may add any form of indentation.

A TGL line may look like this:

`! mc defstr hello,"Hello, World!"  ; Define a string`

Let's disect this line!

### SOL (Start of line)

All TGL lines **MUST** begin with a lone `'!'`. Note that TGL might not catch it if you don't include it but your ASM will catch them.

The following is invalid:

 - `mc defstr` - No `'!'`
 - `!mc defstr` - No space after `'!'`

### Module

The word right after `'!'`, in our case the module name is `mc`, which stands for 'macros'

The whole functionality of TGL is hidden behind modules, each module has different inner workings and provides different functionalities.

### Function

The second word is the name of the function, in our case it's the function `defstr`

Modules export various functions, these functions decide how to change the ASM, what to add.

### Arguments

Functions take different arguments. When in doubt, check this documentation.

The arguments can be of following types:

| Name | Example | Explanation |
|------|---------|-------------|
| `string` | "Hello\n\0" | A simple string variable, enclosed in double quotes |
| `int` | 123 | An integer value |
| `label` | buffer | A label in code (code label, memory label) |
| `register` | rax | A register name |

In our example there are two arguments

1. A `label` named `hello`
2. A `string` with the value of `"Hello, World!"`

Arguments should always be separated by `','`, you may include whitespace around the `','`

### Comments

And lastly, as with any ASM code, `';'` marks the beginning of a comment.
