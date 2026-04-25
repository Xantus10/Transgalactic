#ifndef H_PAGEMGR
#define H_PAGEMGR

#include "chunks.h"
#include "map_page.h"

/**
 * Pointer to the head of the current page
 */
char* PAGEMGR_HEAD;

/**
 * Current position on the page
 */
char* PAGEMGR_CURRENT;

/**
 * Head of the free chunk linked list
 */
free_chunk* PAGEMGR_FREE_HEAD;

/**
 * Initialize global variables
 */
void init_pagemgr();

/**
 * Allocate a new chunk
 */
alloc_chunk* new_chunk(size_t size);

/**
 * Free a chunk
 */
void chunk_free(alloc_chunk* chunk);

#endif