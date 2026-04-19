from typing import Callable, Literal, TypedDict, TypeGuard, get_args

type RawArgument = str

type ArgType_str = Literal['string', 'register', 'label']
class TypedArgument_str(TypedDict):
  argtype: ArgType_str
  value: str

type ArgType_int = Literal['int']
class TypedArgument_int(TypedDict):
  argtype: ArgType_int
  value: int

type ArgTypes = ArgType_str | ArgType_int
type TypedArgument = TypedArgument_str | TypedArgument_int

def isArgString(a: TypedArgument) -> TypeGuard[TypedArgument_str]:
  return a['argtype'] in ['string', 'register', 'label']

def isArgInt(a: TypedArgument) -> TypeGuard[TypedArgument_int]:
  return a['argtype'] == 'int'

type Modules = Literal['mc', 'std', 'lp']
DEFINED_MODULES: tuple[Modules] = get_args(Modules.__value__)

class TGLLine(TypedDict):
  module: Modules
  func: str
  args: list[TypedArgument]

type Sections = Literal['.data', '.bss', '.rodata', '.text']
DEFINED_SECTIONS: tuple[Sections] = get_args(Sections.__value__)

class CodeWrapper(TypedDict):
  before: list[str]
  after: list[str]

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

def isValueRegister(a: str) -> TypeGuard[Registers]:
  return a in REGISTER_LIST

type RegFamily = Literal['a', 'b', 'c', 'd', 'si', 'di', 'bp', 'sp', '8', '9', '10', '11', '12', '13', '14', '15', 'ip']

class RegFamilyList(TypedDict):
  b64: Registers
  b32: Registers
  b16: Registers
  b8: Registers | None
  b88: Registers | None

REGISTER_HIERARCHY: dict[RegFamily, RegFamilyList] = {
  'a': {
    'b64': 'rax',
    'b32': 'eax',
    'b16': 'ax',
    'b8': 'al',
    'b88': 'ah'
  },
  'b': {
    'b64': 'rbx',
    'b32': 'ebx',
    'b16': 'bx',
    'b8': 'bl',
    'b88': 'bh'
  },
  'c': {
    'b64': 'rcx',
    'b32': 'ecx',
    'b16': 'cx',
    'b8': 'cl',
    'b88': 'ch'
  },
  'd': {
    'b64': 'rdx',
    'b32': 'edx',
    'b16': 'dx',
    'b8': 'dl',
    'b88': 'dh'
  },
  'si': {
    'b64': 'rsi',
    'b32': 'esi',
    'b16': 'si',
    'b8': 'sil',
    'b88': None
  },
  'di': {
    'b64': 'rdi',
    'b32': 'edi',
    'b16': 'di',
    'b8': 'dil',
    'b88': None
  },
  'bp': {
    'b64': 'rbp',
    'b32': 'ebp',
    'b16': 'bp',
    'b8': 'bpl',
    'b88': None
  },
  'sp': {
    'b64': 'rsp',
    'b32': 'esp',
    'b16': 'sp',
    'b8': 'spl',
    'b88': None
  },
  '8': {
    'b64': 'r8',
    'b32': 'r8d',
    'b16': 'r8w',
    'b8': 'r8b',
    'b88': None
  },
  '9': {
    'b64': 'r9',
    'b32': 'r9d',
    'b16': 'r9w',
    'b8': 'r9b',
    'b88': None
  },
  '10': {
    'b64': 'r10',
    'b32': 'r10d',
    'b16': 'r10w',
    'b8': 'r10b',
    'b88': None
  },
  '11': {
    'b64': 'r11',
    'b32': 'r11d',
    'b16': 'r11w',
    'b8': 'r11b',
    'b88': None
  },
  '12': {
    'b64': 'r12',
    'b32': 'r12d',
    'b16': 'r12w',
    'b8': 'r12b',
    'b88': None
  },
  '13': {
    'b64': 'r13',
    'b32': 'r13d',
    'b16': 'r13w',
    'b8': 'r13b',
    'b88': None
  },
  '14': {
    'b64': 'r14',
    'b32': 'r14d',
    'b16': 'r14w',
    'b8': 'r14b',
    'b88': None
  },
  '15': {
    'b64': 'r15',
    'b32': 'r15d',
    'b16': 'r15w',
    'b8': 'r15b',
    'b88': None
  },
  'ip': {
    'b64': 'rip',
    'b32': 'eip',
    'b16': 'ip',
    'b8': None,
    'b88': None
  }
}


class InsertInstruction(TypedDict):
  op: None
  content: list[str]

class WriteToSectionInstruction(TypedDict):
  op: Literal['section']
  section: Sections
  content: list[str]


type Instruction = InsertInstruction | WriteToSectionInstruction

def isInsertInstruction(i: Instruction) -> TypeGuard[InsertInstruction]:
  return i['op'] is None

def isWriteToSectionInstruction(i: Instruction) -> TypeGuard[WriteToSectionInstruction]:
  return i['op'] == 'section'


type InstructionList = list[Instruction]


type ModuleExport = dict[str, Callable[[list[TypedArgument]], InstructionList]]

type ModuleTree = dict[Modules, ModuleExport]

class GlobalOptions(TypedDict):
  silent: bool
  dont_save_regs: bool
  dont_save_syscall: bool

class GlobalRegs(TypedDict):
  r1: RegFamilyList
  r2: RegFamilyList
  r3: RegFamilyList
  r4: RegFamilyList


REGS_SET_SYSCALL: GlobalRegs = {
  'r1': REGISTER_HIERARCHY['a'],
  'r2': REGISTER_HIERARCHY['di'],
  'r3': REGISTER_HIERARCHY['si'],
  'r4': REGISTER_HIERARCHY['d'],
}
REGS_SET_RSTART: GlobalRegs = {
  'r1': REGISTER_HIERARCHY['8'],
  'r2': REGISTER_HIERARCHY['9'],
  'r3': REGISTER_HIERARCHY['10'],
  'r4': REGISTER_HIERARCHY['11'],
}
REGS_SET_REND: GlobalRegs = {
  'r1': REGISTER_HIERARCHY['12'],
  'r2': REGISTER_HIERARCHY['13'],
  'r3': REGISTER_HIERARCHY['14'],
  'r4': REGISTER_HIERARCHY['15'],
}

type FileModeStr = Literal['R', 'W', 'RW']
FILE_MODES_STR = get_args(FileModeStr.__value__)
type FileModeInt = Literal[0, 1, 2]
FILE_MODES_INT = get_args(FileModeInt.__value__)

def isFilemode(s: str) -> TypeGuard[FileModeStr]:
  return s in FILE_MODES_STR

def filemode_convert(str_mode: FileModeStr) -> FileModeInt:
  return FILE_MODES_INT[FILE_MODES_STR.index(str_mode)]
