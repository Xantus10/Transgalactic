#include "chunks.h"


alloc_chunk* next_chunk(alloc_chunk* addr) {
  return addr + sizeof(alloc_chunk) + addr->size;
}

free_chunk* prev_chunk(alloc_chunk* addr) {
  return (free_chunk*) addr - sizeof(alloc_chunk) - addr->prev_size;
}

alloc_chunk* next_chunk_flags_add(alloc_chunk* addr, uint8_t mask) {
  alloc_chunk* next = next_chunk(addr);
  next->size |= mask;
  return next;
}

alloc_chunk* next_chunk_flags_remove(alloc_chunk* addr, uint8_t mask) {
  alloc_chunk* next = next_chunk(addr);
  next->size &= ~mask;
  return next;
}


void ll_add_free_chunk(free_chunk* list_head, free_chunk* chunk) {
  // Set the former 1st item values
  list_head->prev = chunk;
  // Link the new chunk to the previous head
  chunk->next = list_head;
  chunk->prev = NULL;
}

void ll_remove_free_chunk(free_chunk* chunk) {
  // If is 1st
  if (chunk->prev == NULL) {
    // It was just the one item
    if (chunk->next == NULL) return;
    // Pop the first item
    chunk->next->prev = NULL;
  // If is last
  } else if (chunk->next = NULL) {
    // Unlink from last item
    chunk->prev->next = NULL;
  } else {
    // Make a jump around self
    chunk->prev->next = chunk->next;
    chunk->next->prev = chunk->prev;
  }
}

free_chunk* ll_look_for_size(free_chunk* list_head, size_t size) {
  free_chunk* found = list_head;
  // While we are not at the end && The chunk size is too small
  while (found != NULL && found->size < size) {
    found = found->next;
  }
  return found;
}
