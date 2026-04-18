from re import match
from shlex import shlex

from .errors import TGLIdentifierError, TGLSyntaxError, TGLValueError
from .types import ArgTypes, FileModeInt, RawArgument, TGLLine, TypedArgument, DEFINED_MODULES, FILE_MODES_INT, FILE_MODES_STR, REGISTER_LIST



def argparse(s: str) -> list[RawArgument]:
  lex = shlex(s, posix=False)
  lex.whitespace += ','
  lex.whitespace_split = False
  lex.escape = '\\'
  lex.commenters = ';'
  return [arg.strip() for arg in lex]

def strparse(s: str) -> str:
  assert s[0] in ['"', "'"]
  assert s[-1] in ['"', "'"]
  assert s[0] == s[-1]
  i = 1
  parsed = ""
  while i < (len(s)-1):
    c = s[i]
    if c == '\\':
      i += 1
      c = s[i]
      if c == 'n':
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
      elif c in '0123456789abcdefABCDEFx':
        num = ''
        base = 10
        if c == 'x':
          base = 16
          i += 1
          c = s[i]
        while c in '0123456789abcdefABCDEF':
          num += c
          i += 1
          c = s[i]
        i -= 1
        parsed += chr(int(num, base))
      else:
        parsed += c
    else:
      parsed += c
    i += 1
  return parsed

def toNASMByteSequence(s: str):
  assert s[0] in ['"', "'"]
  assert s[-1] in ['"', "'"]
  assert s[0] == s[-1]
  i = 0
  parsed = ''
  while i < len(s):
    c = s[i]
    if c == '\\':
      parsed += '",'
      i += 1
      c = s[i]
      if c == 'n':
        parsed += str(ord('\n'))
      elif c == 'a':
        parsed += str(ord('\a'))
      elif c == 'b':
        parsed += str(ord('\b'))
      elif c == 'f':
        parsed += str(ord('\f'))
      elif c == 'r':
        parsed += str(ord('\r'))
      elif c == 't':
        parsed += str(ord('\t'))
      elif c == 'v':
        parsed += str(ord('\v'))
      elif c in '0123456789abcdefABCDEFx':
        num = ''
        base = 10
        if c == 'x':
          base = 16
          i += 1
          c = s[i]
        while c in '0123456789abcdefABCDEF':
          num += c
          i += 1
          c = s[i]
        i -= 1
        parsed += str(int(num, base))
      else:
        parsed += c
      parsed += ',"'
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
    elif match(r'0o[0-7]+', arg):
      res.append({'argtype': 'int', 'value': int(arg[2:], 8)})
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
  if not spl[1] in DEFINED_MODULES: raise TGLIdentifierError(f'\'{spl[1]}\' is not a valid module', line)
  return {'module': spl[1], 'func': spl[2], 'args': typeargs(
    argparse(' '.join(spl[3:]))
  )}

def checkArgTypes(args: list[TypedArgument], check: list[ArgTypes]) -> bool:
  for i in range(len(args)):
    if args[i]['argtype'] != check[i]: return False
  return True


## Special values convertors


def toFileModeInt(mode: str) -> FileModeInt:
  if not mode in FILE_MODES_STR: raise TGLValueError(f'Invalid mode of operation: {mode}', f'{mode=}')
  return FILE_MODES_INT[FILE_MODES_STR.index(mode)]
