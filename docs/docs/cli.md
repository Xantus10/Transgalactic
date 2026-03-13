# Usage from CLI

## Running the program

You may run the Transgalactic python script using the following:

1. Run `python tgl.py`
2. Run `python -m tgl`
3. On linux you may simply type `./tgl.py`

You always have to pass the input filename in the CLI.

`tgl.py myprogram.asm`

## Basic options

### `-h` or `--help`

Print the help message.

### `-o` or `--output OUTPUT_FILE`

You may specify the output file name. If this option is not used, the filename will be `TGL--{GLOBAL_PREFIX}.asm`.

### `-s` or `--silent`

The program will not output any info messages or errors.


## Advanced options

The following options interact with Transgalactic on a prime level and may cause errors if mishandled.

### Regsiters modification options

Transgalactic functions have to modify registers. In order to not break your program the registers are always saved using `push` and then restored using `pop`. This is so you don't have to juggle the values from the registers, however it creates some overhead (results in inefficient and ugly ASM). The following flags modify this behavior.

Note: for functions that return a value, the return register is not saved

#### `--dont-save-regs`

This flag will disable the register saving for every macro except those marked by the `syscall` tag. (It is meant to be used in combination with `--work-regs-set`)

#### `--work-regs-set REGS_SET`

This option allows you to choose which registers tgl will operate on. It is recommended you choose a set of registers that you will not use and then combine with `--dont-save-regs`.

The values are as follows:

 - `SYSCALL` - `RAX, RDI, RSI, RDX` (default)
 - `ALPH` - `RAX, RBX, RCX, RDX`
 - `RSTART` - `R8, R9, R10, R11`
 - `REND` - `R12, R13, R14, R15`

#### `--dont-save-syscall`

This flag disables saving the registers for `syscall` tagged macros. In combination with `--dont-save-regs`, you essentially completely turn off all register saving procedures. This means that you yourself are responsible for maintaining the correct values in your program.

If you choose to do so, then you might want to work in the R8-R15 register range for your tasks and not invade the syscall registers as much as possible.

You can also choose to not save registers if your whole program uses Transgalactic (so you are not doing anything in raw ASM).

### Other options

#### `--global-prefix-override GLOBAL_PREFIX_OVERRIDE`

By default Transgalactic uses a random UUIDv4 for label names to avoid name conflicts. You may use this option to override this behavior and instead use your own prefix (note that the prefix must abide by the rules for label names for NASM).

Example: Creating global label name for `strlen`

Default prefix: `TGL__a3db3421_8f10_418d_8751_f6b8aa46c186_strlen`

Using `--global-prefix-override HELLO_` results in: `HELLO_strlen`
