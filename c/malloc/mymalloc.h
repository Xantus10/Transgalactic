#ifndef H_MALLOC
#define H_MALLOC

#include "chunks.h"
#include "pagemgr.h"

/**
 * Allocate a new chunk
 */
void* mymalloc(size_t size);

/**
 * Free a chunk
 */
void myfree(void* chunk);

#endif