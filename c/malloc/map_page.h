#ifndef H_PAGE_MAP
#define H_PAGE_MAP

#include <stddef.h>

#ifdef _WIN32
  #include <windows.h>
#else
  #include <sys/mman.h>
  #include <unistd.h>
#endif

/**
 * The page size detected
 */
extern size_t PAGE_SIZE;

/**
 * Initialise the page size
 */
size_t init_page_size();

/**
 * Map a memory page for this process (of size PAGE_SIZE)
 */
void* map_page();

#endif