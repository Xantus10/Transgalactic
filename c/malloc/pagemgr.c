#include "pagemgr.h"

void init_pagemgr() {
  init_page_size();
  PAGEMGR_HEAD = map_page();
  PAGEMGR_CURRENT = PAGEMGR_HEAD;
  PAGEMGR_FREE_HEAD = NULL;
}

alloc_chunk* new_chunk(size_t size) {
  if (size % 0x10 != 0) return NULL;
  if (PAGEMGR_HEAD == NULL) return NULL;
  if (PAGEMGR_CURRENT + sizeof(alloc_chunk) + size < PAGEMGR_HEAD + PAGE_SIZE) {
    alloc_chunk* ret = (alloc_chunk*) PAGEMGR_CURRENT;
    PAGEMGR_CURRENT += sizeof(alloc_chunk) + size;
    ret->size = size;
    ret->prev_size = 0;
    ((alloc_chunk*) PAGEMGR_CURRENT)->size |= CHUNK_FLAG_PREVINUSE;
    return ret;
  } else if (PAGEMGR_FREE_HEAD != NULL) {
    free_chunk* ret = ll_look_for_size(PAGEMGR_FREE_HEAD, size);
    if (ret != NULL) {
      if (ret == PAGEMGR_FREE_HEAD) {
        PAGEMGR_FREE_HEAD = ret->next;
      }
      ll_remove_free_chunk(ret);
      ((alloc_chunk*) ret + sizeof(alloc_chunk) + size)->size |= CHUNK_FLAG_PREVINUSE;
      if (ret->size == size) {
        ret->next = NULL;
        ret->prev = NULL;
        return (alloc_chunk*) ret;
      } // HANDLE SPLITTING WHEN NOT SAME SIZE
    }
  }
  return NULL;
}
