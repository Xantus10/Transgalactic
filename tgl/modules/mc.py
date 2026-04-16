from ..errors import TGLArgumentError, TGLNonexistentError
from ..globals import Global
from ..parse import checkArgTypes, strparse
from ..types import InstructionList, ModuleExport, TypedArgument, isArgString, isArgInt, filemode_convert, isFilemode

from .savestate import saveRegs, saveSyscallArgs

### .data section macros

def defstr(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'defstr', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'string']) or not isArgString(args[1]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'defstr', 'expected': ('label', 'string'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  return [
    {
      'op': None,
      'content': [
        f'{args[0]["value"]}_len equ {len(strparse(args[1]["value"]))}',
        f'{args[0]["value"]}: db {args[1]["value"]}'
      ]
    }
  ]

### .bss section macros

def resstr(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'resstr', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'int']) or not isArgInt(args[1]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'resstr', 'expected': ('label', 'int'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  if args[1]['value'] < 0: raise TGLArgumentError(f'Cannot allocate negative size (got {args[1]["value"]})', str(args))
  return [
    {
      'op': None,
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
      'op': None,
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
      'op': 'section',
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
      'op': None,
      'content': [
        'mov rax, 60',
        f'mov rdi, {args[0]["value"]}',
        'syscall'
      ]
    }
  ]


def inp(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'inp', 'expected': 1, 'got': len(args)}, str(args))
  if args[0]['argtype'] != 'label': raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'inp', 'expected': ('label',), 'got': (args[0]['argtype'],)}, str(args))
  wrap = saveSyscallArgs()
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        'mov rax, 0',
        'mov rdi, 0',
        f'lea rsi, [rel {args[0]["value"]}]',
        f'mov rdx, {args[0]["value"]}_len',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def inpdef(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'inpdef', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'int']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'inpdef', 'expected': ('label', 'int'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  return [
    {
      'op': 'section',
      'section': '.bss',
      'content': [f'! mc resstr {args[0]["value"]},{args[1]["value"]}']
    },
    *inp([args[0]])
  ]

def strcp(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'strcp', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'label']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'strcp', 'expected': ('label', 'label'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  rax = Global.regs['r1']
  rdi = Global.regs['r2']['b64']
  rsi = Global.regs['r3']['b64']
  al = rax['b8']
  if not al: raise TGLNonexistentError(f'Tried to use lower 8bit register of {rax["b64"]}, which does not exist.', '')
  wrap = saveRegs([rax['b64'], rdi, rsi])
  label = Global.getRandIdFor('strcp')
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'lea {rsi}, [rel {args[0]["value"]}]',
        f'lea {rdi}, [rel {args[1]["value"]}]',
        f'{label}:',
        f'mov {al}, [{rsi}]',
        f'mov byte [{rdi}], {al}',
        f'inc {rsi}',
        f'inc {rdi}',
        f'test {al}, {al}',
        f'jnz {label}',
        *wrap['after']
      ]
    }
  ]

def strncp(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 3: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'strncp', 'expected': 3, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'label', 'label']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'strncp', 'expected': ('label', 'label', 'label'), 'got': (args[0]['argtype'], args[1]['argtype'], args[2]['argtype'])}, str(args))
  rax = Global.regs['r1']
  rdi = Global.regs['r2']['b64']
  rsi = Global.regs['r3']['b64']
  rdx = Global.regs['r4']['b64']
  al = rax['b8']
  if not al: raise TGLNonexistentError(f'Tried to use lower 8bit register of {rax["b64"]}, which does not exist.', '')
  wrap = saveRegs([rax['b64'], rdi, rsi, rdx])
  label = Global.getRandIdFor('strncp')
  labeldone = Global.getRandIdFor('strncp_done')
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'lea {rsi}, [rel {args[0]["value"]}]',
        f'lea {rdi}, [rel {args[1]["value"]}]',
        f'xor {rdx}, {rdx}',
        f'{label}:',
        f'cmp {rdx}, {args[2]["value"]}',
        f'je {labeldone}',
        f'mov {al}, [{rsi}]',
        f'mov byte [{rdi}], {al}',
        f'inc {rsi}',
        f'inc {rdi}',
        f'inc {rdx}',
        f'test {al}, {al}',
        f'jnz {label}',
        f'{labeldone}:',
        *wrap['after']
      ]
    }
  ]


def time(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 0: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'time', 'expected': 0, 'got': len(args)}, str(args))
  rdisave = saveSyscallArgs('rax')
  return [
    {
      'op': None,
      'content': [
        *rdisave['before'],
        'mov rax, 201',
        'xor rdi, rdi',
        'syscall',
        *rdisave['after']
      ]
    }
  ]


def fopen(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 0: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'fopen', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['string', 'label']) or not isArgString(args[0]) or not isArgString(args[1]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'fopen', 'expected': ('string', 'label'), 'got': (args[0]['argtype'],args[1]['argtype'])}, str(args))
  if not isFilemode(args[1]['value']): raise TGLNonexistentError(f'Nonexistent filemode: {args[1]["value"]}', str(args))
  rdisave = saveSyscallArgs('rax')
  filename, _ = Global.getRandIdFor('filename')
  return [
    {
      'op': 'section',
      'section': '.rodata',
      'content': [
        f'! mc defstr {filename}, {args[0]["value"]}'
      ]
    },
    {
      'op': None,
      'content': [
        *rdisave['before'],
        'mov rax, 2',
        f'lea rdi, [rel {filename}]',
        f'mov rsi, {filemode_convert(args[1]["value"])}',
        'xor rdx, rdx',
        'syscall',
        *rdisave['after']
      ]
    }
  ]




# Export
FUNCTIONS: ModuleExport = {
  'defstr': defstr,
  'resstr': resstr,
  'printdef': printdef,
  'exit': mcexit,
  'inpdef': inpdef,
  'inp': inp,
  'strcp': strcp,
  'strncp': strncp,
  'time': time,
  'fopen': fopen
}
