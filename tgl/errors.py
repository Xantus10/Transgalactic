
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

class TGLArgumentError(TGLSyntaxError):
  """
  A mismatch in tgl function arguments (count, argument type)
  """
  def __init__(self, msg: str, line: str) -> None:
    super().__init__(msg, line)
