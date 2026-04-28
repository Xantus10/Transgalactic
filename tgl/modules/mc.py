from ..errors import TGLArgumentError, TGLNonexistentError
from ..globals import Global
from ..parse import checkArgTypes, strparse, toNASMByteSequence
from ..types import InstructionList, ModuleExport, TypedArgument, isArgString, isArgInt, filemode_convert, isFilemode

from .savestate import saveRegs, saveSyscallArgs, saveSyscallArgsExtended

### .data section macros

def defstr(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'defstr', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label', 'string']) or not isArgString(args[1]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'defstr', 'expected': ('label', 'string'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  return [
    {
      'op': None,
      'content': [
        f'{args[0]["value"]}_len equ {len(strparse(args[1]["value"]))}',
        f'{args[0]["value"]}: db {toNASMByteSequence(args[1]["value"])}'
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
        'mov rax, 1',
        'mov rdi, 1',
        f'lea rsi, [rel {args[0]["value"]}]',
        f'mov rdx, {args[0]["value"]}_len',
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
  if not isArgString(args[0]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'printdef', 'expected': ('string',), 'got': (args[0]['argtype'],)}, str(args))
  strid, isDefined = Global.getRandIdStr(args[0]['value'])
  if isDefined:
    return printdef_defined([{'argtype': 'label', 'value': strid}])
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


def mcprint(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'print', 'expected': 1, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'label': raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'print', 'expected': ('label',), 'got': (args[0]['argtype'],)}, str(args))
  wrap = saveSyscallArgs()
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'! std strlen {args[0]["value"]}',
        'mov rdx, rax',
        'mov rax, 1',
        'mov rdi, 1',
        f'lea rsi, [rel {args[0]["value"]}]',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def mcprintln(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'println', 'expected': 1, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'label': raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'println', 'expected': ('label',), 'got': (args[0]['argtype'],)}, str(args))
  wrap = saveSyscallArgs()
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'! std strlen {args[0]["value"]}',
        'mov rdx, rax',
        'mov rax, 1',
        'mov rdi, 1',
        f'lea rsi, [rel {args[0]["value"]}]',
        'mov byte [rsi + rdx], 10',
        'inc rdx',
        'syscall',
        'dec rdx',
        'mov byte [rsi + rdx], 0',
        *wrap['after']
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
        f'mov byte [{args[0]["value"]} + rax - 1], 0',
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
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'fopen', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['string', 'label']) or not isArgString(args[0]) or not isArgString(args[1]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'fopen', 'expected': ('string', 'label'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  if not isFilemode(args[1]['value']): raise TGLNonexistentError(f'Nonexistent filemode: {args[1]["value"]}', str(args))
  wrap = saveSyscallArgs('rax')
  filename, isDefined = Global.getRandIdStr(args[0]['value'])
  null_term = '\\0'+args[0]["value"][-1] if strparse(args[0]['value'])[-1] != '\0' else args[0]["value"][-1]
  defineInstruction: InstructionList = [] if isDefined else [{
      'op': 'section',
      'section': '.rodata',
      'content': [
        f'! mc defstr {filename}, {args[0]["value"][:-1]+null_term}'
      ]
    }]
  return [
    *defineInstruction,
    {
      'op': None,
      'content': [
        *wrap['before'],
        'mov rax, 2',
        f'lea rdi, [rel {filename}]',
        f'mov rsi, {filemode_convert(args[1]["value"])}',
        'xor rdx, rdx',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def fwrite_defined(args: list[TypedArgument]) -> InstructionList:
  wrap = saveSyscallArgs()
  length = ''
  strlen_snippet = []
  if len(args) == 3:
    length = args[2]['value']
  else:
    length = 'rax'
    strlen_snippet = [
      f'! std strlen {args[1]["value"]}'
    ]
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'mov rdi, {args[0]["value"]}',
        *strlen_snippet,
        f'mov rdx, {length}',
        'mov rax, 1',
        f'lea rsi, [rel {args[1]["value"]}]',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def fwrite(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'fwrite', 'expected': 2, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'register' or not isArgString(args[0]): raise TGLArgumentError(f'Invalid argument type for \'fwrite\' first argument (expected: (register), got: {args[0]})', str(args))
  if not isArgString(args[1]): raise TGLArgumentError(f'Invalid argument type for \'fwrite\' second argument (expected: (label OR string), got: {args[1]})', str(args))
  str_label, isDefined = Global.getRandIdStr(args[1]['value'])
  if args[1]['argtype'] == 'label':
    return fwrite_defined(args)
  elif args[1]['argtype'] == 'string':
    defineInstruction: InstructionList = [] if isDefined else [{
      'op': 'section',
      'section': '.rodata',
      'content': [
        f'! mc defstr {str_label}, {args[1]["value"]}'
      ]
    }]
    return defineInstruction + fwrite_defined([args[0], {'argtype': 'label', 'value': str_label}, {'argtype': 'label', 'value': f'{str_label}_len'}])
  raise TGLArgumentError(f'Invalid argument type for \'fwrite\' second argument (expected: (label OR string), got: {args[1]})', str(args))

def fread(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 3: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'fread', 'expected': 3, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['register', 'label', 'int']) or not isArgString(args[0]) or not isArgString(args[1]) or not isArgInt(args[2]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'fread', 'expected': ('register', 'label', 'int'), 'got': (args[0]['argtype'], args[1]['argtype'], args[2]['argtype'])}, str(args))
  wrap = saveSyscallArgs('rax')
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'mov rdi, {args[0]["value"]}',
        'mov rax, 0',
        f'lea rsi, [rel {args[1]["value"]}]',
        f'mov rdx, {args[2]["value"]}',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def fclose(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'fclose', 'expected': 1, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'register': raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'fclose', 'expected': ('register',), 'got': (args[0]['argtype'],)}, str(args))
  wrap = saveSyscallArgs()
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'mov rdi, {args[0]["value"]}',
        'mov rax, 3',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def fclear(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'fclear', 'expected': 1, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'string': raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'fclear', 'expected': ('string',), 'got': (args[0]['argtype'],)}, str(args))
  return [
    {
      'op': None,
      'content': [
        f'! mc fopen {args[0]["value"]}, W',
        '! mc fclose rax'
      ]
    }
  ]


def mmap(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'mmap', 'expected': 1, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'int': raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'mmap', 'expected': ('int',), 'got': (args[0]['argtype'],)}, str(args))
  wrap = saveSyscallArgsExtended('rax')
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        'mov rax, 9',
        'xor rdi, rdi',
        f'mov rsi, {args[0]["value"]*4096}',
        'mov rdx, 3',
        'mov r10, 34',
        'mov r8, -1',
        'xor r9, r9',
        'syscall',
        *wrap['after']
      ]
    }
  ]

def munmap(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'munmap', 'expected': 2, 'got': len(args)}, str(args))
  if not args[0]['argtype'] == 'register' or not (args[1]['argtype'] in ['int', 'label']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'munmap', 'expected': ('register', 'int'), 'got': (args[0]['argtype'], args[1]['argtype'])}, str(args))
  wrap = saveSyscallArgs()
  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'mov rdi, {args[0]["value"]}',
        'mov rax, 11',
        f'mov rsi, {args[1]["value"]*4096}'
        'syscall',
        *wrap['after']
      ]
    }
  ]


# Export
FUNCTIONS: ModuleExport = {
  'defstr': defstr,
  'resstr': resstr,
  'printdef': printdef,
  'exit': mcexit,
  'print': mcprint,
  'println': mcprintln,
  'inpdef': inpdef,
  'inp': inp,
  'strcp': strcp,
  'strncp': strncp,
  'time': time,
  'fopen': fopen,
  'fwrite': fwrite,
  'fread': fread,
  'fclose': fclose,
  'fclear': fclear
}
