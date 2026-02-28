import argparse

from .code import Code
from .errors import TGLError
from .globals import Global

def createParser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(
    prog="Transgalactic",
    description="Extension for 64bit NASM",
    epilog="For more info check out https://xantus10.github.io/Transgalactic/"
  )

  parser.add_argument(
    'input',
    help='Input filename'
  )

  parser.add_argument(
    '-o', '--output',
    help='Output filename (defaults to TGL--{GLOBAL_PREFIX}.asm)'
  )

  parser.add_argument(
    '-s', '--silent',
    action='store_true',
    help='Program will not produce output'
  )

  parser.add_argument(
    '--global-prefix-override',
    help='Specify a custom global prefix to use instead of a random UUID'
  )

  return parser

def main():
  parser = createParser()
  args = parser.parse_args()
  
  try:
    if args.silent: Global.options['silent'] = True
    if args.global_prefix_override: Global.overridePrefix(args.global_prefix_override)

    code = Code.loadFromFile(args.input)
    code.translateCode()
    code.saveToFile(args.output)
  except TGLError as e:
    if not Global.options['silent']: print(e.printable())
