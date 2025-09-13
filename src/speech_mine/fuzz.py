from rapidfuzz import fuzz
from typing import List, Tuple
from speech_mine.models import WordData


def speech_fuzzy_match(
    word_list: List[WordData],
    query: str,
    similarity_range: Tuple[float, float] = (0, 1),
    top_k: int = 10
) -> List[Tuple[int, int, float]]:
    """
    Find the most similar word windows to a query using rapidfuzz similarity matching.
    
    This function splits the query into words and searches for similar word sequences
    in the word_list using sliding windows of varying sizes. It filters results by
    similarity score, removes overlapping matches (keeping higher scoring ones), and
    returns the top-k results.
    
    Args:
        word_list: List of WordData objects containing word information
        query: Search query as a string (sentence, word, or phrase)
        similarity_range: Tuple of (min_similarity, max_similarity) to filter results.
                         Only windows with similarity scores in this range are returned.
        top_k: Maximum number of results to return. If more matches exist within
               similarity_range, only the top-k highest scoring ones are returned.
    
    Returns:
        List of tuples containing (start_index, end_index, similarity_score) where
        indices refer to positions in the word_list. For single words, start_index
        equals end_index.
    
    Example:
        >>> word_data = [WordData(...), WordData(...), ...]
        >>> results = speech_fuzzy_match(word_data, "hello world", (0.8, 1.0), 5)
        >>> # Returns: [(0, 1, 0.95), (5, 6, 0.87), ...]
    """
    if not word_list or not query.strip():
        return []
    
    # Split query into words and get query size
    query_words = query.strip().split()
    query_size = len(query_words)
    
    if query_size == 0:
        return []
    
    # Generate all possible windows with sizes in range [query_size-1, query_size+1]
    candidates = []
    min_window_size = max(1, query_size - 1)
    max_window_size = query_size + 1
    
    for window_size in range(min_window_size, min(max_window_size + 1, len(word_list) + 1)):
        for start_idx in range(len(word_list) - window_size + 1):
            end_idx = start_idx + window_size - 1
            
            # Extract words from window
            window_words = [word_list[i].word for i in range(start_idx, end_idx + 1)]
            window_text = ' '.join(window_words)
            
            # Calculate similarity using rapidfuzz
            similarity = fuzz.ratio(query, window_text) / 100.0  # Convert to 0-1 range
            
            # Filter by similarity range
            if similarity_range[0] <= similarity <= similarity_range[1]:
                candidates.append((start_idx, end_idx, similarity, window_size))
    
    if not candidates:
        return []
    
    # Remove overlapping matches, keeping the one with highest similarity
    # If same similarity, prefer fewer words (smaller window)
    filtered_candidates = []
    candidates.sort(key=lambda x: (-x[2], x[3]))  # Sort by similarity desc, then window size asc
    
    for start_idx, end_idx, similarity, window_size in candidates:
        # Check if this candidate overlaps with any already selected candidate
        overlaps = False
        for existing_start, existing_end, _, _ in filtered_candidates:
            # Check for overlap: ranges overlap if start1 <= end2 and start2 <= end1
            if start_idx <= existing_end and existing_start <= end_idx:
                overlaps = True
                break
        
        if not overlaps:
            filtered_candidates.append((start_idx, end_idx, similarity, window_size))
    
    # Sort by similarity descending and take top_k
    filtered_candidates.sort(key=lambda x: -x[2])
    top_candidates = filtered_candidates[:top_k]
    
    # Return in the required format (start_index, end_index, similarity_score)
    return [(start_idx, end_idx, similarity) for start_idx, end_idx, similarity, _ in top_candidates]

