"""
Script formatting module.

This module contains the ScriptFormatter class that converts CSV transcripts
into beautifully formatted movie-style scripts for better visualization.
"""

import csv
import json
import os
import re
from typing import Dict, List, Optional


class ScriptFormatter:
    """
    Formatter for converting CSV transcripts to movie-style scripts.
    """
    
    def __init__(self, custom_speakers: Optional[Dict[str, str]] = None):
        """
        Initialize the formatter.
        
        Args:
            custom_speakers: Optional dict mapping SPEAKER_XX to custom names
        """
        self.custom_speakers = custom_speakers or {}
    
    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Format seconds into MM:SS format."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    @staticmethod
    def format_duration(start_seconds: float, end_seconds: float) -> str:
        """Format duration as [MM:SS - MM:SS]."""
        return f"[{ScriptFormatter.format_timestamp(start_seconds)} - {ScriptFormatter.format_timestamp(end_seconds)}]"
    
    @staticmethod
    def clean_speaker_name(speaker: str) -> str:
        """Convert SPEAKER_00 format to more readable names."""
        if speaker.startswith("SPEAKER_"):
            number = speaker.replace("SPEAKER_", "")
            try:
                num = int(number)
                # Convert to more readable speaker names
                speaker_names = [
                    "SPEAKER A", "SPEAKER B", "SPEAKER C", "SPEAKER D", 
                    "SPEAKER E", "SPEAKER F", "SPEAKER G", "SPEAKER H",
                    "SPEAKER I", "SPEAKER J"
                ]
                if num < len(speaker_names):
                    return speaker_names[num]
                else:
                    return f"SPEAKER {chr(65 + num)}"  # A, B, C, etc.
            except ValueError:
                pass
        return speaker
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and format text for better readability."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common transcription issues
        text = text.replace(' .', '.')
        text = text.replace(' ,', ',')
        text = text.replace(' ?', '?')
        text = text.replace(' !', '!')
        
        # Ensure sentences end with proper punctuation
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text
    
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into sentences for better formatting."""
        # Simple sentence splitting - can be improved
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def load_segments_from_csv(self, csv_file: str) -> List[Dict]:
        """
        Load segments from CSV file.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            List of segment dictionaries
        """
        segments = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['type'] == 'segment':  # Only process segments, not individual words
                    segments.append({
                        'speaker': row['speaker'],
                        'start': float(row['start']),
                        'end': float(row['end']),
                        'text': row['text'],
                        'confidence': float(row['confidence']) if row['confidence'] else 0.0
                    })
        
        return segments
    
    def load_metadata(self, csv_file: str) -> Dict:
        """
        Load metadata from companion JSON file.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            Metadata dictionary
        """
        metadata_file = csv_file.replace('.csv', '_metadata.json')
        metadata = {}
        
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except Exception:
                pass
        
        return metadata
    
    def format_script(self, csv_file: str, output_file: str) -> None:
        """
        Format the CSV transcript into a movie-style script.
        
        Args:
            csv_file: Path to input CSV file
            output_file: Path to output text file
        """
        print(f"📖 Formatting script from: {csv_file}")
        print(f"📝 Output will be saved to: {output_file}")
        
        # Read CSV data and metadata
        try:
            segments = self.load_segments_from_csv(csv_file)
        except FileNotFoundError:
            print(f"❌ Error: File '{csv_file}' not found.")
            return
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return
        
        if not segments:
            print("❌ No segments found in CSV file.")
            return
        
        metadata = self.load_metadata(csv_file)
        
        # Create output content
        lines = []
        
        # Header
        lines.append("=" * 80)
        lines.append("TRANSCRIPT")
        lines.append("=" * 80)
        lines.append("")
        
        # Metadata section
        if metadata:
            lines.append("RECORDING DETAILS:")
            lines.append("-" * 40)
            if 'audio_file' in metadata:
                filename = os.path.basename(metadata['audio_file'])
                lines.append(f"File: {filename}")
            if 'duration' in metadata:
                total_duration = self.format_timestamp(metadata['duration'])
                lines.append(f"Duration: {total_duration}")
            if 'language' in metadata:
                confidence = metadata.get('language_probability', 0)
                lines.append(f"Language: {metadata['language'].upper()} (confidence: {confidence:.1%})")
            if 'speakers' in metadata:
                speaker_count = len(metadata['speakers'])
                lines.append(f"Speakers: {speaker_count}")
            if 'processing_timestamp' in metadata:
                lines.append(f"Processed: {metadata['processing_timestamp']}")
            lines.append("")
        
        # Speaker legend
        unique_speakers = list(set(segment['speaker'] for segment in segments))
        unique_speakers.sort()
        
        if len(unique_speakers) > 1:
            lines.append("CAST:")
            lines.append("-" * 40)
            for speaker in unique_speakers:
                clean_name = self.custom_speakers.get(speaker, self.clean_speaker_name(speaker))
                lines.append(f"{clean_name}")
            lines.append("")
        
        lines.append("TRANSCRIPT:")
        lines.append("-" * 40)
        lines.append("")
        
        # Format segments
        current_speaker = None
        
        for i, segment in enumerate(segments):
            speaker = segment['speaker']
            text = self.clean_text(segment['text'])
            start_time = segment['start']
            end_time = segment['end']
            confidence = segment['confidence']
            
            # Get clean speaker name
            clean_name = self.custom_speakers.get(speaker, self.clean_speaker_name(speaker))
            
            # Add speaker change indicator
            if speaker != current_speaker:
                if current_speaker is not None:  # Not the first speaker
                    lines.append("")  # Empty line between different speakers
                
                # Add timestamp and speaker name
                timestamp = self.format_duration(start_time, end_time)
                confidence_indicator = ""
                if confidence < 0.5:
                    confidence_indicator = " [LOW CONFIDENCE]"
                
                lines.append(f"{timestamp} {clean_name}{confidence_indicator}:")
                current_speaker = speaker
            
            # Format the text - split long segments for readability
            if len(text) > 100:
                # Split into sentences for long segments
                sentences = self.split_into_sentences(text)
                for j, sentence in enumerate(sentences):
                    lines.append(f"    {sentence}")
            else:
                lines.append(f"    {text}")
            
            # Add pause indicators for long gaps
            if i < len(segments) - 1:
                next_segment = segments[i + 1]
                gap = next_segment['start'] - end_time
                
                if gap > 3.0:  # More than 3 seconds gap
                    gap_duration = self.format_timestamp(gap)
                    lines.append(f"")
                    lines.append(f"    [...{gap_duration} pause...]")
                    lines.append(f"")
        
        # Footer
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"END OF TRANSCRIPT")
        if metadata and 'total_segments' in metadata:
            lines.append(f"Total segments: {metadata['total_segments']}")
        if metadata and 'total_words' in metadata:
            lines.append(f"Total words: {metadata['total_words']}")
        lines.append("=" * 80)
        
        # Write to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Script formatted successfully!")
            print(f"📄 Output saved to: {output_file}")
            print(f"📊 Processed {len(segments)} segments from {len(unique_speakers)} speakers")
            
        except Exception as e:
            print(f"❌ Error writing output file: {e}")
    
    @staticmethod
    def create_custom_speakers_template(csv_file: str) -> str:
        """
        Create a template file for custom speaker names.
        
        Args:
            csv_file: Path to CSV file
            
        Returns:
            Path to created template file
        """
        # Read speakers from CSV
        speakers = set()
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['type'] == 'segment':
                        speakers.add(row['speaker'])
        except Exception:
            return ""
        
        speakers = sorted(speakers)
        
        # Create JSON template
        template = {
            speaker: f"PERSON_{i+1}" for i, speaker in enumerate(speakers)
        }
        
        template_file = csv_file.replace('.csv', '_speaker_names.json')
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template, f, indent=2)
            return template_file
        except Exception:
            return ""
    
    @staticmethod
    def load_custom_speakers(json_file: str) -> Optional[Dict[str, str]]:
        """
        Load custom speaker names from JSON file.
        
        Args:
            json_file: Path to JSON file
            
        Returns:
            Dictionary of speaker mappings or None
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
