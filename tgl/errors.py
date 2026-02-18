
class TGLError(Exception):
  def __init__(self, msg: str, line: str) -> None:
    self.msg = msg
    self.line = line
  
  def printable(self) -> str:
    return f'''!!! TGL ERROR HAS OCCURRED !!!

{self.__class__.__name__}: {self.msg}

In the following context: {self.line}'''

class SyntaxError(TGLError):
  def __init__(self, msg: str, line: str) -> None:
    super().__init__(msg, line)

class IdentifierError(TGLError):
  def __init__(self, msg: str, line: str) -> None:
    super().__init__(msg, line)