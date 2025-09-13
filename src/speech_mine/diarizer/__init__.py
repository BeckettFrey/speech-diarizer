"""
Script Extractor - Speech-to-Text with Speaker Diarization

A Python package for extracting transcripts from audio files with speaker diarization
and word-level timestamps.
"""

from .processor import SpeechDiarizationProcessor
from .formatter import ScriptFormatter
from .models import DiaryMetadata

__all__ = ["SpeechDiarizationProcessor", "ScriptFormatter", "DiaryMetadata"]
