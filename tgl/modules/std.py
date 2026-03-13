from ..errors import TGLArgumentError, TGLNonexistentError
from ..globals import Global
from ..parse import checkArgTypes
from ..types import InstructionList, ModuleExport, TypedArgument

from .savestate import saveRegs


def strlen(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'strncp', 'expected': 1, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['label']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'strlen', 'expected': ('label',), 'got': (args[0]['argtype'],)}, str(args))
  rax = Global.regs['r1']['b64']
  al = Global.regs['r1']['b8']
  rdi = Global.regs['r3']['b64']
  rsi = Global.regs['r2']['b64']
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
          f'mov {rax}, {rdi}'
        ]
      }
    ]
  funCall: InstructionList = [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'lea {rsi}, [rel {args[0]}]',
        f'mov {rdi}, {rsi}',
        *wrap['after']
      ]
    }
  ]
  return funCall + funBody



FUNCTIONS: ModuleExport = {
  'strlen': strlen
}
