import argparse

from .code import Code
from .errors import TGLError
from .globals import Global
from .types import REGS_SET_SYSCALL, REGS_SET_RSTART, REGS_SET_REND

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
    help='Do not perform register saving for non syscall macros (Can break your code; Check the documentation)'
  )

  advanced.add_argument(
    '--work-regs-set',
    dest='regs_set',
    choices=['SYSCALL', 'RSTART', 'REND'],
    help='The registers set macros will operate on'
  )

  advanced.add_argument(
    '--dont-save-syscall',
    action='store_true',
    help='Do not perform register saving for syscall macros (Can break your code; Check the documentation)'
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
    if args.dont_save_syscall: Global.options['dont_save_syscall'] = True
    if args.global_prefix_override: Global.overridePrefix(args.global_prefix_override)
    match args.regs_set:
      case 'SYSCALL':
        Global.regs = REGS_SET_SYSCALL
      case 'RSTART':
        Global.regs = REGS_SET_RSTART
      case 'REND':
        Global.regs = REGS_SET_REND
      case _: pass

    code = Code.loadFromFile(args.input_file)
    code.translateCode()
    code.saveToFile(args.output_file)
  except TGLError as e:
    if not Global.options['silent']: print(e.printable())
