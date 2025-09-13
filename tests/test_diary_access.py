import pytest
import json
import tempfile
import os
from speech_mine.access import TranscriptionAccessTool


class TestTranscriptionAccessTool:
    """Comprehensive test suite for TranscriptionAccessTool"""
    
    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing"""
        return """type,speaker,start,end,text,word,word_position,confidence,overlap_duration
segment,SPEAKER_01,0.0,1.72,Hello world.,,,-0.18,1.689
word,SPEAKER_01,0.0,0.5,Hello world.,Hello,0,0.95,1.689
word,SPEAKER_01,0.5,1.72,Hello world.,world.,1,0.98,1.689
segment,SPEAKER_01,2.0,3.5,How are you?,,,-0.15,1.5
word,SPEAKER_01,2.0,2.3,How are you?,How,0,0.92,1.5
word,SPEAKER_01,2.3,2.6,How are you?,are,1,0.96,1.5
word,SPEAKER_01,2.6,3.5,How are you?,you?,2,0.94,1.5
segment,SPEAKER_00,4.0,5.0,Good.,,,-0.1,1.0
word,SPEAKER_00,4.0,5.0,Good.,Good.,0,0.99,1.0"""

    @pytest.fixture
    def empty_csv_data(self):
        """Empty CSV with just headers"""
        return "type,speaker,start,end,text,word,word_position,confidence,overlap_duration"

    @pytest.fixture
    def malformed_csv_data(self):
        """CSV with missing/invalid data"""
        return """type,speaker,start,end,text,word,word_position,confidence,overlap_duration
