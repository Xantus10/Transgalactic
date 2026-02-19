from typing import Literal, Self

from .errors import IdentifierError

type Sections = Literal['.data', '.bss', '.rodata', '.text']
DEFINED_SECTIONS = ('.data', '.bss', '.rodata', '.text')

class Code:
  def __init__(self, code: str):
    self.code = code.replace('\r', '').split('\n')
    self.sections: dict[Sections, int] = {}
    self.findSections()

  @classmethod
  def loadFromFile(cls, filename: str) -> Self:
    with open(filename, 'r') as f:
      return cls(f.read())
  
  def saveToFile(self, filename: str):
    with open(filename, 'w') as f:
      f.write('\n'.join(self.code))

  def findSections(self):
    for i, line in enumerate(self.code):
      spl = line.split()
      if spl[0] == 'section' and spl[1] in DEFINED_SECTIONS:
        self.sections[spl[1]] = i

  def incrementSectionIx(self, insertIndex: int, lineCount: int):
    for key, value in self.sections.items():
      if value >= insertIndex:
        self.sections[key] += lineCount
  
  def writeToIx(self, ix: int, data: str, overwriteLines: int = 0):
    self.code[ix:ix+overwriteLines] = data.split('\n')
    self.incrementSectionIx(ix, data.count('\n')+1)
  
  def createSection(self, section: Sections):
    if not section in DEFINED_SECTIONS: raise IdentifierError(f'Section \'{section}\' is not recognized as a TGL working section and is not supported', '')
    nextSectionIx = DEFINED_SECTIONS.index(section) + 1
    placeIndex = len(self.code)
    while nextSectionIx < len(DEFINED_SECTIONS):
      if DEFINED_SECTIONS[nextSectionIx] in self.sections.keys():
        placeIndex = self.sections[DEFINED_SECTIONS[nextSectionIx]]
        break
    self.writeToIx(placeIndex, f'section {section}')
    self.sections[section] = placeIndex

  def writeToSection(self, section: Sections, data: str):
    if not section in self.sections.keys(): self.createSection(section)
    self.writeToIx(self.sections[section] + 1, data)
