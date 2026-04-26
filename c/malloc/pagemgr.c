#include "pagemgr.h"

char* PAGEMGR_HEAD = NULL;

char* PAGEMGR_CURRENT = NULL;

free_chunk* PAGEMGR_FREE_HEAD = NULL;

void init_pagemgr() {
  // Initialize map_page
  init_page_size();
  PAGEMGR_HEAD = (char*) map_page();
  // Current pointer at the beginning
  PAGEMGR_CURRENT = PAGEMGR_HEAD;
  // Free list empty
  PAGEMGR_FREE_HEAD = NULL;
}

alloc_chunk* new_chunk(size_t size) {
  // If invalid size
  if (size % 0x10 != 0) return NULL;
  // If not initialized
  if (PAGEMGR_HEAD == NULL) return NULL;
  // If we have enough space in the page
  if (PAGEMGR_CURRENT + sizeof(alloc_chunk)*2 + size < PAGEMGR_HEAD + PAGE_SIZE) {
    // New pointer
    alloc_chunk* ret = (alloc_chunk*) PAGEMGR_CURRENT;
    // Set values
    ret->size &= CHUNK_FLAGS_SPACE;
    ret->size |= size;
    ret->prev_size = 0;
    // Check if it's the first chunk
    if (PAGEMGR_HEAD == PAGEMGR_CURRENT) ret->size |= CHUNK_FLAG_PREVINUSE;
    // Move the CURRENT pointer
    PAGEMGR_CURRENT += sizeof(alloc_chunk) + size;
    alloc_chunk* next = next_chunk_flags_add(ret, CHUNK_FLAG_PREVINUSE);
    next->size &= CHUNK_FLAGS_SPACE;
    return ret;
  // If there are chunks in the free list
  } else if (PAGEMGR_FREE_HEAD != NULL) {
    // Look for a chunk big enough
    free_chunk* ret = ll_look_for_size(PAGEMGR_FREE_HEAD, size);
    if (ret != NULL) {
      // If the returned chunk is the HEAD
      if (ret == PAGEMGR_FREE_HEAD) {
        // Move the head
        PAGEMGR_FREE_HEAD = ret->next;
      }
      // Remove the chunk
      ll_remove_free_chunk(ret);
      // Set the PREVINUSE flag for the NEXT chunk
      next_chunk_flags_add((alloc_chunk*) ret, CHUNK_FLAG_PREVINUSE);
      // If there is not enough space in the chunk to split it
      if ((ret->size & ~CHUNK_FLAGS_SPACE) <= size + sizeof(alloc_chunk)) {
        ret->next = NULL;
        ret->prev = NULL;
        return (alloc_chunk*) ret;
      }
      // Size of the new chunk (total_size - size - new_chunk_metadata)
      size_t new_size = (ret->size & ~CHUNK_FLAGS_SPACE) - size - sizeof(alloc_chunk);
      // Set updated size
      ret->size &= CHUNK_FLAGS_SPACE;
      ret->size |= size;
      // New chunk
      alloc_chunk* new = next_chunk((alloc_chunk*) ret);
      new->prev_size = 0;
      new->size = new_size | CHUNK_FLAG_PREVINUSE;
      // Mark the chunk as free
      chunk_free(new);
      return (alloc_chunk*) ret;
    }
  }
  return NULL;
}


void chunk_free(alloc_chunk* chunk) {
  // We free this chunk, so unset the next->previnuse
  alloc_chunk* next = next_chunk_flags_remove(chunk, CHUNK_FLAG_PREVINUSE);
  // And provide the prev_size, since previnuse is unset now
  next->prev_size = chunk->size & ~CHUNK_FLAGS_SPACE;
  // If the previous chunk is empty
  if (!(chunk->size & CHUNK_FLAG_PREVINUSE)) {
    free_chunk* prev = prev_chunk(chunk);
    if (prev == PAGEMGR_FREE_HEAD) {
      // Move the head
      PAGEMGR_FREE_HEAD = prev->next;
    }
    ll_remove_free_chunk(prev);
    // Expand the prev chunk by our chunk
    size_t new_size = (prev->size & ~CHUNK_FLAGS_SPACE) + (chunk->size & ~CHUNK_FLAGS_SPACE) + sizeof(alloc_chunk);
    prev->size &= CHUNK_FLAGS_SPACE;
    prev->size |= new_size;
    // Free the expanded chunk
    return chunk_free((alloc_chunk*) prev);
  }
  // If we are at the end of allocated chunks (size==0)
  if ((next->size & ~CHUNK_FLAGS_SPACE) == 0) {
    ll_add_free_chunk(PAGEMGR_FREE_HEAD, (free_chunk*) chunk);
    PAGEMGR_FREE_HEAD = (free_chunk*) chunk;
    return;
  }
  alloc_chunk* nnext = next_chunk(next);
  // Check the next-next chunk for info about the next chunk
  if (!(nnext->size & CHUNK_FLAG_PREVINUSE)) {
    if ((free_chunk*) next == PAGEMGR_FREE_HEAD) {
      // Move the head
      PAGEMGR_FREE_HEAD = ((free_chunk*) next)->next;
    }
    ll_remove_free_chunk(((free_chunk*) next));
    // Call free on the next chunk (it will trigger the 1st branch)
    chunk_free(next);
  // If we cannot expand forwards or backwards
  } else {
    ll_add_free_chunk(PAGEMGR_FREE_HEAD, (free_chunk*) chunk);
    PAGEMGR_FREE_HEAD = (free_chunk*) chunk;
  }
}
