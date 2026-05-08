from ..errors import TGLArgumentError, TGLNonexistentError
from ..globals import Global
from ..parse import checkArgTypes, strparse, toNASMByteSequence
from ..types import InstructionList, ModuleExport, TypedArgument, isArgString, isValueRegister, isArgInt, filemode_convert, isFilemode

from .savestate import saveRegs, saveSyscallArgs, saveSyscallArgsExtended


def init(args: list[TypedArgument]) -> InstructionList:
  if len(args) > 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'init', 'expected': 1, 'got': len(args)}, str(args))
  pagesize = 4096
  if len(args) == 1:
    if not isArgInt(args[0]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'init', 'expected': ('int',), 'got': (args[0]['argtype'],)}, str(args))
    pagesize = args[0]['value']

  rax = Global.regs['r1']['b64']
  rdi = Global.regs['r2']['b64']
  rsi = Global.regs['r3']['b64']
  rdx = Global.regs['r4']['b64']

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
  ll_lookfor = Global.getRandIdFor('ll_lookfor')
  ll_addfreech = Global.getRandIdFor('ll_addfreech')
  ll_removefreech = Global.getRandIdFor('ll_removefreech')
  mallocLabel, _ = Global.getGlobalIdFor('malloc')
  freeLabel, _ = Global.getGlobalIdFor('free')

  return [
    {
      'op': 'section',
      'section': '.data',
      'content': [
        f'struc {alChunkLabel}', # AllocChunk struc
        '.prev_size resq 1',
        '.size resq 1',
        'endstruc',
        f'struc {frChunkLabel}', # FreeChunk struc
        '.prev_size resq 1',
        '.size resq 1',
        '.prev resq 1',
        '.next resq 1',
        'endstruc',
        f'{pagesizeLabel} equ {pagesize}', # ASM constants
        f'{flagsSpaceLabel} equ 15',
        f'{flagsSpaceInvLabel} equ -16',
        f'{flagPrevinuseLabel} equ 1',
        f'{flagPrevinuseInvLabel} equ -2',
        f'{headLabel}: dq 0', # Global variables
        f'{curLabel}: dq 0',
        f'{freeheadLabel}: dq 0'
      ]
    },
    {
      'op': 'section',
      'section': '.text',
      'content': [
        f'{initLabel}:', # Init func
        f'! mc mmap PAGE_SIZE',
        f'mov qword [rel {headLabel}], rax',
        f'mov qword [rel {curLabel}], rax',
        'ret',
        f'{ll_lookfor}:', # LL look_for
        f'mov {rdi}, [rel {freeheadLabel}]',
        '.start:'
        'jz .end',
        f'cmp [{rdi} + {frChunkLabel}.size], rax',
        'jge .end',
        f'mov {rdi}, [{rdi} + {frChunkLabel}.next]',
        'jmp .start',
        '.end:',
        'ret',
        f'{ll_addfreech}:', # LL add_free_chunk
        f'mov {rax}, [rel {freeheadLabel}]',
        f'test {rax}, -1',
        'jz .no_head',
        f'mov qword [{rax} + {frChunkLabel}.prev], {rdi}',
        '.no_head:',
        f'mov qword [{rdi} + {frChunkLabel}.prev], 0',
        f'mov qword [{rdi} + {frChunkLabel}.next], rax',
        'ret',
        f'{ll_removefreech}:', # LL remove_free_chunk
        f'mov {rdx}, [{rdi} + {frChunkLabel}.prev]',
        f'mov {rsi}, [{rdi} + {frChunkLabel}.next]',
        f'test {rdx}, {rdx}',
        'jnz .not_first',
        f'test {rsi}, {rsi}',
        'jz .single',
        f'mov qword [{rsi} + {frChunkLabel}.prev], 0',
        '.single:',
        'ret',
        '.not_first:',
        f'test {rsi}, {rsi}',
        'jnz .not_last',
        f'mov qword [{rdx} + {frChunkLabel}.next], 0',
        'ret',
        '.not_last:',
        f'mov qword [{rdx} + {frChunkLabel}.next], {rsi}',
        f'mov qword [{rsi} + {frChunkLabel}.next], {rdx}',
        'ret',
        f'{mallocLabel}:', # malloc - size in RAX
        f'mov {rdi}, [rel {curLabel}]',
        f'lea {rdi}, [{rdi} + {alChunkLabel}_size*2]',
        f'add {rdi}, {rax}',
        f'mov {rsi}, [rel {headLabel}]',
        f'add {rsi}, {pagesizeLabel}',
        f'cmp {rdi}, {rsi}',
        'jge .free_list_fallback',
        f'mov {rdi}, [rel {curLabel}]',
        f'mov qword [{rdi}], 0',
        f'lea {rsi}, [{rdi} + {alChunkLabel}.size]',
        f'mov {rdx}, [{rsi}]',
        f'and {rdx}, {flagsSpaceLabel}',
        f'or {rdx}, {rax}',
        f'cmp {rdi}, [rel {headLabel}]',
        'jne .not_first',
        f'or {rdx}, {flagPrevinuseLabel}',
        '.not_first:',
        f'mov qword [{rsi}], {rdx}'
        f'lea {rsi}, [{rdi} + {alChunkLabel}_size + {rax}]',
        f'mov qword [rel {curLabel}], {rsi}',
        f'add {rsi}, {alChunkLabel}.size',
        f'mov {rdx}, [{rsi}]',
        f'and {rdx}, {flagsSpaceLabel}',
        f'or {rdx}, {flagPrevinuseLabel}',
        f'mov qword [{rsi}], {rdx}',
        'ret',
        '.free_list_fallback:', # Free list fallback
        f'test qword [rel {freeheadLabel}], -1',
        'jz .fail',
        f'call {ll_lookfor}',
        f'test {rdi}, {rdi}',
        'jz .fail',
        f'cmp {rdi}, [rel {freeheadLabel}]',
        'jne .not_head',
        f'mov {rdx}, [{rdi} + {frChunkLabel}.next]',
        f'mov qword [rel {freeheadLabel}], {rdx}',
        '.not_head:',
        f'call {ll_removefreech}',
        f'lea {rsi}, [{rdi} + {alChunkLabel}_size + {rax} + {alChunkLabel}.size]',
        f'mov {rdx}, [{rsi}]',
        f'or {rdx}, {flagPrevinuseLabel}',
        f'mov qword [{rsi}], {rdx}',
        f'mov {rsi}, [{rdi} + {alChunkLabel}.size]',
        f'and {rsi}, {flagsSpaceInvLabel}',
        f'mov {rdx}, {rax}',
        f'add {rdx}, {alChunkLabel}',
        f'cmp {rsi}, {rdx}',
        'jg .chunk_split',
        f'mov qword [{rdi} + {frChunkLabel}.next], 0',
        f'mov qword [{rdi} + {frChunkLabel}.prev], 0',
        'ret',
        '.chunk_split:',
        f'sub {rsi}, {rax}',
        f'sub {rsi}, {alChunkLabel}_size',
        f'mov {rdx}, [{rdi} + {alChunkLabel}.size]',
        f'and {rdx}, {flagsSpaceLabel}',
        f'or {rdx}, {rax}',
        f'mov qword [{rdi} + {alChunkLabel}.size], {rdx}',
        f'lea {rdx}, [{rdi} + {rax} + {alChunkLabel}_size]',
        f'mov qword [{rdx} + {alChunkLabel}.prev_size], 0',
        f'or {rsi}, {flagPrevinuseLabel}',
        f'mov qword [{rdx} + {alChunkLabel}.size], {rsi}',
        f'pus {rdi}',
        f'mov {rdi}, {rdx}',
        f'call {freeLabel}',
        f'pop {rdi}',
        'ret',
        '.fail:',
        f'mov {rdi}, 0',
        'ret',
        f'{freeLabel}:', # free (pointer in RDI)
        f'mov {rdx}, [{rdi} + {alChunkLabel}.size]',
        f'and {rdx}, {flagsSpaceInvLabel}',
        f'lea {rsi}, [{rdi} + {alChunkLabel}_size + {rdx}]',
        f'mov qword [{rsi} + {alChunkLabel}.prev_size], {rdx}',
        f'mov {rax}, [{rsi} + {alChunkLabel}.size]',
        f'and {rax}, {flagPrevinuseInvLabel}',
        f'mov qword [{rsi} + {alChunkLabel}.size], {rax}',
        f'mov {rax}, [{rdi} + {alChunkLabel}.size]',
        f'test {rax}, {flagPrevinuseLabel}',
        'jnz .previnuse_set', # The prev chunk is free
        f'mov {rax}, [{rdi} + {alChunkLabel}.prev_size]',
        f'sub {rdi}, {rax}',
        f'sub {rdi}, {alChunkLabel}_size',
        f'cmp {rdi}, [rel {freeheadLabel}]',
        'jne .not_head',
        f'mov {rax}, [{rdi} + {frChunkLabel}.next]',
        f'mov qword [rel {freeheadLabel}], {rax}',
        '.not_head:',
        f'mov {rax}, [{rdi} + {frChunkLabel}.size]',
        f'and {rax}, {flagsSpaceInvLabel}',
        f'add {rax}, {rdx}',
        f'add {rax}, {alChunkLabel}_size',
        f'call {ll_removefreech}',
        f'lea {rsi}, [{rdi} + {frChunkLabel}.size]',
        f'mov {rdx}, [{rsi}]',
        f'and {rdx}, {flagsSpaceLabel}',
        f'or {rdx}, {rax}',
        f'mov qword [{rsi}], {rdx}',
        f'call {freeLabel}',
        'ret',
        '.previnuse_set:', # prev chunk not free
        f'mov {rdx}, [{rsi} + {alChunkLabel}.size]',
        f'and {rdx}, {flagsSpaceInvLabel}',
        f'test {rdx}, {rdx}',
        'jz .end',
        f'mov {rax}, [{rsi} + {alChunkLabel}.size]',
        f'lea {rdx}, [{rsi} + {alChunkLabel}_size + {rax}]',
        f'mov {rax}, [{rdx} + {alChunkLabel}.size]',
        f'and {rax}, {flagPrevinuseLabel}',
        f'test {rax}, {rax}',
        'jz .end',
        f'cmp {rsi}, [rel {freeheadLabel}]',
        'jne .not_headn',
        f'mov {rax}, [{rsi} + {frChunkLabel}.next]',
        f'mov qword [rel {freeheadLabel}], {rax}',
        '.not_headn:',
        f'mov {rdi}, {rsi}',
        f'call {ll_removefreech}',
        f'call {freeLabel}',
        'ret',
        '.end:',
        f'call {ll_addfreech}',
        f'mov qword [rel {freeheadLabel}], {rdi}',
        'ret'
      ]
    },
    {
      'op': None,
      'content': [
        f'call {initLabel}'
      ]
    }
  ]


