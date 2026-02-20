from typing import Literal, TypedDict, get_args

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


type Namespaces = Literal['mc', 'std']
DEFINED_NAMESPACES: tuple[Namespaces] = get_args(Namespaces.__value__)

class TGLLine(TypedDict):
  namespace: Namespaces
  func: str
  args: list[TypedArgument]

type Sections = Literal['.data', '.bss', '.rodata', '.text']
DEFINED_SECTIONS: tuple[Sections] = get_args(Sections.__value__)