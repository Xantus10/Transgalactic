#include "mymalloc.h"


void* mymalloc(size_t size) {
  if (PAGEMGR_HEAD == NULL) init_pagemgr();
  return (void*) (((char*) new_chunk((size + 0xf) & (~0xf))) + sizeof(alloc_chunk));
}


void myfree(void* chunk) {
  chunk_free((alloc_chunk*) (((char*) chunk) - sizeof(alloc_chunk)));
}
