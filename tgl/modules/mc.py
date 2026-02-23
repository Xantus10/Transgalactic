from typing import cast

from ..errors import TGLArgumentError
from ..globals import Global
from ..parse import checkArgTypes, strparse
from ..types import InstructionList, ModuleExport, TypedArgument

from .savestate import saveSyscallArgs

### .data section macros

def defstr(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'defstr', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'string']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'defstr', 'expected': ('label', 'string'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  return [
    {
      'section': None,
      'content': [
        f'{args[0]["value"]}_len equ {len(strparse(cast(str, args[1]["value"])))}',
        f'{args[0]["value"]}: db {args[1]["value"]}'
      ]
    }
  ]

### .bss section macros

def resstr(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'resstr', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'int']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'resstr', 'expected': ('label', 'int'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  if cast(int, args[1]['value']) < 0: raise TGLArgumentError(f'Cannot allocate negative size (got {args[1]["value"]})', str(args))
  return [
    {
      'section': None,
      'content': [
        f'{args[0]["value"]}_len equ {args[1]["value"]}',
        f'{args[0]["value"]}: resb {args[0]["value"]}_len'
      ]
    }
  ]

### .text section macros

def printdef_defined(args: list[TypedArgument]) -> InstructionList:
  wrap = saveSyscallArgs()
  return [
    {
      'section': None,
      'content': [
        *wrap['before'],
        'mov rax 1',
        'mov rdi 1',
        f'lea rsi [rel {args[0]["value"]}]',
        f'mov rdx {args[0]["value"]}_len',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def printdef_defname(args: list[TypedArgument]) -> InstructionList:
  if not checkArgTypes(args, ['label', 'string']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'printdef', 'expected': ('label', 'string'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  return [
    {
      'section': '.rodata',
      'content': [f'! mc defstr {args[0]["value"]},{args[1]["value"]}']
    },
    *printdef_defined([args[0]])
  ]

def printdef_rand(args: list[TypedArgument]) -> InstructionList:
  strid = Global.getRandId()
  return printdef_defname([{'argtype': 'label', 'value': strid}, args[0]])

def printdef(args: list[TypedArgument]) -> InstructionList:
  al = len(args)
  if al == 1:
    if args[0]['argtype'] == 'string':
      return printdef_rand(args)
    elif args[0]['argtype'] == 'label':
      return printdef_defined(args)
    raise TGLArgumentError(f'Invalid argument types for \'printdef\' (expected: (label OR string), got: {args[0]})', str(args))
  elif al == 2:
    return printdef_defname(args)
  raise TGLArgumentError(f'Invalid argument count for \'printdef\' (expected: 1 or 2, got: {al})', str(args))


def mcexit(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'exit', 'expected': 1, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'int': raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'exit', 'expected': ('int',), 'got': (args[0]['argtype'],)}, str(args))
  return [
    {
      'section': None,
      'content': [
        'mov rax, 60',
        f'mov rdi, {args[0]["value"]}',
        'syscall'
      ]
    }
  ]


# Export
FUNCTIONS: ModuleExport = {
  'defstr': defstr,
  'resstr': resstr,
  'printdef': printdef
}
