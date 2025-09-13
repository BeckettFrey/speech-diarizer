"""
Command-line interface for script formatting.

This module provides the CLI for the script formatting tool.
"""

import argparse
import os
import sys

from .formatter import ScriptFormatter


def create_format_parser() -> argparse.ArgumentParser:
    """Create argument parser for format command."""
    parser = argparse.ArgumentParser(
        description="Format transcript CSV into a movie-style script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  format output.csv transcript.txt
  format output.csv script.txt --speakers custom_names.json
  format output.csv script.txt --create-template
        """
    )
    
    parser.add_argument(
        "input_csv",
        help="Input CSV file from extract command"
    )
    parser.add_argument(
        "output_txt",
        help="Output text file for formatted script"
    )
    parser.add_argument(
        "--speakers",
        help="JSON file with custom speaker names (SPEAKER_00: 'John Doe', etc.)"
    )
    parser.add_argument(
        "--create-template",
        action="store_true",
        help="Create a template JSON file for custom speaker names"
    )
    
    return parser


def format_command(args: argparse.Namespace) -> int:
    """
    Execute the format command.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Validate input file
    if not os.path.exists(args.input_csv):
        print(f"❌ Error: Input file '{args.input_csv}' not found.")
        return 1
    
    # Create speaker template if requested
    if args.create_template:
        template_file = ScriptFormatter.create_custom_speakers_template(args.input_csv)
        if template_file:
            print(f"📋 Created speaker template: {template_file}")
            print("Edit this file to customize speaker names, then use --speakers option.")
            return 0
        else:
            print("❌ Failed to create speaker template.")
            return 1
    
    # Load custom speakers if provided
    custom_speakers = None
    if args.speakers:
        custom_speakers = ScriptFormatter.load_custom_speakers(args.speakers)
        if custom_speakers:
            print(f"📋 Loaded custom speaker names from: {args.speakers}")
        else:
            print(f"⚠️  Warning: Could not load speaker names from: {args.speakers}")
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output_txt)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Format the script
        formatter = ScriptFormatter(custom_speakers)
        formatter.format_script(args.input_csv, args.output_txt)
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main() -> int:
    """Main entry point for the format CLI."""
    parser = create_format_parser()
    args = parser.parse_args()
    return format_command(args)


if __name__ == "__main__":
    sys.exit(main())
