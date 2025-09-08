"""
Script Extractor - Speech-to-Text with Speaker Diarization

A Python package for extracting transcripts from audio files with speaker diarization
and word-level timestamps.
"""

__version__ = "0.1.0"
__author__ = "Beckett Frey"

from .processor import SpeechDiarizationProcessor
from .formatter import ScriptFormatter

__all__ = ["SpeechDiarizationProcessor", "ScriptFormatter"]
