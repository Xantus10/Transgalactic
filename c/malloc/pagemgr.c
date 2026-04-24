#include "pagemgr.h"

void init_pagemgr() {
  // Initialize map_page
  init_page_size();
  PAGEMGR_HEAD = map_page();
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
    // Move the CURRENT pointer
    PAGEMGR_CURRENT += sizeof(alloc_chunk) + size;
    // Set values
    ret->size = size;
    ret->prev_size = 0;
    // Set the PREVINUSE flag for the NEXT chunk
    ((alloc_chunk*) PAGEMGR_CURRENT)->size |= CHUNK_FLAG_PREVINUSE;
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
      ((alloc_chunk*) ret + sizeof(alloc_chunk) + size)->size |= CHUNK_FLAG_PREVINUSE;
      // If we get lucky and the sizes match - just return
      if (ret->size == size) {
        ret->next = NULL;
        ret->prev = NULL;
        return (alloc_chunk*) ret;
      } // HANDLE SPLITTING WHEN NOT SAME SIZE
    }
  }
  return NULL;
}
