#ifndef H_META
#define H_META

#define CHUNK_FLAGS_SPACE 0b1111
#define CHUNK_FLAG_PREVINUSE 0b1

#include <stdint.h>

/**
 * Allocated chunk
 */
typedef struct alloc_chunk {
  /**
   * Previous chunk size
   */
  size_t prev_size;

  /**
   * This chunk size
   */
  size_t size;

} alloc_chunk;

/**
 * Free chunk
 */
typedef struct free_chunk {
  /**
   * Previous chunk size
   */
  size_t* prev_size;

  /**
   * This chunk size
   */
  size_t size;

  /**
   * Previous free pointer
   */
  free_chunk* prev;

  /**
   * Next free pointer
   */
  free_chunk* next;

} free_chunk;


/**
 * Return the address to the next chunk
 * 
 * @return Pointer to the next chunk
 */
alloc_chunk* next_chunk(alloc_chunk* addr);

/**
 * Return the address to the previous chunk (ONLY IF PREVINUSE==0)
 * 
 * @return Pointer to the next chunk
 */
free_chunk* prev_chunk(alloc_chunk* addr);

/**
 * Add flag bits for the next chunk
 * 
 * @return Pointer to the next chunk
 */
alloc_chunk* next_chunk_flags_add(alloc_chunk* addr, uint8_t mask);

/**
 * Remove flag bits for the next chunk
 * 
 * @return Pointer to the next chunk
 */
alloc_chunk* next_chunk_flags_remove(alloc_chunk* addr, uint8_t mask);


/**
 * Add a free chunk into the linked list (list_head != NULL)
 */
void ll_add_free_chunk(free_chunk* list_head, free_chunk* chunk);

/**
 * Remove a free chunk from the linked list
 */
void ll_remove_free_chunk(free_chunk* chunk);

/**
 * Look for a chunk of suitable size in the free list
 */
free_chunk* ll_look_for_size(free_chunk* list_head, size_t size);

#endif