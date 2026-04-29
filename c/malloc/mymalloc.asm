struc AllocChunk
  .prev_size resq 1
  .size resq 1
endstruc

struc FreeChunk
  .prev_size resq 1
  .size resq 1
  .prev resq 1
  .next resq 1
endstruc

PAGE_SIZE equ 4096
FLAGS_SPACE equ 15
FLAG_PREVINUSE equ 1


section .data
  HEAD: dq 0
  CUR: dq 0
  FREE_HEAD: dq 0


section .text
  init:
  ! mc mmap 1
  mov qword [rel HEAD], rax
  mov qword [rel CUR], rax
  ret

  ; size in RAX, ret in RDI
  ll_lookfor:
  ; Load the address at FREE_HEAD
  mov rdi, [rel FREE_HEAD]
  .start
    test rdi, rdi
    jz .end
    cmp [rdi + FreeChunk.size], rax
    jge .end
    mov rdi, [rdi + FreeChunk.next]
    jmp .start
  .end
  ret

  ; pointer to chunk in rdi
  ll_remove_free_chunk:
  mov rdx, [rdi + FreeChunk.prev]
  mov rsi, [rdi + FreeChunk.next]
  test rdx, rdx
  jnz .not_first
    test rsi, rsi
    jz .single
      ; Unlink from next item
      mov qword [rsi + FreeChunk.prev], 0
    .single
    ret
  .not_first
    test rsi, rsi
    jnz .not_last
    ; Unlink from last item
    mov qword [rdx + FreeChunk.next], 0
    ret
  .not_last
    ; chunk->prev->next
    mov qword [rdx + FreeChunk.next], rsi
    ; chunk->next->prev
    mov qword [rsi + FreeChunk.prev], rdx
    ret

  ; size in RAX, ret in RDI
  malloc:
  mov rdi, [rel CUR]
  lea rdi, [rdi + AllocChunk_size*2]
  add rdi, rax
  mov rsi, [rel HEAD]
  add rsi, PAGE_SIZE
  ; Compare if there is enough space in the mempage
  cmp rdi, rsi
  jge .free_list_fallback
    ; The ret pointer
    mov rdi, [rel CUR]
    ; prev_size = 0
    mov qword [rdi], 0
    ; size
    lea rsi, [rdi + AllocChunk.size]
    mov rdx, [rsi]
    ; &= FLAGS_SPACE
    and rdx, FLAGS_SPACE
    ; |= size
    or rdx, rax
    ; Test for 1st chunk CUR == HEAD
    test rdi, [rel HEAD]
    jnz .not_first
      or rdx, FLAG_PREVINUSE
    .not_first
    ; Store the data back
    mov [rsi], rdx
    ; Next chunk->size
    lea rsi, [rdi + AllocChunk_size + rax + AllocChunk.size]
    mov rdx, [rsi]
    ; &= FLAGS_SPACE
    and rdx, FLAGS_SPACE
    ; Add the PREVINUSE flag
    or rdx, FLAG_PREVINUSE
    mov [rsi], rdx
    ret
  .free_list_fallback
    ; Is FREE_HEAD NULL pointer?
    test qword [rel FREE_HEAD], -1
    jz .fail
    ; Look for sufficiently large chunk
    call ll_lookfor
    ; Is the result NULL
    test rdi, rdi
    jz .fail
    ; Is the chunk the FREE_HEAD
    test rdi, [rel FREE_HEAD]
    jz .not_head
      ; Move the free head to be the ->next
      mov rdx, [rdi + FreeChunk.next]
      mov qword [rel FREE_HEAD], rdx
    .not_head
    call ll_remove_free_chunk
    lea rsi, [rdi + AllocChunk_size + rax + AllocChunk.size]
    mov rdx, [rsi]
    ; Add the PREVINUSE flag
    or rdx, FLAG_PREVINUSE
    mov [rsi], rdx
    ; Check for chunk splitting

  .fail
  mov rdi, 0
  ret
  
