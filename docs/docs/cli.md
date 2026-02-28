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

### `--global-prefix-override GLOBAL_PREFIX_OVERRIDE`

By default Transgalactic uses a random UUIDv4 for label names to avoid name conflicts. You may use this option to override this behavior and instead use your own prefix (note that the prefix must abide by the rules for label names for NASM).

Example: Creating global label name for `strlen`

Default prefix: `TGL__a3db3421_8f10_418d_8751_f6b8aa46c186_strlen`

Using `--global-prefix-override HELLO_` results in: `HELLO_strlen`
