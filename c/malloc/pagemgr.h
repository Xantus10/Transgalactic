#ifndef H_PAGEMGR
#define H_PAGEMGR

#include "chunks.h"
#include "map_page.h"

/**
 * Pointer to the head of the current page
 */
void* PAGEMGR_HEAD = NULL;

/**
 * Current position on the page
 */
void* PAGEMGR_CURRENT = NULL;

/**
 * Head of the free chunk linked list
 */
free_chunk* PAGEMGR_FREE_HEAD = NULL;

void init_pagemgr();

alloc_chunk* new_chunk(size_t size);

#endif