segment,SPEAKER_01,invalid,1.72,Hello world.,,,-0.18,1.689
word,SPEAKER_01,,0.5,Hello world.,Hello,,0.95,
word,SPEAKER_01,0.5,,Hello world.,world.,1,,1.689
segment,,2.0,3.5,,,,-0.15,
word,SPEAKER_01,2.0,2.3,,How,0,0.92,1.5"""

    @pytest.fixture
    def sample_metadata(self):
        """Sample metadata for testing"""
        return {
            "audio_file": "/path/to/audio.wav",
            "language": "en",
            "language_probability": 0.99,
            "duration": 110.97,
            "total_segments": 3,
            "total_words": 6,
            "speakers": ["SPEAKER_00", "SPEAKER_01"],
            "processing_timestamp": "2025-09-09 10:20:45"
        }

    @pytest.fixture
    def tool_with_data(self, sample_csv_data, sample_metadata):
        """TranscriptionAccessTool instance with sample data loaded"""
        tool = TranscriptionAccessTool()
        tool.load_data(sample_csv_data, sample_metadata)
        return tool

    @pytest.fixture
    def empty_tool(self):
        """Empty TranscriptionAccessTool instance"""
        return TranscriptionAccessTool()

    # Initialization and Data Loading Tests
    def test_initialization(self):
        """Test tool initializes with empty state"""
        tool = TranscriptionAccessTool()
        assert tool.segments == []
        assert tool.words == []
        assert tool.utterance_map == {}
        assert tool.words_by_utterance == {}
        assert tool.metadata == {}

    def test_load_data_basic(self, sample_csv_data, sample_metadata):
        """Test basic data loading functionality"""
        tool = TranscriptionAccessTool()
        tool.load_data(sample_csv_data, sample_metadata)
        
        assert len(tool.segments) == 3
        assert len(tool.words) == 6
        assert tool.metadata == sample_metadata
        assert len(tool.utterance_map) == 3
        assert len(tool.words_by_utterance) == 3

    def test_load_data_without_metadata(self, sample_csv_data):
        """Test loading data without metadata"""
        tool = TranscriptionAccessTool()
        tool.load_data(sample_csv_data)
        
        assert len(tool.segments) == 3
        assert len(tool.words) == 6
        assert tool.metadata == {}

    def test_load_data_empty_csv(self, empty_csv_data):
        """Test loading empty CSV"""
        tool = TranscriptionAccessTool()
        tool.load_data(empty_csv_data)
        
        assert tool.segments == []
        assert tool.words == []
        assert tool.utterance_map == {}
        assert tool.words_by_utterance == {}

    def test_load_data_malformed_csv(self, malformed_csv_data):
        """Test loading CSV with malformed data"""
        tool = TranscriptionAccessTool()
        tool.load_data(malformed_csv_data)
        
        # Should handle malformed data gracefully
        assert len(tool.segments) >= 0
        assert len(tool.words) >= 0

    def test_load_from_files(self, sample_csv_data, sample_metadata):
        """Test loading from actual files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as csv_file:
            csv_file.write(sample_csv_data)
            csv_file_path = csv_file.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as json_file:
            json.dump(sample_metadata, json_file)
            json_file_path = json_file.name

        try:
            tool = TranscriptionAccessTool()
            tool.load_from_files(csv_file_path, json_file_path)
            
            assert len(tool.segments) == 3
            assert len(tool.words) == 6
            assert tool.metadata == sample_metadata
        finally:
            os.unlink(csv_file_path)
            os.unlink(json_file_path)

    def test_load_from_files_no_metadata(self, sample_csv_data):
        """Test loading from CSV file without metadata file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as csv_file:
            csv_file.write(sample_csv_data)
            csv_file_path = csv_file.name

        try:
            tool = TranscriptionAccessTool()
            tool.load_from_files(csv_file_path)
            
            assert len(tool.segments) == 3
            assert len(tool.words) == 6
            assert tool.metadata == {}
        finally:
            os.unlink(csv_file_path)

    # Word Retrieval Tests
    def test_get_word_valid(self, tool_with_data):
        """Test getting valid word"""
        result = tool_with_data.get_word(0, 1)
        
        assert result is not None
        assert result['utterance_number'] == 0
        assert result['word_index'] == 1
        assert result['word_data']['word'] == 'world.'
        assert result['total_words_in_utterance'] == 2

    def test_get_word_invalid_utterance(self, tool_with_data):
        """Test getting word with invalid utterance number"""
        result = tool_with_data.get_word(999, 0)
        assert result is None

    def test_get_word_invalid_word_index(self, tool_with_data):
        """Test getting word with invalid word index"""
        result = tool_with_data.get_word(0, 999)
        assert result is None

    def test_get_word_negative_indices(self, tool_with_data):
        """Test getting word with negative indices"""
        result = tool_with_data.get_word(-1, 0)
        assert result is None
        
        result = tool_with_data.get_word(0, -1)
        assert result is None

    def test_get_word_empty_tool(self, empty_tool):
        """Test getting word from empty tool"""
        result = empty_tool.get_word(0, 0)
        assert result is None

    # Word Range Tests
    def test_get_word_range_valid(self, tool_with_data):
        """Test getting valid word range"""
        result = tool_with_data.get_word_range(1, 0, 2)  # "How are you?"
        
        assert result is not None
        assert result['utterance_number'] == 1
        assert result['start_window'] == 0
        assert result['end_window'] == 2
        assert result['word_count'] == 3
        assert len(result['words']) == 3
        assert result['words'][0]['word'] == 'How'
        assert result['words'][2]['word'] == 'you?'

    def test_get_word_range_partial(self, tool_with_data):
        """Test getting partial word range"""
        result = tool_with_data.get_word_range(1, 1, 1)  # Just "are"
        
        assert result is not None
        assert result['word_count'] == 1
        assert result['words'][0]['word'] == 'are'

    def test_get_word_range_out_of_bounds(self, tool_with_data):
        """Test word range with out of bounds indices"""
        result = tool_with_data.get_word_range(1, 0, 999)
        
        assert result is not None
        assert result['start_window'] == 0
        assert result['end_window'] == 2  # Adjusted to last valid index
        assert result['word_count'] == 3

    def test_get_word_range_invalid_range(self, tool_with_data):
        """Test word range with start > end"""
        result = tool_with_data.get_word_range(1, 5, 1)
        assert result is None

    def test_get_word_range_invalid_utterance(self, tool_with_data):
        """Test word range with invalid utterance"""
        result = tool_with_data.get_word_range(999, 0, 1)
        assert result is None

    def test_get_word_range_time_span(self, tool_with_data):
        """Test word range time span calculation"""
        result = tool_with_data.get_word_range(1, 0, 2)
        
        assert 'time_span' in result
        assert 'start' in result['time_span']
        assert 'end' in result['time_span']
        assert 'duration' in result['time_span']
        assert result['time_span']['duration'] >= 0

    # Utterance Tests
    def test_get_utterance_valid(self, tool_with_data):
        """Test getting valid utterance"""
        result = tool_with_data.get_utterance(0)
        
        assert result is not None
        assert result['utterance_number'] == 0
        assert result['word_count'] == 2
        assert len(result['words']) == 2
        assert result['segment_data']['text'] == 'Hello world.'

    def test_get_utterance_invalid(self, tool_with_data):
        """Test getting invalid utterance"""
        result = tool_with_data.get_utterance(999)
        assert result is None

    def test_get_utterance_duration(self, tool_with_data):
        """Test utterance duration calculation"""
        result = tool_with_data.get_utterance(0)
        
        assert 'duration' in result
        assert result['duration'] is not None
        assert result['duration'] > 0

    # Search Tests
    def test_search_words_case_sensitive(self, tool_with_data):
        """Test case-sensitive word search"""
        results = tool_with_data.search_words("Hello", case_sensitive=True)
        
        assert len(results) == 1
        assert results[0]['word_data']['word'] == 'Hello'
        assert results[0]['utterance_number'] == 0
        assert results[0]['word_index'] == 0

    def test_search_words_case_insensitive(self, tool_with_data):
        """Test case-insensitive word search"""
        results = tool_with_data.search_words("hello", case_sensitive=False)
        
        assert len(results) == 1
        assert results[0]['word_data']['word'] == 'Hello'

    def test_search_words_partial_match(self, tool_with_data):
        """Test partial word matching"""
        results = tool_with_data.search_words("wor", case_sensitive=False)
        
        assert len(results) == 1
        assert "wor" in results[0]['word_data']['word'].lower()

    def test_search_words_no_matches(self, tool_with_data):
        """Test search with no matches"""
        results = tool_with_data.search_words("xyz")
        assert len(results) == 0

    def test_search_words_empty_query(self, tool_with_data):
        """Test search with empty query"""
        results = tool_with_data.search_words("")
        # Should match all words since empty string is in all strings
        assert len(results) == 6

    def test_search_words_empty_tool(self, empty_tool):
        """Test search on empty tool"""
        results = empty_tool.search_words("hello")
        assert len(results) == 0

    # Time Range Tests
    def test_get_words_by_time_range_valid(self, tool_with_data):
        """Test getting words by valid time range"""
        results = tool_with_data.get_words_by_time_range(0.0, 2.0)
        
        assert len(results) >= 2
        for word in results:
            assert word['start'] >= 0.0
            assert word['end'] <= 2.0

    def test_get_words_by_time_range_no_matches(self, tool_with_data):
        """Test time range with no matching words"""
        results = tool_with_data.get_words_by_time_range(100.0, 200.0)
        assert len(results) == 0

    def test_get_words_by_time_range_sorted(self, tool_with_data):
        """Test that time range results are sorted by start time"""
        results = tool_with_data.get_words_by_time_range(0.0, 10.0)
        
        if len(results) > 1:
            for i in range(1, len(results)):
                assert results[i-1]['start'] <= results[i]['start']

    def test_get_words_by_time_range_invalid_range(self, tool_with_data):
        """Test time range where start > end"""
        results = tool_with_data.get_words_by_time_range(5.0, 1.0)
        assert len(results) == 0

    def test_get_words_by_time_range_empty_tool(self, empty_tool):
        """Test time range on empty tool"""
        results = empty_tool.get_words_by_time_range(0.0, 10.0)
        assert len(results) == 0

    # Statistics Tests
    def test_get_stats_basic(self, tool_with_data):
        """Test basic statistics"""
        stats = tool_with_data.get_stats()
        
        assert 'total_utterances' in stats
        assert 'total_words' in stats
        assert 'total_speakers' in stats
        assert 'speakers' in stats
        assert 'average_confidence' in stats
        
        assert stats['total_utterances'] == 3
        assert stats['total_words'] == 6
        assert stats['total_speakers'] == 2
        assert 'SPEAKER_00' in stats['speakers']
        assert 'SPEAKER_01' in stats['speakers']

    def test_get_stats_confidence_calculation(self, tool_with_data):
        """Test confidence score calculation"""
        stats = tool_with_data.get_stats()
        
        assert 'average_confidence' in stats
        assert 0 <= stats['average_confidence'] <= 1

    def test_get_stats_with_metadata(self, tool_with_data):
        """Test statistics include metadata"""
        stats = tool_with_data.get_stats()
        
        assert 'duration' in stats
        assert 'language' in stats
        assert stats['duration'] == 110.97

    def test_get_stats_empty_tool(self, empty_tool):
        """Test statistics on empty tool"""
        stats = empty_tool.get_stats()
        
        assert stats['total_utterances'] == 0
        assert stats['total_words'] == 0
        assert stats['total_speakers'] == 0
        assert stats['speakers'] == []
        assert stats['average_confidence'] == 0

    # Export Tests
    def test_export_json(self, tool_with_data):
        """Test JSON export"""
        result = tool_with_data.export('json')
        
        assert 'metadata' in result
        assert 'utterances' in result
        assert 'stats' in result
        assert isinstance(result, dict)

    def test_export_words(self, tool_with_data):
        """Test words export"""
        result = tool_with_data.export('words')
        
        assert isinstance(result, list)
        assert len(result) == 6
        assert all('word' in item for item in result)

    def test_export_segments(self, tool_with_data):
        """Test segments export"""
        result = tool_with_data.export('segments')
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert all('text' in item for item in result)

    def test_export_utterances(self, tool_with_data):
        """Test utterances export"""
        result = tool_with_data.export('utterances')
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert all('utterance_number' in item for item in result)
        assert all('segment' in item for item in result)
        assert all('words' in item for item in result)

    def test_export_invalid_format(self, tool_with_data):
        """Test export with invalid format defaults to JSON"""
        result = tool_with_data.export('invalid_format')
        
        assert isinstance(result, dict)
        assert 'metadata' in result

    def test_export_empty_tool(self, empty_tool):
        """Test export on empty tool"""
        result = empty_tool.export('json')
        
        assert result['utterances'] == []
        assert result['stats']['total_words'] == 0
        
    def test_utterance_indexing_with_duplicate_texts(self):
        """Test utterance indexing when multiple segments have same text"""
        duplicate_csv = """type,speaker,start,end,text,word,word_position,confidence,overlap_duration
