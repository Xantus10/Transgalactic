from re import match
from shlex import shlex
from typing import Literal, TypedDict, get_args

from .errors import TGLIdentifierError, TGLSyntaxError
from .modules.savestate import REGISTER_LIST

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


def argparse(s: str) -> list[RawArgument]:
  lex = shlex(s, posix=False)
  lex.whitespace = ','
  lex.whitespace_split = True
  lex.escape = '\\'
  lex.commenters = ';'
  return [arg.strip() for arg in lex]

def strparse(s: str) -> str:
  assert s[0] in ['"', "'"]
  assert s[-1] in ['"', "'"]
  i = 1
  parsed = ""
  while i < (len(s)-1):
    c = s[i]
    if c == '\\':
      i += 1
      c = s[i]
      if c.isdigit():
        num = ''
        while c.isdigit():
          num += c
          i += 1
          c = s[i]
        i -= 1
        parsed += chr(int(num))
      elif c == 'n':
        parsed += '\n'
      elif c == 'a':
        parsed += '\a'
      elif c == 'b':
        parsed += '\b'
      elif c == 'f':
        parsed += '\f'
      elif c == 'r':
        parsed += '\r'
      elif c == 't':
        parsed += '\t'
      elif c == 'v':
        parsed += '\v'
      else:
        parsed += c
    else:
      parsed += c
    i += 1
  return parsed

def typeargs(args: list[RawArgument]) -> list[TypedArgument]:
  res: list[TypedArgument] = []
  for arg in args:
    if arg[0] in ['"', "'"]:
      res.append({'argtype': 'string', 'value': arg})
    elif match(r'^[\+\-]?\d+$', arg):
      res.append({'argtype': 'int', 'value': int(arg)})
    elif match(r'0x[A-Fa-f0-9]+', arg):
      res.append({'argtype': 'int', 'value': int(arg[2:], 16)})
    elif arg in REGISTER_LIST:
      res.append({'argtype': 'register', 'value': arg})
    else:
      res.append({'argtype': 'label', 'value': arg})
  return res

def parseline(line: str) -> TGLLine | None:
  spl = line.split()
  if len(spl) < 1: return None
  if spl[0] != '!': return None
  if len(spl) < 3: raise TGLSyntaxError('Too few words', line)
  if not spl[1] in DEFINED_NAMESPACES: raise TGLIdentifierError(f'\'{spl[1]}\' is not a valid namespace', line)
  return {'namespace': spl[1], 'func': spl[2], 'args': typeargs(
    argparse(' '.join(spl[3:]))
  )}

def checkArgTypes(args: list[TypedArgument], check: list[ArgTypes]) -> bool:
  for i in range(len(args)):
    if args[i]['argtype'] != check[i]: return False
  return True
