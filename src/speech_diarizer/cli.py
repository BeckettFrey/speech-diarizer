"""
Main CLI entry point for speech-diarizer.

This module provides a unified CLI with multiple subcommands.
"""

import argparse
import sys
from typing import List

from .cli_extract import extract_command, create_extract_parser
from .cli_format import format_command, create_format_parser


def create_main_parser() -> argparse.ArgumentParser:
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="speech-diarizer",
        description="Speech-to-Text with Speaker Diarization and Script Formatting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  speech-diarizer extract meeting.wav output.csv --hf-token YOUR_TOKEN
  speech-diarizer format output.csv formatted_script.txt
  speech-diarizer format output.csv script.txt --speakers custom_names.json
        """
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="{extract,format}"
    )
    
    # Extract subcommand
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract transcript from audio with speaker diarization",
        parents=[create_extract_parser()],
        add_help=False
    )
    extract_parser.set_defaults(func=extract_command)
    
    # Format subcommand  
    format_parser = subparsers.add_parser(
        "format", 
        help="Format CSV transcript into movie-style script",
        parents=[create_format_parser()],
        add_help=False
    )
    format_parser.set_defaults(func=format_command)
    
    return parser


def main(args: List[str] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_main_parser()
    
    if args is None:
        args = sys.argv[1:]
    
    if not args:
        parser.print_help()
        return 1
    
    parsed_args = parser.parse_args(args)
    
    if not hasattr(parsed_args, 'func'):
        parser.print_help()
        return 1
    
    return parsed_args.func(parsed_args)


if __name__ == "__main__":
    sys.exit(main())
