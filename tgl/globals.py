from uuid import uuid4
from re import match

from .errors import TGLSyntaxError, TGLLoopSyntaxError
from .types import GlobalOptions, GlobalRegs, Registers, REGS_SET_SYSCALL

safeuuid = lambda: str(uuid4()).replace('-', '_')

class Global:
  _Prefix = 'TGL__' + safeuuid() + '_'
  _UsedLabels: list[str] = []

  options: GlobalOptions = {
    'silent': False,
    'dont_save_regs': False,
    'dont_save_syscall': False
  }

  _LoopQueue: list[tuple[Registers, str, int, int]] = []

  regs: GlobalRegs = REGS_SET_SYSCALL

  @staticmethod
  def overridePrefix(new_prefix: str):
    if not match('^[A-Za-z0-9_]+$', new_prefix): raise TGLSyntaxError('Prefix override uses invalid characters', new_prefix)
    Global._Prefix = new_prefix
  
  @staticmethod
  def getRawPrefix():
    return Global._Prefix.replace('_', '-')[:-1]

  @staticmethod
  def getGlobalIdFor(name: str):
    isPresent = True
    if not name in Global._UsedLabels:
      Global._UsedLabels.append(name)
      isPresent = False
    return (Global._Prefix + name, isPresent)

  @staticmethod
  def getLocalIdFor(name: str):
    return '.' + Global._Prefix + name
  
  @staticmethod
  def getRandId():
    return Global.getGlobalIdFor(safeuuid())[0]
  
  @staticmethod
  def getRandIdFor(name: str):
    return Global.getRandId() + '_' + name
  
  @staticmethod
  def newLoop(args: tuple[Registers, str, int, int]):
    Global._LoopQueue.append(args)

  @staticmethod
  def endLoop():
    if len(Global._LoopQueue) == 0: raise TGLLoopSyntaxError('Redundant loop end', '')
    return Global._LoopQueue.pop()
  
  @staticmethod
  def _checkLoopEnds():
    if len(Global._LoopQueue) != 0: raise TGLLoopSyntaxError('Loop without end', '')

  @staticmethod
  def checkFinalStatus():
    Global._checkLoopEnds()
  
