from typing import Callable, cast, TypedDict

from ..code import Sections
from ..errors import TGLArgumentError
from ..parse import checkArgTypes, strparse, TypedArgument

class Instruction(TypedDict):
  section: Sections | None
  content: str

def defstr(args: list[TypedArgument]) -> list[Instruction]:
  if len(args) != 2: raise TGLArgumentError(f'Invalid argument count for \'defstr\' (expected: 2, got: {len(args)})', '')
  if not checkArgTypes(args, ['label', 'string']): raise TGLArgumentError(f'Invalid argument types for \'defstr\' (expected: (label, string), got: {args})', '')
  return [
    {
      'section': '.rodata',
      'content': f'{args[0]["value"]}_len equ {len(strparse(cast(str, args[1]["value"])))}' + '\n' + f'{args[0]["value"]}: db {args[1]["value"]}'
    }
  ]

FUNCTIONS: dict[str, Callable[[list[TypedArgument]], list[Instruction]]] = {
  'defstr': defstr
}
