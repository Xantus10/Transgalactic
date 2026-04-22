from ..errors import TGLIdentifierError
from ..globals import Global
from ..types import CodeWrapper, Registers, REGISTER_LIST

def _saveRegs(registers: list[Registers]) -> CodeWrapper:
  bef: list[str] = []
  aft: list[str] = []
  for i in range(len(registers)):
    r = registers[i]
    if not r in REGISTER_LIST: raise TGLIdentifierError(f'Unsupported register \'{r}\'', '')
    bef.append(f'push {r}' + '\n')
    aft.append(f'pop {registers[-i-1]}')
  return {
    'before': bef,
    'after': aft
  }


def saveRegsFunction(registers: list[Registers]):
  return _saveRegs(registers)


def saveRegs(registers: list[Registers]):
  if Global.options['dont_save_regs']:
    return _saveRegs([])
  return _saveRegs(registers)


def saveSyscallArgs(ret: Registers | None = None):
  if Global.options['dont_save_syscall']:
    return _saveRegs([])
  sys: list[Registers] = ['rax', 'rdi', 'rsi', 'rdx']
  if ret in sys: sys.remove(ret)
  return _saveRegs(sys)


def saveSyscallArgsExtended(ret: Registers | None = None):
  if Global.options['dont_save_syscall']:
    return _saveRegs([])
  sys: list[Registers] = ['rax', 'rdi', 'rsi', 'rdx', 'r8', 'r9', 'r10']
  if ret in sys: sys.remove(ret)
  return _saveRegs(sys)
