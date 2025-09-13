from dataclasses import dataclass  


@dataclass
class DiaryMetadata:
    """Data class for audio file metadata and processing information"""
    audio_file: str
    language: str
    language_probability: float
    duration: float
    total_segments: int
    total_words: int
    speakers: list[str]
    processing_timestamp: str
