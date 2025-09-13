from typing import List
from speech_mine.fuzz import WordData, speech_fuzzy_match


class TestFuzzySpeechMatch:
    """Test cases for speech_fuzzy_match function"""
    
    def create_word_data(self, words: List[str], speaker: str = "speaker1") -> List[WordData]:
        """Helper function to create WordData objects from a list of words"""
        word_data_list = []
        for i, word in enumerate(words):
            word_data_list.append(WordData(
                type="word",
                speaker=speaker,
                start=float(i),
                end=float(i + 1),
                text=word,
                word=word,
                word_position=i,
                confidence=0.9,
                overlap_duration=0.0,
                utterance_number=1
            ))
        return word_data_list

    def test_exact_match_single_word(self):
        """Test exact match for a single word"""
        words = ["hello", "world", "test"]
        word_list = self.create_word_data(words)
        
        results = speech_fuzzy_match(word_list, "hello")
        
        assert len(results) > 0
        assert results[0][2] == 1.0  # Perfect similarity
        assert results[0][0] == 0    # Start index
        assert results[0][1] == 0    # End index (same for single word)

    def test_exact_match_multiple_words(self):
        """Test exact match for multiple words"""
        words = ["hello", "world", "how", "are", "you"]
        word_list = self.create_word_data(words)
        
        results = speech_fuzzy_match(word_list, "hello world")
        
        assert len(results) > 0
        assert results[0][2] == 1.0  # Perfect similarity
        assert results[0][0] == 0    # Start index
        assert results[0][1] == 1    # End index

    def test_partial_match(self):
        """Test partial fuzzy matching"""
        words = ["hello", "world", "testing", "fuzzy", "matching"]
        word_list = self.create_word_data(words)
        
        results = speech_fuzzy_match(word_list, "helo world")  # Typo in "hello"
        
        assert len(results) > 0
        assert results[0][2] > 0.7  # Should have good similarity despite typo
        assert results[0][0] == 0
        assert results[0][1] == 1

    def test_window_size_variation(self):
        """Test that function checks different window sizes (±1 from query length)"""
        words = ["the", "quick", "brown", "fox", "jumps"]
        word_list = self.create_word_data(words)
        
        # Query with 2 words should check windows of size 1, 2, and 3
        results = speech_fuzzy_match(word_list, "quick brown", similarity_range=(0.5, 1.0))
        
        assert len(results) > 0
        # Should find exact match for "quick brown"
        exact_match = next((r for r in results if r[2] == 1.0), None)
        assert exact_match is not None
        assert exact_match[0] == 1  # "quick" starts at index 1
        assert exact_match[1] == 2  # "brown" ends at index 2

    def test_similarity_range_filtering(self):
        """Test that similarity_range parameter filters results correctly"""
        words = ["hello", "world", "completely", "different", "text"]
        word_list = self.create_word_data(words)
        
        # High similarity threshold should return fewer results
        high_threshold_results = speech_fuzzy_match(
            word_list, "hello world", similarity_range=(0.9, 1.0)
        )
        
        # Low similarity threshold should return more results
        low_threshold_results = speech_fuzzy_match(
            word_list, "hello world", similarity_range=(0.3, 1.0)
        )
        
        assert len(high_threshold_results) <= len(low_threshold_results)
        
        # All results should be within the specified range
        for _, _, similarity in high_threshold_results:
            assert 0.9 <= similarity <= 1.0

    def test_top_k_limiting(self):
        """Test that top_k parameter limits the number of results"""
        words = ["test"] * 10  # Create many identical words
        word_list = self.create_word_data(words)
        
        results_k3 = speech_fuzzy_match(word_list, "test", top_k=3)
        results_k5 = speech_fuzzy_match(word_list, "test", top_k=5)
        
        assert len(results_k3) <= 3
        assert len(results_k5) <= 5
        assert len(results_k3) <= len(results_k5)

    def test_overlap_removal(self):
        """Test that overlapping matches are handled correctly"""
        words = ["hello", "world", "hello", "universe"]
        word_list = self.create_word_data(words)
        
        results = speech_fuzzy_match(word_list, "hello", similarity_range=(0.8, 1.0))
        
        # Should not return overlapping windows
        for i, (start1, end1, _) in enumerate(results):
            for j, (start2, end2, _) in enumerate(results[i+1:], i+1):
                # Check no overlap: start1 <= end2 and start2 <= end1 means overlap
                overlap = start1 <= end2 and start2 <= end1
                assert not overlap, f"Found overlapping results: ({start1},{end1}) and ({start2},{end2})"

    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        words = ["hello", "world"]
        word_list = self.create_word_data(words)
        
        # Empty query
        results = speech_fuzzy_match(word_list, "")
        assert len(results) == 0
        
        # Empty word list
        results = speech_fuzzy_match([], "hello")
        assert len(results) == 0
        
        # Whitespace only query
        results = speech_fuzzy_match(word_list, "   ")
        assert len(results) == 0

    def test_no_matches_in_similarity_range(self):
        """Test when no matches fall within similarity range"""
        words = ["completely", "different", "words"]
        word_list = self.create_word_data(words)
        
        # Very high similarity threshold for unrelated query
        results = speech_fuzzy_match(
            word_list, "hello world", similarity_range=(0.95, 1.0)
        )
        
        assert len(results) == 0

    def test_single_word_window(self):
        """Test that single word queries work correctly"""
        words = ["apple", "banana", "cherry", "date"]
        word_list = self.create_word_data(words)
        
        results = speech_fuzzy_match(word_list, "banana")
        
        assert len(results) > 0
        # Should find exact match
        best_match = results[0]
        assert best_match[2] == 1.0  # Perfect similarity
        assert best_match[0] == best_match[1] == 1  # Single word at index 1

    def test_results_sorted_by_similarity(self):
        """Test that results are sorted by similarity score in descending order"""
        words = ["hello", "helo", "help", "world"]  # Different similarities to "hello"
        word_list = self.create_word_data(words)
        
        results = speech_fuzzy_match(word_list, "hello", similarity_range=(0.0, 1.0))
        
        assert len(results) >= 2
        # Check that similarities are in descending order
        for i in range(len(results) - 1):
            assert results[i][2] >= results[i+1][2]

    def test_query_longer_than_word_list(self):
        """Test handling when query has more words than available in word_list"""
        words = ["short", "list"]
        word_list = self.create_word_data(words)
        
        results = speech_fuzzy_match(word_list, "this is a much longer query than available")
        
        # Should still return some results (checking smaller windows)
        # Results might have low similarity, but function shouldn't crash
        assert isinstance(results, list)

    def test_dataclass_word_extraction(self):
        """Test that the function correctly extracts words from WordData objects"""
        word_data_list = [
            WordData(
                type="word",
                speaker="speaker1", 
                start=0.0,
                end=1.0,
                text="Hello",  # Different from word field
                word="hello",  # This should be used for matching
                word_position=0,
                confidence=0.95,
                overlap_duration=0.0,
                utterance_number=1
            ),
            WordData(
                type="word",
                speaker="speaker1",
                start=1.0,
                end=2.0, 
                text="World",
                word="world",
                word_position=1,
                confidence=0.92,
                overlap_duration=0.0,
                utterance_number=1
            )
        ]
        
        results = speech_fuzzy_match(word_data_list, "hello world")
        
        assert len(results) > 0
        assert results[0][2] == 1.0  # Should match perfectly using 'word' field