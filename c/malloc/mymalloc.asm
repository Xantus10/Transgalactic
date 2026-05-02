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
FLAGS_SPACE_INVERSE equ -16
FLAG_PREVINUSE equ 1
FLAG_PREVINUSE_INVERSE equ -2


section .data
  HEAD: dq 0
  CUR: dq 0
  FREE_HEAD: dq 0


section .text
  init:
  mov rax, 9
  xor rdi, rdi
  mov rsi, PAGE_SIZE
  mov rdx, 3
  mov r10, 34
  mov r8, -1
  xor r9, r9
  syscall
  mov qword [rel HEAD], rax
  mov qword [rel CUR], rax
  ret

  ; size in RAX, ret in RDI
  ll_lookfor:
  ; Load the address at FREE_HEAD
  mov rdi, [rel FREE_HEAD]
  .start:
    test rdi, rdi
    jz .end
    cmp [rdi + FreeChunk.size], rax
    jge .end
    mov rdi, [rdi + FreeChunk.next]
    jmp .start
  .end:
  ret

  ; pointer to chunk in RDI
  ll_add_free_chunk:
  mov rax, [rel FREE_HEAD]
  ; Is free head NULL
  test rax, -1
  jz .no_head
    mov qword [rax + FreeChunk.prev], rdi
  .no_head:
  mov qword [rdi + FreeChunk.prev], 0
  mov qword [rdi + FreeChunk.next], rax
  ret

  ; pointer to chunk in RDI
  ll_remove_free_chunk:
  mov rdx, [rdi + FreeChunk.prev]
  mov rsi, [rdi + FreeChunk.next]
  test rdx, rdx
  jnz .not_first
    test rsi, rsi
    jz .single
      ; Unlink from next item
      mov qword [rsi + FreeChunk.prev], 0
    .single:
    ret
  .not_first:
    test rsi, rsi
    jnz .not_last
    ; Unlink from last item
    mov qword [rdx + FreeChunk.next], 0
    ret
  .not_last:
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
    cmp rdi, [rel HEAD]
    jne .not_first
      or rdx, FLAG_PREVINUSE
    .not_first:
    ; Store the data back
    mov qword [rsi], rdx
    ; Move the CUR pointer
    lea rsi, [rdi + AllocChunk_size + rax]
    mov qword [rel CUR], rsi
    ; Next chunk->size
    add rsi, AllocChunk.size
    mov rdx, [rsi]
    ; &= FLAGS_SPACE
    and rdx, FLAGS_SPACE
    ; Add the PREVINUSE flag
    or rdx, FLAG_PREVINUSE
    mov qword [rsi], rdx
    ret
  .free_list_fallback:
    ; Is FREE_HEAD NULL pointer?
    test qword [rel FREE_HEAD], -1
    jz .fail
    ; Look for sufficiently large chunk
    call ll_lookfor
    ; Is the result NULL
    test rdi, rdi
    jz .fail
    ; Is the chunk the FREE_HEAD
    cmp rdi, [rel FREE_HEAD]
    jne .not_head
      ; Move the free head to be the ->next
      mov rdx, [rdi + FreeChunk.next]
      mov qword [rel FREE_HEAD], rdx
    .not_head:
    call ll_remove_free_chunk
    lea rsi, [rdi + AllocChunk_size + rax + AllocChunk.size]
    mov rdx, [rsi]
    ; Add the PREVINUSE flag
    or rdx, FLAG_PREVINUSE
    mov qword [rsi], rdx
    ; Check for chunk splitting
    mov rsi, [rdi + AllocChunk.size]
    and rsi, FLAGS_SPACE_INVERSE
    mov rdx, rax
    add rdx, AllocChunk_size
    cmp rsi, rdx
    jg .chunk_split
      mov qword [rdi + FreeChunk.next], 0
      mov qword [rdi + FreeChunk.prev], 0
      ret
    .chunk_split:
    ; rsi holds new_size
    sub rsi, rax
    sub rsi, AllocChunk_size
    mov rdx, [rdi + AllocChunk.size]
    ; Set the ret->size
    and rdx, FLAGS_SPACE
    or rdx, rax
    mov qword [rdi + AllocChunk.size], rdx
    ; rdx = new
    lea rdx, [rdi + rax + AllocChunk_size]
    mov qword [rdx + AllocChunk.prev_size], 0
    ; Add the previnuse flag
    or rsi, FLAG_PREVINUSE
    mov qword [rdx + AllocChunk.size], rsi
    mov rax, rdi
    mov rdi, rdx
    call free
    mov rdi, rax
    ret
  .fail:
  mov rdi, 0
  ret


  ; Pointer to free in RDI
  free:
  ; This-> size
  mov rdx, [rdi + AllocChunk.size]
  ; Remove flags (pure size)
  and rdx, FLAGS_SPACE_INVERSE
  ; Next chunk
  lea rsi, [rdi + AllocChunk_size + rdx]
  ; Set the prev_size
  mov qword [rsi + AllocChunk.prev_size], rdx
  ; Remove next->PREVINUSE
  mov rax, [rsi + AllocChunk.size]
  and rax, FLAG_PREVINUSE_INVERSE
  mov qword [rsi + AllocChunk.size], rax
  mov rax, [rdi + AllocChunk.size]
  test rax, FLAG_PREVINUSE
  ; If the previous chunk is empty - coalesce
  jnz .previnuse_set
    ; rdx holds size & FLAGS_SPACE_INV, and that's all we need
    mov rax, [rdi + AllocChunk.prev_size]
    ; prev chunk
    sub rdi, rax
    sub rdi, AllocChunk_size
    cmp rdi, [rel FREE_HEAD]
    jne .not_head
      ; Move the free head to be the ->next
      mov rax, [rdi + FreeChunk.next]
      mov qword [rel FREE_HEAD], rax
    .not_head:
    ; New size
    mov rax, [rdi + FreeChunk.size]
    and rax, FLAGS_SPACE_INVERSE
    add rax, rdx
    add rax, AllocChunk_size
    ; Remove the chunk
    call ll_remove_free_chunk
    lea rsi, [rdi + FreeChunk.size]
    mov rdx, [rsi]
    ; Logically set size = 0
    and rdx, FLAGS_SPACE
    or rdx, rax
    mov qword [rsi], rdx
    ; Call free with rdi=prev chunk
    call free
    ret
  .previnuse_set:
  mov rdx, [rsi + AllocChunk.size]
  and rdx, FLAGS_SPACE_INVERSE
  ; Last chunk - size==0
  test rdx, rdx
  jz .end
  mov rax, [rsi + AllocChunk.size]
  ; NextNext chunk
  lea rdx, [rsi + AllocChunk_size + rax]
  mov rax, [rdx + AllocChunk.size]
  and rax, FLAG_PREVINUSE
  ; Is the nnext->flag_previnuse set
  test rax, rax
  jnz .end
    cmp rsi, [rel FREE_HEAD]
    jne .not_headn
      ; Move the free head to be the ->next
      mov rax, [rsi + FreeChunk.next]
      mov qword [rel FREE_HEAD], rax
    .not_headn:
    mov rdi, rsi
    call ll_remove_free_chunk
    call free
    ret
  .end:
  call ll_add_free_chunk
  mov qword [rel FREE_HEAD], rdi
  ret

global _start
_start:
  call init

  mov rax, 0x20
  call malloc
  mov r8, rdi

  mov rax, 0x10
  call malloc
  mov r9, rdi

  mov rax, 0x20
  call malloc
  mov r10, rdi

  mov rdi, r9
  call free

  mov rdi, r10
  call free

  mov rdi, r8
  call free

  mov rax, 60
  xor rdi, rdi
  syscall
