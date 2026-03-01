from ..errors import TGLIdentifierError
from ..globals import Global
from ..types import CodeWrapper, Registers, REGISTER_LIST

def saveRegs(registers: list[Registers]) -> CodeWrapper:
  bef: list[str] = []
  aft: list[str] = []
  if Global.options['dont_save_regs']:
    return {
      'before': bef,
      'after': aft
    }
  for i in range(len(registers)):
    r = registers[i]
    if not r in REGISTER_LIST: raise TGLIdentifierError(f'Unsupported register \'{r}\'', '')
    bef.append(f'push {r}' + '\n')
    aft.append(f'pop {registers[-i-1]}')
  return {
    'before': bef,
    'after': aft
  }

save4regs = lambda: saveRegs(['rax', 'rbx', 'rcx', 'rdx'])
saveSyscallArgs = lambda: saveRegs(['rax', 'rdi', 'rsi', 'rdx'])
