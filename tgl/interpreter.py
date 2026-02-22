from .errors import TGLIdentifierError
from .types import InstructionList, ModuleTree, TGLLine

from .modules.mc import FUNCTIONS as MC_FUNCTIONS


MODULE_TREE: ModuleTree = {
  'mc': MC_FUNCTIONS
}

def interpret(parsed_line: TGLLine) -> InstructionList:
  if not parsed_line['func'] in MODULE_TREE[parsed_line['module']].keys(): raise TGLIdentifierError(f'Module \'{parsed_line['module']}\' does not expose function \'{parsed_line['func']}\'', str(parsed_line))
  return MODULE_TREE[parsed_line['module']][parsed_line['func']](parsed_line['args'])
