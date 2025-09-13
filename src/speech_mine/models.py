from typing import Optional
from dataclasses import dataclass


@dataclass
class WordData:
    """Data class for individual word information"""
    type: str
    speaker: str
    start: float
    end: float
    text: str
    word: str
    word_position: int
    confidence: float
    overlap_duration: float
    utterance_number: Optional[int] = None


@dataclass
class SegmentData:
    """Data class for segment information"""
    type: str
    speaker: str
    start: float
    end: float
    text: str
    word: str
    word_position: Optional[int]
    confidence: float
    overlap_duration: float
    utterance_number: Optional[int] = None