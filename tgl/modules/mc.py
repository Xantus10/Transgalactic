from typing import cast

from ..errors import TGLArgumentError
from ..globals import Global
from ..parse import checkArgTypes, strparse
from ..types import InstructionList, ModuleExport, TypedArgument

from .savestate import saveSyscallArgs

### .data section macros

def defstr(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError(f'Invalid argument count for \'defstr\' (expected: 2, got: {len(args)})', str(args))
  if not checkArgTypes(args, ['label', 'string']): raise TGLArgumentError(f'Invalid argument types for \'defstr\' (expected: (label, string), got: {args})', str(args))
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
  if len(args) != 2: raise TGLArgumentError(f'Invalid argument count for \'resstr\' (expected: 2, got: {len(args)})', str(args))
  if not checkArgTypes(args, ['label', 'int']): raise TGLArgumentError(f'Invalid argument types for \'resstr\' (expected: (label, int), got: {args})', str(args))
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

def printdef(args: list[TypedArgument]) -> InstructionList:
  al = len(args)
  wrap = saveSyscallArgs()
  if al == 1:
    if args[0]['argtype'] == 'string':
      strid = Global.getRandId()
      return [
        {
          'section': '.rodata',
          'content': [f'! mc defstr {strid},{args[0]["value"]}']
        },
        {
          'section': None,
          'content': [
            *wrap['before'],
            'mov rax 1',
            'mov rdi 1',
            f'lea rsi [rel {strid}]',
            f'mov rdx {strid}_len',
            *wrap['after']
          ]
        }
      ]
    elif args[0]['argtype'] == 'label':
      return [
        {
          'section': None,
          'content': [
            *wrap['before'],
            'mov rax 1',
            'mov rdi 1',
            f'lea rsi [rel {args[0]["value"]}]',
            f'mov rdx {args[0]["value"]}_len',
            *wrap['after']
          ]
        }
      ]
    raise TGLArgumentError(f'Invalid argument types for \'printdef\' (expected: (label OR string), got: {args[0]})', str(args))
  elif al == 2:
    if not checkArgTypes(args, ['label', 'string']): raise TGLArgumentError(f'Invalid argument types for \'printdef\' (expected: (label, string), got: {args})', str(args))
    return [
      {
        'section': '.rodata',
        'content': [f'! mc defstr {args[0]["value"]},{args[1]["value"]}']
      },
      {
        'section': None,
        'content': [
          *wrap['before'],
          'mov rax 1',
          'mov rdi 1',
          f'lea rsi [rel {args[0]["value"]}]',
          f'mov rdx {args[0]["value"]}_len',
          *wrap['after']
        ]
      }
    ]
  raise TGLArgumentError(f'Invalid argument count for \'printdef\' (expected: 1 or 2, got: {al})', str(args))


FUNCTIONS: ModuleExport = {
  'defstr': defstr,
  'resstr': resstr,
  'printdef': printdef
}
