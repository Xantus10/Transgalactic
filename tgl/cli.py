import argparse

from .code import Code
from .errors import TGLError
from .globals import Global

def createParser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="tgl.py",
    description="Translate TGL enhanced ASM into pure NASM",
    epilog="For more info check out https://xantus10.github.io/Transgalactic/"
  )

  parser.add_argument(
    'input_file',
    help='Input filename'
  )

  parser.add_argument(
    '-o', '--output',
    dest='output_file',
    help='Output filename (defaults to TGL--{GLOBAL_PREFIX}.asm)'
  )

  parser.add_argument(
    '-s', '--silent',
    action='store_true',
    help='Program will not produce output'
  )

  advanced = parser.add_argument_group('Advanced options')

  advanced.add_argument(
    '--dont-save-regs',
    action='store_true',
    help='Do not perform register saving (Can break your code; Check the documentation)'
  )

  advanced.add_argument(
    '--global-prefix-override',
    help='Specify a custom global prefix to use instead of a random UUID'
  )

  return parser

def main():
  parser = createParser()
  args = parser.parse_args()
  
  try:
    if args.silent: Global.options['silent'] = True
    if args.dont_save_regs: Global.options['dont_save_regs'] = True
    if args.global_prefix_override: Global.overridePrefix(args.global_prefix_override)

    code = Code.loadFromFile(args.input_file)
    code.translateCode()
    code.saveToFile(args.output_file)
  except TGLError as e:
    if not Global.options['silent']: print(e.printable())
