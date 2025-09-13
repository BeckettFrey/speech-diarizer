"""
Speech Mine: A comprehensive toolkit for speech processing and analysis.

This package provides tools for speech diarization, transcription access, and fuzzy matching
of speech data. It includes processors for handling audio diarization, formatters for script
output, metadata management, and utilities for accessing and searching transcription data.
"""

from .diarizer import SpeechDiarizationProcessor, ScriptFormatter, DiaryMetadata
from .access import TranscriptionAccessTool
from .fuzz import speech_fuzzy_match, WordData

__all__ = ["SpeechDiarizationProcessor", "TranscriptionAccessTool", "speech_fuzzy_match", "WordData", "ScriptFormatter", "DiaryMetadata"]