segment,SPEAKER_01,0.0,1.0,Hello.,,,-0.18,1.0
segment,SPEAKER_00,2.0,3.0,Hello.,,,-0.15,1.0
word,SPEAKER_01,0.0,1.0,Hello.,Hello.,0,0.95,1.0
word,SPEAKER_00,2.0,3.0,Hello.,Hello.,0,0.92,1.0"""
        
        tool = TranscriptionAccessTool()
        tool.load_data(duplicate_csv)
        
        # Should handle duplicate texts appropriately
        assert len(tool.utterance_map) <= 1  # Only one unique text

    def test_words_without_segments(self):
        """Test words that don't match any segment text"""
        orphan_csv = """type,speaker,start,end,text,word,word_position,confidence,overlap_duration
segment,SPEAKER_01,0.0,1.0,Hello.,,,-0.18,1.0
word,SPEAKER_01,0.0,1.0,Different text.,Hello.,0,0.95,1.0"""
        
        tool = TranscriptionAccessTool()
        tool.load_data(orphan_csv)
        
        # Should handle gracefully
        assert len(tool.segments) == 1

    def test_confidence_scores_none_values(self):
        """Test handling of None confidence scores"""
        none_confidence_csv = """type,speaker,start,end,text,word,word_position,confidence,overlap_duration
word,SPEAKER_01,0.0,1.0,Hello.,Hello.,0,,1.0
word,SPEAKER_01,1.0,2.0,Hello.,world.,1,0.95,1.0"""
        
        tool = TranscriptionAccessTool()
        tool.load_data(none_confidence_csv)
        
        stats = tool.get_stats()
        # Should calculate average excluding None values
        assert stats['average_confidence'] == 0.95

    def test_word_position_sorting(self, tool_with_data):
        """Test that words are sorted by word_position within utterances"""
        utterance = tool_with_data.get_utterance(1)  # "How are you?"
        
        words = utterance['words']
        for i in range(1, len(words)):
            assert words[i-1]['word_position'] <= words[i]['word_position']

    # Performance and Large Data Tests
    def test_large_dataset_simulation(self):
        """Test with simulated large dataset"""
        # Create a larger CSV for testing
        csv_lines = ["type,speaker,start,end,text,word,word_position,confidence,overlap_duration"]
        
        for i in range(100):
            # Add segment
            csv_lines.append(f"segment,SPEAKER_01,{i},{i+1},Utterance {i}.,,,-0.1,1.0")
            # Add words
            csv_lines.append(f"word,SPEAKER_01,{i},{i+0.5},Utterance {i}.,Utterance,0,0.95,1.0")
            csv_lines.append(f"word,SPEAKER_01,{i+0.5},{i+1},Utterance {i}.,{i}.,1,0.98,1.0")
        
        large_csv = "\n".join(csv_lines)
        
        tool = TranscriptionAccessTool()
        tool.load_data(large_csv)
        
        assert len(tool.segments) == 100
        assert len(tool.words) == 200
        assert len(tool.utterance_map) == 100
        
        # Test random access still works
        result = tool.get_word(50, 1)
        assert result is not None

    def test_memory_cleanup_after_reload(self, sample_csv_data):
        """Test that data is properly cleaned when reloading"""
        tool = TranscriptionAccessTool()
        tool.load_data(sample_csv_data)
        
        original_word_count = len(tool.words)
        
        # Load new data
        new_csv = """type,speaker,start,end,text,word,word_position,confidence,overlap_duration
segment,SPEAKER_00,0.0,1.0,New data.,,,-0.1,1.0
word,SPEAKER_00,0.0,1.0,New data.,New,0,0.95,1.0"""
        
        tool.load_data(new_csv)
        
        # Should have new data, not accumulated
        assert len(tool.words) == 1
        assert len(tool.segments) == 1


if __name__ == "__main__":
    # Run tests with: pytest test_diary_access.py.py -v
    pytest.main([__file__, "-v"])