def malloc(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'malloc', 'expected': 1, 'got': len(args)}, str(args))
  if not isArgInt(args[0]): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'malloc', 'expected': ('int',), 'got': (args[0]['argtype'],)}, str(args))

  rax = Global.regs['r1']['b64']
  rdi = Global.regs['r2']['b64']
  rsi = Global.regs['r3']['b64']
  rdx = Global.regs['r4']['b64']

  wrap = saveRegs([rax, rdi, rsi, rdx])

  mallocLabel, isDefined = Global.getGlobalIdFor('malloc')

  if not isDefined: raise TGLNonexistentError('Called malloc without initializing the dat module!', '')

  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'mov {rax}, {((args[0]["value"] + 0xf) // 0x10) * 0x10}', # round to 0x10
        f'call {mallocLabel}',
        f'mov rax, {rdi}',
        *wrap['after']
      ]
    }
  ]


def free(args: list[TypedArgument]) -> InstructionList:
  if len(args) != 1: raise TGLArgumentError.preset({'et': 'argcount', 'func_name': 'free', 'expected': 1, 'got': len(args)}, str(args))
  if not isArgString(args[0]) or not isValueRegister(args[0]['value']): raise TGLArgumentError.preset({'et': 'argtypes', 'func_name': 'free', 'expected': ('register',), 'got': (args[0]['argtype'],)}, str(args))

  rax = Global.regs['r1']['b64']
  rdi = Global.regs['r2']['b64']
  rsi = Global.regs['r3']['b64']
  rdx = Global.regs['r4']['b64']

  wrap = saveRegs([rax, rdi, rsi, rdx])

  mallocLabel, isDefined = Global.getGlobalIdFor('malloc')

  if not isDefined: raise TGLNonexistentError('Called malloc without initializing the dat module!', '')

  return [
    {
      'op': None,
      'content': [
        *wrap['before'],
        f'mov {rax}, {args[0]["value"]}',
        f'call {mallocLabel}',
        f'mov rax, {rdi}',
        *wrap['after']
      ]
    }
  ]


# Export
FUNCTIONS: ModuleExport = {
  'init': init,
  'malloc': malloc,
  'free': free
}
