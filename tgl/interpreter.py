from .types import InstructionList, ModuleTree, TGLLine

from .modules.mc import FUNCTIONS as MC_FUNCTIONS


MODULE_TREE: ModuleTree = {
  'mc': MC_FUNCTIONS
}

def interpret(parsed_line: TGLLine) -> InstructionList:
  return MODULE_TREE[parsed_line['module']][parsed_line['func']](parsed_line['args'])
