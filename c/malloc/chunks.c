#include "chunks.h"

void ll_add_free_chunk(free_chunk* list_head, free_chunk* chunk) {
  // Set the former 1st item values
  list_head->prev = chunk;
  list_head->prev_size = chunk->size;
  // Link the new chunk to the previous head
  chunk->next = list_head;
  chunk->prev = NULL;
  chunk->prev_size = 0;
}

void ll_remove_free_chunk(free_chunk* chunk) {
  // If is 1st
  if (chunk->prev == NULL) {
    // Pop the first item
    chunk->next->prev = NULL;
    chunk->next->prev_size = 0;
  // If is last
  } else if (chunk->next = NULL) {
    // Unlink from last item
    chunk->prev->next = NULL;
  } else {
    // Make a jump around self
    chunk->prev->next = chunk->next;
    chunk->next->prev = chunk->prev;
    // Set the prev size
    chunk->next->prev_size = chunk->prev_size;
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
