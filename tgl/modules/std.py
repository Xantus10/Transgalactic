from ..errors import TGLArgumentError, TGLNonexistentError
from ..globals import Global
from ..parse import checkArgTypes
from ..types import InstructionList, ModuleExport, TypedArgument

from .savestate import saveRegs, saveSyscallArgs


def strlen(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'strncp', 'expected': 1, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'strlen', 'expected': ('label',), 'got': (args[0]['argtype'],)}, str(args))
  rax = Global.regs['r1']['b64']
  al = Global.regs['r1']['b8']
  rdi = Global.regs['r2']['b64']
  rsi = Global.regs['r3']['b64']
  if not al: raise TGLNonexistentError(f'Tried to use lower 8bit register of {rax}, which does not exist.', '')
  wrap = saveRegs([rdi, rsi])
  funlabel, isPresent = Global.getGlobalIdFor('strlen')
  funlabelfinish, _ = Global.getGlobalIdFor('strlen_finish')
  funBody: InstructionList = []
  if not isPresent:
    funBody = [
      {
        'op': 'section',
        'section': '.text',
        'content': [
          f'{funlabel}:',
          f'mov {al}, [{rdi}]',
          f'test {al}, {al}',
          f'jz {funlabelfinish}',
          f'inc {rdi}',
          f'jmp {funlabel}',
          f'{funlabelfinish}:',
          f'sub {rdi}, {rsi}',
          f'mov rax, {rdi}',
          'ret'
        ]
      }
    ]
  funCall: InstructionList = [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'lea {rsi}, [rel {args[0]["value"]}]',
        f'mov {rdi}, {rsi}',
        f'call {funlabel}',
        *wrap['after']
      ]
    }
  ]
  return funCall + funBody

# Non exportable code snippet for str to int conversion
# Accept: input number in {rax}
# Give: address to string in {rdi}
def str_to_int_conversion() -> InstructionList:
  rdi = Global.regs['r2']['b64']
  rsi = Global.regs['r3']['b64']
  sil = Global.regs['r3']['b8']
  if not sil: raise TGLNonexistentError(f'Tried to use lower 8bit register of {rsi}, which does not exist.', '')
  wrap = saveRegs(['rdx', rsi, 'rcx'])
  funlabel, isPresent = Global.getGlobalIdFor('strtoint_conversion')
  if isPresent: return []
  bufferlabel, _ = Global.getGlobalIdFor('strtoint_buffer')
  funlabelzero, _ = Global.getGlobalIdFor('strtoint_zero')
  funlabelpositive, _ = Global.getGlobalIdFor('strtoint_positive')
  funlabeldone, _ = Global.getGlobalIdFor('strtoint_done')
  funlabelfin, _ = Global.getGlobalIdFor('strtoint_fin')
  return [
    {
      'op': 'section',
      'section': '.bss',
      'content': [
        f'! mc resstr {bufferlabel}, 22'
      ]
    },
    {
      'op': 'section',
      'section': '.text',
      'content': [
        f'{funlabel}:',
        *wrap['before'],
        f'lea {rdi}, [rel {bufferlabel}+{bufferlabel}_len-1]',
        'mov rcx, 10',
        f'mov byte [{rdi}], 0',
        f'dec {rdi}',
        f'mov {sil}, 0',
        'cmp rax, 0',
        f'je {funlabelzero}',
        f'jg {funlabelpositive}',
        f'mov {sil}, \'-\'',
        'neg rax',
        f'jmp {funlabelpositive}',
        f'{funlabelzero}:',
        f'mov byte [{rdi}], \'0\'',
        f'dec {rdi}',
        f'jmp {funlabeldone}',
        f'{funlabelpositive}:',
        'xor rdx, rdx',
        'div rcx',
        'add dl, \'0\'',
        f'mov byte [{rdi}], dl',
        f'dec {rdi}',
        'test rax, rax',
        f'jnz {funlabelpositive}',
        f'{funlabeldone}:',
        f'mov byte [{rdi}], {sil}',
        f'test {sil}, {sil}',
        f'jnz {funlabelfin}',
        f'inc {rdi}',
        f'{funlabelfin}:',
        *wrap['after'],
        'ret'
      ]
    }
  ]

def printint(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'printint', 'expected': 1, 'got': len(args)}, str(args))
  if not args[0]['argtype'] in ['register', 'int']: raise TGLArgumentError(f'Invalid argument type for \'printint\' (expected: (register OR int), got: {args[0]})', str(args))
  str_int_conv_definition = str_to_int_conversion()
  funlabel, _ = Global.getGlobalIdFor('strtoint_conversion')
  bufferlabel, _ = Global.getGlobalIdFor('strtoint_buffer')
  rdi = Global.regs['r2']['b64']
  wrap = saveRegs([rdi])
  syscallWrap = saveSyscallArgs()
  return [
    *str_int_conv_definition,
    {
      'op': None,
      'content': [
        *wrap['before'],
        *syscallWrap['before'],
        f'mov rax, {args[0]["value"]}',
        f'call {funlabel}',
        f'mov rsi, {rdi}',
        f'lea rax, [rel {bufferlabel}]',
        f'sub {rdi}, rax',
        f'mov rax, {bufferlabel}_len',
        f'sub rax, {rdi}',
        'dec rax',
        'mov rdx, rax',
        'mov rax, 1',
        'mov rdi, 1',
        'syscall'
      ]
    }
  ]


FUNCTIONS: ModuleExport = {
  'strlen': strlen,
  'printint': printint
}
