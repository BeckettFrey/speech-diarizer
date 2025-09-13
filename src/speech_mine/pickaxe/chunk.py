"""
Audio chunking utility for breaking long audio files into smaller segments.

This module provides functionality to split .wav audio files into chunks based on
YAML configuration that defines time boundaries and optional names for each chunk.
"""

import os
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path


class AudioChunker:
    """
    A utility to break long audio files into chunks for processing.
    
    Features:
    - YAML configuration for chunk boundaries
    - Sequential naming based on start time
    - Output directory management
    - Validation of chunk boundaries and start times
    """
    
    def __init__(self, fade_in_duration: int = 0, fade_out_duration: int = 0, 
                 silence_padding: int = 0):
        """
        Initialize AudioChunker with optional audio processing settings.
        
        Args:
            fade_in_duration: Duration of fade in effect in milliseconds (default: 0)
            fade_out_duration: Duration of fade out effect in milliseconds (default: 0)  
            silence_padding: Duration of silence padding in milliseconds (default: 0)
        """
        self.fade_in_duration = fade_in_duration
        self.fade_out_duration = fade_out_duration
        self.silence_padding = silence_padding
    
    def load_config(self, config_path: str) -> List[Dict[str, Any]]:
        """
        Load chunk configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            List of chunk configuration dictionaries
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If configuration structure is invalid
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict) or 'chunks' not in config:
            raise ValueError("YAML must contain a 'chunks' key with list of chunk definitions")
        
        chunks = config['chunks']
        if not isinstance(chunks, list):
            raise ValueError("'chunks' must be a list")
        
        return chunks
    
    def validate_chunks(self, chunks: List[Dict[str, Any]], audio_duration: float) -> None:
        """
        Validate chunk configuration for correctness.
        
        Args:
            chunks: List of chunk configuration dictionaries
            audio_duration: Duration of the audio file in seconds
            
        Raises:
            ValueError: If validation fails
        """
        if not chunks:
            raise ValueError("No chunks defined in configuration")
        
        start_times = []
        
        for i, chunk in enumerate(chunks):
            # Validate required fields
            if 'start' not in chunk or 'end' not in chunk:
                raise ValueError(f"Chunk {i}: 'start' and 'end' times are required")
            
            start = float(chunk['start'])
            end = float(chunk['end'])
            
            # Validate time values
            if start < 0:
                raise ValueError(f"Chunk {i}: start time cannot be negative ({start})")
            
            if end <= start:
                raise ValueError(f"Chunk {i}: end time ({end}) must be greater than start time ({start})")
            
            if end > audio_duration:
                raise ValueError(f"Chunk {i}: end time ({end}) exceeds audio duration ({audio_duration})")
            
            # Check for duplicate start times
            if start in start_times:
                raise ValueError(f"Chunk {i}: duplicate start time ({start}). Start times must be unique.")
            
            start_times.append(start)
            
            # Validate optional name field
            if 'name' in chunk and not isinstance(chunk['name'], str):
                raise ValueError(f"Chunk {i}: 'name' must be a string")
    
    def process_audio_file(self, audio_path: str, config_path: str, output_dir: str) -> List[str]:
        """
        Process audio file and create chunks based on configuration.
        
        Args:
            audio_path: Path to input .wav audio file
            config_path: Path to YAML configuration file
            output_dir: Directory to save chunk files
            
        Returns:
            List of paths to created chunk files
            
        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If audio file is not .wav format or validation fails
        """
        # Import pydub here to defer dependency check
        try:
            from pydub import AudioSegment
        except ImportError:
            raise ImportError("pydub is required for audio processing. Install with: pip install pydub")
        
        # Validate audio file
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        if not audio_path.lower().endswith('.wav'):
            raise ValueError("Only .wav files are supported")
        
        # Load audio file
        audio = AudioSegment.from_wav(audio_path)
        audio_duration = len(audio) / 1000.0  # Convert to seconds
        
        # Load and validate configuration
        chunks = self.load_config(config_path)
        self.validate_chunks(chunks, audio_duration)
        
        # Sort chunks by start time for sequential indexing
        chunks.sort(key=lambda x: float(x['start']))
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Process each chunk
        output_files = []
        for index, chunk in enumerate(chunks):
            start_time = float(chunk['start']) * 1000  # Convert to milliseconds
            end_time = float(chunk['end']) * 1000    # Convert to milliseconds
            
            # Extract chunk
            chunk_audio = audio[start_time:end_time]
            
            # Apply silence padding
            if self.silence_padding > 0:
                silence = AudioSegment.silent(duration=self.silence_padding)
                chunk_audio = silence + chunk_audio + silence
            
            # Apply fade effects
            if self.fade_in_duration > 0:
                chunk_audio = chunk_audio.fade_in(self.fade_in_duration)
            
            if self.fade_out_duration > 0:
                chunk_audio = chunk_audio.fade_out(self.fade_out_duration)
            
            # Generate filename
            if 'name' in chunk:
                filename = f"{index}.{chunk['name']}.wav"
            else:
                filename = f"{index}.wav"
            
            output_path = os.path.join(output_dir, filename)
            
            # Export chunk
            chunk_audio.export(output_path, format="wav")
            output_files.append(output_path)
            
        return output_files


def chunk_audio_file(audio_path: str, config_path: str, output_dir: str,
                     fade_in: int = 0, fade_out: int = 0, silence_padding: int = 0) -> List[str]:
    """
    Convenience function to chunk an audio file with given configuration.
    
    Args:
        audio_path: Path to input .wav audio file
        config_path: Path to YAML configuration file  
        output_dir: Directory to save chunk files
        fade_in: Fade in duration in milliseconds
        fade_out: Fade out duration in milliseconds
        silence_padding: Silence padding duration in milliseconds
        
    Returns:
        List of paths to created chunk files
    """
    chunker = AudioChunker(fade_in_duration=fade_in, 
                          fade_out_duration=fade_out,
                          silence_padding=silence_padding)
    
    return chunker.process_audio_file(audio_path, config_path, output_dir)