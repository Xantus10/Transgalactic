from typing import Literal, Self, TypedDict

class TGLError(Exception):
  """
  Base class for Transgalactic errors
  """
  def __init__(self, msg: str, line: str) -> None:
    self.msg = msg
    self.line = line
  
  def printable(self) -> str:
    return f'''!!! TGL ERROR HAS OCCURRED !!!

{self.__class__.__name__}: {self.msg}

In the following context: {self.line}'''

class TGLSyntaxError(TGLError):
  """
  An error in the language syntax has occured

  This class is a base for more detailed errors
  """
  def __init__(self, msg: str, line: str) -> None:
    super().__init__(msg, line)

class TGLIdentifierError(TGLSyntaxError):
  """
  An invalid identifier was used

  Examples include:
    Invalid register name
    Invalid function call
    Invalid module
  """
  def __init__(self, msg: str, line: str) -> None:
    super().__init__(msg, line)


class _TGLArgumentErrorPreset_argcount(TypedDict):
  et: Literal['argcount']
  func_name: str
  expected: int
  got: int

class _TGLArgumentErrorPreset_argtypes(TypedDict):
  et: Literal['argtypes']
  func_name: str
  expected: tuple[str, ...]
  got: tuple[str, ...]

type _TGLArgumentErrorPreset = _TGLArgumentErrorPreset_argcount | _TGLArgumentErrorPreset_argtypes

class TGLArgumentError(TGLSyntaxError):
  """
  A mismatch in tgl function arguments (count, argument type)
  """
  def __init__(self, msg: str, line: str) -> None:
    super().__init__(msg, line)

  @classmethod
  def preset(cls, data: _TGLArgumentErrorPreset, line: str) -> Self:
    match data['et']:
      case 'argcount':
        return cls(f'Invalid argument count for \'{data["func_name"]}\' (expected: {data["expected"]}, got: {data["got"]})', line)
      case 'argtypes':
        return cls(f'Invalid argument types for \'{data["func_name"]}\' (expected: {data["expected"]}, got: {data["got"]})', line)
