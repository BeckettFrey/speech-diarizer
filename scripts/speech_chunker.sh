#!/bin/bash
# speech_chunker.sh: Shell wrapper for src/speech_mine/pickaxe/cli_chunk.py
# Usage: ./speech_chunker.sh <input_audio> <config_yaml> <output_dir>

set -e

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_audio> <config_yaml> <output_dir>"
    exit 1
fi

INPUT_AUDIO="$1"
CONFIG_YAML="$2"
OUTPUT_DIR="$3"

python3 src/speech_mine/pickaxe/cli_chunk.py "$INPUT_AUDIO" "$CONFIG_YAML" "$OUTPUT_DIR"
