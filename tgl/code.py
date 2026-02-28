from typing import Self

from .errors import TGLIdentifierError
from .globals import Global
from .interpreter import interpret
from .parse import parseline
from .types import InstructionList, Sections, DEFINED_SECTIONS

class Code:
  def __init__(self, code: str):
    self.code = code.replace('\r', '').split('\n')
    self.sections: dict[Sections, int] = {}
    self.translated = False
    self.ix = -1
    self.findSections()

  @classmethod
  def loadFromFile(cls, filename: str) -> Self:
    with open(filename, 'r') as f:
      return cls(f.read())
  
  def saveToFile(self, filename: str | None):
    if not filename: filename = Global.getRawPrefix()
    with open(filename, 'w') as f:
      f.write('\n'.join(self.code))

  def findSections(self):
    for i, line in enumerate(self.code):
      spl = line.split()
      if len(spl) < 2: continue
      if spl[0] == 'section' and spl[1] in DEFINED_SECTIONS:
        self.sections[spl[1]] = i

  def incrementSectionIx(self, insertIndex: int, lineCount: int):
    for key, value in self.sections.items():
      if value >= insertIndex:
        self.sections[key] += lineCount
  
  def writeToIx(self, ix: int, data: list[str], overwriteLines: int = 0):
    self.code[ix:ix+overwriteLines] = data
    self.incrementSectionIx(ix, len(data)-overwriteLines)
  
  def createSection(self, section: Sections):
    if not section in DEFINED_SECTIONS: raise TGLIdentifierError(f'Section \'{section}\' is not recognized as a TGL working section and is not supported', '')
    nextSectionIx = DEFINED_SECTIONS.index(section) + 1
    placeIndex = len(self.code)
    while nextSectionIx < len(DEFINED_SECTIONS):
      if DEFINED_SECTIONS[nextSectionIx] in self.sections.keys():
        placeIndex = self.sections[DEFINED_SECTIONS[nextSectionIx]]
        break
    self.writeToIx(placeIndex, [f'section {section}'])
    self.sections[section] = placeIndex

  def writeToSection(self, section: Sections, data: list[str]):
    if not section in self.sections.keys():
      self.createSection(section)
      if self.ix != -1: self.ix += 1
    self.writeToIx(self.sections[section] + 1, data)
    if self.ix != -1: self.ix += len(data)

  def translateCode(self): # Remember: If you ever encounter an infinite loop, you are not erasing the original tgl command!
    while not self.translated:
      self.ix = 0
      self.translated = True
      for i, line in enumerate(self.code):
        self.ix = i
        par = parseline(line)
        if par:
          instructions = interpret(par)
          self.runInstructions(instructions)
        self.ix += 1

  def runInstructions(self, instructions: InstructionList):
    for inst in instructions:
      if not inst['section']:
        self.writeToIx(self.ix, inst['content'], overwriteLines=1)
      else:
        self.writeToSection(inst['section'], inst['content'])
        self.translated = False
