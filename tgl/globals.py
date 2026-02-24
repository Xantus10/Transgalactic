from uuid import uuid4

from .errors import TGLIdentifierError

safeuuid = lambda: str(uuid4()).replace('-', '_')

class Global:
  _Prefix = 'TGL__' + safeuuid() + '_'
  _UsedLabels: list[str] = []

  @staticmethod
  def overridePrefix(new_prefix: str):
    Global._Prefix = new_prefix

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
