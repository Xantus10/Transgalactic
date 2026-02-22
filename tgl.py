from tgl.code import Code
from tgl.errors import TGLError

try:
  c = Code.loadFromFile('test.asm')
  c.translateCode()
  c.saveToFile('tgl_test.asm')
except TGLError as e:
  print(e.printable())
