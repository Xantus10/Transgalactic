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
size_t PAGE_SIZE = 0;

size_t init_page_size();

void* map_page();

#endif