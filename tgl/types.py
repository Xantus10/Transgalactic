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

class Instruction(TypedDict):
  section: Sections | None
  content: list[str]

type InstructionList = list[Instruction]

type ModuleExport = dict[str, Callable[[list[TypedArgument]], InstructionList]]

type ModuleTree = dict[Modules, ModuleExport]
