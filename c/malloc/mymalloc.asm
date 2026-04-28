section .data
  PAGE_SIZE equ 4096
  CHUNK_DATA equ 16
  HEAD: dq 0
  CUR: dq 0
  FREE_HEAD: dq 0


section .text
  init:
  ! mc mmap 1
  mov [rel HEAD], rax
  mov [rel CUR], rax
  ret

  ;;; size in RAX
  malloc:
  mov r8, [rel CUR]
  lea r8, [r8 + CHUNK_DATA*2]
  add r8, rax
  mov r9, [rel HEAD]
  add r9, PAGE_SIZE
  cmp r8, r9
  jge free_list_fallback
  
