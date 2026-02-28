from typing import Callable, Literal, TypedDict, get_args

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


type Modules = Literal['mc', 'std']
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

class Instruction(TypedDict):
  section: Sections | None
  content: list[str]

type InstructionList = list[Instruction]

type ModuleExport = dict[str, Callable[[list[TypedArgument]], InstructionList]]

type ModuleTree = dict[Modules, ModuleExport]

class GlobalOptions(TypedDict):
  silent: bool
