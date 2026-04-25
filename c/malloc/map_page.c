#include "map_page.h"

PAGE_SIZE = 0;

// If we are on windows
#ifdef _WIN32
  /**
   * Initialize PAGE_SIZE
   */
  size_t init_page_size() {
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    PAGE_SIZE = si.dwPageSize;
  }

  /**
   * Get a pointer to a page
   * 
   * @return Pointer to the page (NULL at fail)
   */
  void* map_page() {
    if (PAGE_SIZE == 0) return NULL;

    void* ptr = VirtualAlloc(
      NULL,
      PAGE_SIZE,
      MEM_COMMIT | MEM_RESERVE,
      PAGE_READWRITE
    );

    return ptr;
  }
#else // If we are on Linux
  /**
   * Initialize PAGE_SIZE
   */
  size_t init_page_size() {
    PAGE_SIZE = sysconf(_SC_PAGESIZE);
  }

  /**
   * Get a pointer to a page
   * 
   * @return Pointer to the page (NULL at fail)
   */
  void* map_page(void) {
    if (PAGE_SIZE == 0) return NULL;

    void* ptr = mmap(
      NULL,
      PAGE_SIZE,
      PROT_READ | PROT_WRITE,
      MAP_PRIVATE | MAP_ANONYMOUS,
      -1,
      0
    );

    if (ptr == MAP_FAILED)
      return NULL;

    return ptr;
  }
#endif