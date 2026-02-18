from re import match
from shlex import shlex
from typing import Literal, TypedDict

from .errors import IdentifierError, SyntaxError

type RawArgument = str

class TypedArgument_str(TypedDict):
  argtype: Literal['string', 'register', 'label']
  value: str

class TypedArgument_int(TypedDict):
  argtype: Literal['int']
  value: int

type TypedArgument = TypedArgument_str | TypedArgument_int

type Namespaces = Literal['mc', 'std']
DEFINED_NAMESPACES = ('mc', 'std')

class TGLLine(TypedDict):
  namespace: Namespaces
  func: str
  args: list[TypedArgument]


REGISTER_LIST = [
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
      res.append({'argtype': 'string', 'value': strparse(arg)})
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
  if len(spl) < 3: raise SyntaxError('Too few words', line)
  if not spl[1] in DEFINED_NAMESPACES: raise IdentifierError(f'\'{spl[1]}\' is not a valid namespace', line)
  return {'namespace': spl[1], 'func': spl[2], 'args': typeargs(
    argparse(' '.join(spl[3:]))
  )}
  
