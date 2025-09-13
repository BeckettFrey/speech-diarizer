#!/usr/bin/env python3
"""
Command-line interface for audio chunking utility.

This script provides a CLI to chunk audio files based on YAML configuration.
"""

import argparse
import sys
import os
from pathlib import Path

from speech_mine.pickaxe.chunk import chunk_audio_file


def main():
    """Main CLI entry point for audio chunking."""
    parser = argparse.ArgumentParser(
        description="Chunk audio files based on YAML configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic chunking
  %(prog)s audio.wav config.yaml output_dir/

  # With fade effects and padding
  %(prog)s audio.wav config.yaml output_dir/ --fade-in 500 --fade-out 500 --padding 100

YAML Configuration Format:
  chunks:
    - start: 0.0
      end: 30.0
      name: "intro"       # optional
    - start: 30.0
      end: 120.0
      name: "main_discussion"
        """
    )
    
    # Required arguments
    parser.add_argument('audio_file', 
                       help='Input .wav audio file to chunk')
    parser.add_argument('config_file', 
                       help='YAML configuration file defining chunk boundaries')
    parser.add_argument('output_dir', 
                       help='Output directory for chunk files (created if needed)')
    
    # Optional arguments for audio processing
    parser.add_argument('--fade-in', type=int, default=0, metavar='MS',
                       help='Fade in duration in milliseconds (default: 0)')
    parser.add_argument('--fade-out', type=int, default=0, metavar='MS',
                       help='Fade out duration in milliseconds (default: 0)')
    parser.add_argument('--padding', type=int, default=0, metavar='MS',
                       help='Silence padding duration in milliseconds (default: 0)')
    
    # Utility arguments
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.exists(args.config_file):
        print(f"Error: Config file not found: {args.config_file}", file=sys.stderr)
        sys.exit(1)
    
    if not args.audio_file.lower().endswith('.wav'):
        print(f"Error: Only .wav files are supported, got: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # Validate numeric arguments
    if args.fade_in < 0:
        print(f"Error: Fade in duration cannot be negative: {args.fade_in}", file=sys.stderr)
        sys.exit(1)
    
    if args.fade_out < 0:
        print(f"Error: Fade out duration cannot be negative: {args.fade_out}", file=sys.stderr)
        sys.exit(1)
    
    if args.padding < 0:
        print(f"Error: Padding duration cannot be negative: {args.padding}", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"Audio file: {args.audio_file}")
        print(f"Config file: {args.config_file}")
        print(f"Output directory: {args.output_dir}")
        print(f"Fade in: {args.fade_in}ms")
        print(f"Fade out: {args.fade_out}ms")
        print(f"Padding: {args.padding}ms")
        print()
    
    try:
        # Process the audio file
        output_files = chunk_audio_file(
            audio_path=args.audio_file,
            config_path=args.config_file,
            output_dir=args.output_dir,
            fade_in=args.fade_in,
            fade_out=args.fade_out,
            silence_padding=args.padding
        )
        
        # Report results
        print(f"Successfully created {len(output_files)} chunk(s):")
        for file_path in output_files:
            file_name = os.path.basename(file_path)
            if args.verbose:
                file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
                print(f"  {file_name} ({file_size:.2f} MB)")
            else:
                print(f"  {file_name}")
        
        print(f"\nOutput saved to: {args.output_dir}")
        
    except ImportError as e:
        print(f"Error: Missing dependency - {e}", file=sys.stderr)
        print("Please install required dependencies: pip install pydub PyYAML", file=sys.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()