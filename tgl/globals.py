from uuid import uuid4
from re import match

from .errors import TGLIdentifierError, TGLSyntaxError
from .types import GlobalOptions

safeuuid = lambda: str(uuid4()).replace('-', '_')

class Global:
  _Prefix = 'TGL__' + safeuuid() + '_'
  _UsedLabels: list[str] = []

  options: GlobalOptions = {
    'silent': False
  }

  @staticmethod
  def overridePrefix(new_prefix: str):
    if not match('^[A-Za-z0-9_]+$', new_prefix): raise TGLSyntaxError('Prefix override uses invalid characters', new_prefix)
    Global._Prefix = new_prefix
  
  @staticmethod
  def getRawPrefix():
    return Global._Prefix.replace('_', '-')[:-1]

  @staticmethod
  def getGlobalIdFor(name: str):
    if name in Global._UsedLabels: raise TGLIdentifierError(f'Duplicit identifier \'{name}\'', name)
    Global._UsedLabels.append(name)
    return Global._Prefix + name

  @staticmethod
  def getLocalIdFor(name: str):
    return '.' + Global._Prefix + name
  
  @staticmethod
  def getRandId():
    return Global.getGlobalIdFor(safeuuid())
  
  @staticmethod
  def getRandIdFor(name: str):
    return Global.getRandId() + '_' + name
