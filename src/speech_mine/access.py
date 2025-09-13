import csv
import json
from typing import Dict, List, Optional, Union, Any
from io import StringIO
from .models import SegmentData, WordData


class TranscriptionAccessTool:
    """
    A tool for efficiently accessing transcription data with word-level information.
    Allows retrieval of individual words and ranges by utterance and index.
    """
    
    def __init__(self):
        self.segments: List[SegmentData] = []
        self.words: List[WordData] = []
        self.utterance_map: Dict[int, SegmentData] = {}
        self.words_by_utterance: Dict[int, List[WordData]] = {}
        self.metadata: Dict[str, Any] = {}
    
    def load_data(self, csv_data: str, metadata: Dict[str, Any] = None):
        """
        Load data from CSV string and metadata dictionary
        
        Args:
            csv_data: The CSV data as a string
            metadata: The metadata dictionary
        """
        self.metadata = metadata or {}
        self._parse_csv(csv_data)
        self._build_indexes()
    
    def load_from_files(self, csv_file_path: str, metadata_file_path: str = None):
        """
        Load data from CSV file and optional metadata JSON file
        
        Args:
            csv_file_path: Path to the CSV file
            metadata_file_path: Path to the metadata JSON file (optional)
        """
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            csv_data = f.read()
        
        metadata = {}
        if metadata_file_path:
            with open(metadata_file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        
        self.load_data(csv_data, metadata)
    
    def _parse_csv(self, csv_data: str):
        """Parse CSV data and separate segments from words"""
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)
        
        self.segments = []
        self.words = []
        
        for row in reader:
            # Convert numeric fields
            numeric_fields = ['start', 'end', 'word_position', 'confidence', 'overlap_duration']
            for field in numeric_fields:
                if row[field] == '':
                    row[field] = None
                else:
                    try:
                        if field == 'word_position':
                            row[field] = int(row[field]) if row[field] is not None else None
                        else:
                            row[field] = float(row[field]) if row[field] is not None else None
                    except (ValueError, TypeError):
                        row[field] = None
            
            if row['type'] == 'segment':
                segment = SegmentData(**row)
                self.segments.append(segment)
            elif row['type'] == 'word':
                word = WordData(**row)
                self.words.append(word)
    
    def _build_indexes(self):
        """Build indexes for efficient lookups"""
        # Collect unique utterance texts and assign numbers
        utterance_texts = []
        seen_texts = set()
        
        for segment in self.segments:
            if segment.text and segment.text.strip() and segment.text.strip() not in seen_texts:
                utterance_texts.append(segment.text.strip())
                seen_texts.add(segment.text.strip())
        
        text_to_utterance_num = {text: i for i, text in enumerate(utterance_texts)}
        
        # Map segments to utterance numbers
        for segment in self.segments:
            if segment.text and segment.text.strip():
                utt_num = text_to_utterance_num.get(segment.text.strip())
                if utt_num is not None:
                    segment.utterance_number = utt_num
                    self.utterance_map[utt_num] = segment
        
        # Group words by utterance
        for word in self.words:
            if word.text and word.text.strip():
                utt_num = text_to_utterance_num.get(word.text.strip())
                if utt_num is not None:
                    word.utterance_number = utt_num
                    if utt_num not in self.words_by_utterance:
                        self.words_by_utterance[utt_num] = []
                    self.words_by_utterance[utt_num].append(word)
        
        # Sort words within each utterance by word_position
        for words in self.words_by_utterance.values():
            words.sort(key=lambda w: w.word_position if w.word_position is not None else 0)
    
    def get_word(self, utterance_num: int, word_index: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific word by utterance number and word index
        
        Args:
            utterance_num: The utterance number
            word_index: The index of the word within the utterance
            
        Returns:
            Dictionary with word data and metadata, or None if not found
        """
        if utterance_num not in self.words_by_utterance:
            return None
        
        words = self.words_by_utterance[utterance_num]
        if word_index < 0 or word_index >= len(words):
            return None
        
        word = words[word_index]
        segment = self.utterance_map.get(utterance_num)
        
        return {
            'utterance_number': utterance_num,
            'word_index': word_index,
            'word_data': word.__dict__,
            'segment_data': segment.__dict__ if segment else None,
            'total_words_in_utterance': len(words)
        }
    
    def get_word_range(self, utterance_num: int, start_index: int, end_index: int) -> Optional[Dict[str, Any]]:
        """
        Get a range of words within an utterance
        
        Args:
            utterance_num: The utterance number
            start_index: Starting word index (inclusive)
            end_index: Ending word index (inclusive)
            
        Returns:
            Dictionary with range data in the specified format, or None if not found
        """
        if utterance_num not in self.words_by_utterance:
            return None
        
        words = self.words_by_utterance[utterance_num]
        
        # Validate and adjust indices
        actual_start = max(0, start_index)
        actual_end = min(len(words) - 1, end_index)
        
        if actual_start > actual_end:
            return None
        
        range_words = words[actual_start:actual_end + 1]
        segment = self.utterance_map.get(utterance_num)
        
        return {
            'start_window': actual_start,
            'end_window': actual_end,
            'utterance_number': utterance_num,
            'words': [word.__dict__ for word in range_words],
            'segment_data': segment.__dict__ if segment else None,
            'word_count': len(range_words),
            'time_span': {
                'start': range_words[0].start,
                'end': range_words[-1].end,
                'duration': range_words[-1].end - range_words[0].start
            } if range_words else None
        }
    
    def get_utterance(self, utterance_num: int) -> Optional[Dict[str, Any]]:
        """
        Get all words in an utterance
        
        Args:
            utterance_num: The utterance number
            
        Returns:
            Complete utterance data or None if not found
        """
        if utterance_num not in self.words_by_utterance:
            return None
        
        words = self.words_by_utterance[utterance_num]
        segment = self.utterance_map.get(utterance_num)
        
        return {
            'utterance_number': utterance_num,
            'segment_data': segment.__dict__ if segment else None,
            'words': [word.__dict__ for word in words],
            'word_count': len(words),
            'duration': segment.end - segment.start if segment else None
        }
    
    def search_words(self, search_text: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Search for words containing specific text
        
        Args:
            search_text: Text to search for
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            List of matching words with their locations
        """
        results = []
        search_term = search_text if case_sensitive else search_text.lower()
        
        for utterance_num, words in self.words_by_utterance.items():
            for index, word in enumerate(words):
                word_text = word.word if case_sensitive else word.word.lower()
                if search_term in word_text:
                    results.append({
                        'utterance_number': utterance_num,
                        'word_index': index,
                        'word_data': word.__dict__,
                        'match_text': search_term
                    })
        
        return results
    
    def get_words_by_time_range(self, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """
        Get words within a specific time range
        
        Args:
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            List of words within the time range
        """
        results = []
        
        for word in self.words:
            if word.start >= start_time and word.end <= end_time:
                results.append(word.__dict__)
        
        # Sort by start time
        results.sort(key=lambda w: w['start'])
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the transcription
        
        Returns:
            Statistics dictionary
        """
        total_utterances = len(self.utterance_map)
        total_words = len(self.words)
        speakers = list(set(word.speaker for word in self.words))
        
        confidence_scores = [word.confidence for word in self.words 
                           if word.confidence is not None]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        stats = {
            'total_utterances': total_utterances,
            'total_words': total_words,
            'total_speakers': len(speakers),
            'speakers': speakers,
            'average_confidence': avg_confidence,
            'duration': self.metadata.get('duration', 0)
        }
        
        stats.update(self.metadata)
        return stats
    
    def export(self, format_type: str = 'json') -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Export data in various formats
        
        Args:
            format_type: Export format ('json', 'words', 'segments', 'utterances')
            
        Returns:
            Exported data in the specified format
        """
        if format_type == 'words':
            return [word.__dict__ for word in self.words]
        elif format_type == 'segments':
            return [segment.__dict__ for segment in self.segments]
        elif format_type == 'utterances':
            utterances = []
            for utt_num, segment in self.utterance_map.items():
                utterances.append({
                    'utterance_number': utt_num,
                    'segment': segment.__dict__,
                    'words': [word.__dict__ for word in self.words_by_utterance.get(utt_num, [])]
                })
            return utterances
        else:  # 'json'
            return {
                'metadata': self.metadata,
                'utterances': self.export('utterances'),
                'stats': self.get_stats()
            }

# Example usage:
if __name__ == "__main__":
    # Load CSV from file
    csv_file_path = "transcription.csv" 
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        csv_data = f.read()

    # Load metadata from JSON file if it exists
    metadata_file_path = "metadata.json"
    metadata = {}
    try:
        with open(metadata_file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except FileNotFoundError:
        metadata = {}

    # Initialize and load data
    tool = TranscriptionAccessTool()
    tool.load_data(csv_data, metadata)
    
    # Example usage:
    # Get individual word
    word = tool.get_word(0, 2)  # Utterance 0, word index 2
    print("Single word:", word)
    
    # Get word range
    word_range = tool.get_word_range(0, 1, 3)  # Utterance 0, words 1-3
    print("Word range:", word_range)
    
    # Get full utterance
    utterance = tool.get_utterance(0)
    print("Full utterance:", utterance)
    
    # Search functionality
    matches = tool.search_words("tea")
    print("Search results:", matches)
    
    # Get statistics
    stats = tool.get_stats()
    print("Statistics:", stats)