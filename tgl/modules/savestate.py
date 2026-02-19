from typing import Literal, TypedDict, get_args

from ..errors import TGLIdentifierError

class CodeWrapper(TypedDict):
  before: str
  after: str

type Registers = Literal[
    # RAX family
    "rax", "eax", "ax", "al", "ah",
    
    # RBX family
    "rbx", "ebx", "bx", "bl", "bh",
    
    # RCX family
    "rcx", "ecx", "cx", "cl", "ch",
    
    # RDX family
    "rdx", "edx", "dx", "dl", "dh",
    
    # RSI family
    "rsi", "esi", "si", "sil",
    
    # RDI family
    "rdi", "edi", "di", "dil",
    
    # RBP family
    "rbp", "ebp", "bp", "bpl",
    
    # RSP family
    "rsp", "esp", "sp", "spl",
    
    # R8–R15 families
    "r8",  "r8d",  "r8w",  "r8b",
    "r9",  "r9d",  "r9w",  "r9b",
    "r10", "r10d", "r10w", "r10b",
    "r11", "r11d", "r11w", "r11b",
    "r12", "r12d", "r12w", "r12b",
    "r13", "r13d", "r13w", "r13b",
    "r14", "r14d", "r14w", "r14b",
    "r15", "r15d", "r15w", "r15b",
    
    # Instruction pointer
    "rip", "eip", "ip"
]

REGISTER_LIST: tuple[Registers] = get_args(Registers.__value__)

def saveRegs(registers: list[Registers]) -> CodeWrapper:
  bef = ''
  aft = ''
  for i in range(len(registers)):
    r = registers[i]
    if not r in REGISTER_LIST: raise TGLIdentifierError(f'Unsupported register \'{r}\'', '')
    bef += f'push {r}' + '\n'
    aft += f'pop {registers[-i-1]}'
  return {
    'before': bef,
    'after': aft
  }

save4regs = lambda: saveRegs(['rax', 'rbx', 'rcx', 'rdx'])
saveSyscallArgs = lambda: saveRegs(['rax', 'rdi', 'rsi', 'rdx'])
