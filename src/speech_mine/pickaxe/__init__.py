"""
Pickaxe module - Audio processing utilities for speech-mine.

This module contains utilities for audio file manipulation and processing,
including chunking long audio files into smaller segments.
"""

from .chunk import AudioChunker, chunk_audio_file

__all__ = ['AudioChunker', 'chunk_audio_file']