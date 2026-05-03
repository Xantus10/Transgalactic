from ..errors import TGLArgumentError, TGLNonexistentError
from ..globals import Global
from ..parse import checkArgTypes, strparse, toNASMByteSequence
from ..types import InstructionList, ModuleExport, TypedArgument, isArgString, isArgInt, filemode_convert, isFilemode

from .savestate import saveRegs, saveSyscallArgs, saveSyscallArgsExtended


def init(args: list[TypedArgument]) -> InstructionList:
  if len(args) > 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'init', 'expected': 1, 'got': len(args)}, str(args))
  pagesize = 4096
  if len(args) == 1:
    if not isArgInt(args[0]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'init', 'expected': ('int',), 'got': (args[0]['argtype'],)}, str(args))
    pagesize = args[0]['value'] * 4096


  alChunkLabel, _ = Global.getGlobalIdFor('AllocChunk')
  frChunkLabel, _ = Global.getGlobalIdFor('FreeChunk')

  pagesizeLabel, _ = Global.getGlobalIdFor('PAGE_SIZE')
  flagPrevinuseLabel, _ = Global.getGlobalIdFor('FLAG_PREVINUSE')
  flagPrevinuseInvLabel, _ = Global.getGlobalIdFor('FLAG_PREVINUSE_INVERSE')
  flagsSpaceLabel, _ = Global.getGlobalIdFor('FLAGS_SPACE')
  flagsSpaceInvLabel, _ = Global.getGlobalIdFor('FLAGS_SPACE_INVERSE')

  headLabel, _ = Global.getGlobalIdFor('HEAD')
  curLabel, _ = Global.getGlobalIdFor('CUR')
  freeheadLabel, _ = Global.getGlobalIdFor('FREE_HEAD')
  
  initLabel, _ = Global.getGlobalIdFor('init')
  mallocLabel, _ = Global.getGlobalIdFor('malloc')
  freeLabel, _ = Global.getGlobalIdFor('free')

  return [
    {
      'op': 'section',
      'section': '.data',
      'content': []
    }
  ]

# Export
FUNCTIONS: ModuleExport = {
  'init': init
}
