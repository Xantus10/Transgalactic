from typing import cast

from ..errors import TGLArgumentError
from ..parse import checkArgTypes, strparse
from ..types import InstructionList, ModuleExport, TypedArgument


def defstr(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError(f'Invalid argument count for \'defstr\' (expected: 2, got: {len(args)})', str(args))
  if not checkArgTypes(args, ['label', 'string']): raise TGLArgumentError(f'Invalid argument types for \'defstr\' (expected: (label, string), got: {args})', str(args))
  return [
    {
      'section': None,
      'content': [
        f'{args[0]["value"]}_len equ {len(strparse(cast(str, args[1]["value"])))}',
        f'{args[0]["value"]}: db {args[1]["value"]}'
      ]
    }
  ]

FUNCTIONS: ModuleExport = {
  'defstr': defstr
}
