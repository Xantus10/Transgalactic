from ..errors import TGLArgumentError
from ..globals import Global
from ..parse import checkArgTypes
from ..types import InstructionList, ModuleExport, TypedArgument, isArgString, isValueRegister, isArgInt



def for_loop(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 4: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'for', 'expected': 4, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['register', 'int', 'int', 'int']) or not isArgString(args[0]) or not isValueRegister(args[0]['value']) or not isArgInt(args[1]) or not isArgInt(args[2]) or not isArgInt(args[3]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'for', 'expected': ('register', 'int', 'int', 'int'), 'got': (args[0]['argtype'],args[1]['argtype'],args[2]['argtype'],args[3]['argtype'],)}, str(args))
  label = Global.getRandIdFor('for')
  Global.newLoop((args[0]['value'], label, args[2]['value'], args[3]['value']))

  return [
    {
      'op': None,
      'content': [
        f'mov {args[0]["value"]}, {args[1]["value"]}',
        f'{label}:'
      ]
    }
  ]

def end_for_loop(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 0: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'endfor', 'expected': 0, 'got': len(args)}, str(args))
  reg, label, final, change = Global.endLoop()

  jump_op = 'jl' if change > 0 else 'jg'

  return [
    {
      'op': None,
      'content': [
        f'add {reg}, {change}',
        f'cmp {reg}, {final}',
        f'{jump_op} {label}'
      ]
    }
  ]


def until(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 2: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'unt', 'expected': 2, 'got': len(args)}, str(args))
  if not checkArgTypes(args, ['register', 'int']) or not isArgString(args[0]) or not isValueRegister(args[0]['value']) or not isArgInt(args[1]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'unt', 'expected': ('register', 'int'), 'got': (args[0]['argtype'],args[1]['argtype'])}, str(args))
  label = Global.getRandIdFor('until')
  Global.newLoop((args[0]['value'], label, args[1]['value'], 0))

  return [
    {
      'op': None,
      'content': [
        f'{label}:'
      ]
    }
  ]

def end_until(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 0: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'endunt', 'expected': 0, 'got': len(args)}, str(args))
  reg, label, final, _ = Global.endLoop()

  return [
    {
      'op': None,
      'content': [
        f'cmp {reg}, {final}',
        f'jne {label}'
      ]
    }
  ]



# Export
FUNCTIONS: ModuleExport = {
  'for': for_loop,
  'endfor': end_for_loop,
  'unt': until,
  'endunt': end_until
}
