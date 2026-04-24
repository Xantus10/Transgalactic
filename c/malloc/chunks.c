#include "chunks.h"

void ll_add_free_chunk(free_chunk* list_head, free_chunk* chunk) {
  list_head->prev = chunk;
  list_head->prev_size = chunk->size;
  chunk->next = list_head;
  chunk->prev = NULL;
  chunk->prev_size = 0;
}

void ll_remove_free_chunk(free_chunk* chunk) {
  if (chunk->prev == NULL) {
    chunk->next->prev = NULL;
    chunk->next->prev_size = 0;
  } else if (chunk->next = NULL) {
    chunk->prev->next = NULL;
  } else {
    chunk->prev->next = chunk->next;
    chunk->next->prev = chunk->prev;
    chunk->next->prev_size = chunk->prev_size;
  }
}

free_chunk* ll_look_for_size(free_chunk* list_head, size_t size) {
  free_chunk* found = list_head;
  while (found != NULL && found->size >= size) {
    found = found->next;
  }
  return found;
}
