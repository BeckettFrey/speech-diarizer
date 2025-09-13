#!/bin/bash
# speech_chunker.sh: Shell wrapper for audio chunking utility
# Usage: ./speech_chunker.sh <input_audio> <config_yaml> <output_dir> [additional_options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check minimum arguments
if [ "$#" -lt 3 ]; then
    echo -e "${BLUE}Audio Chunking Script${NC}"
    echo -e "${BLUE}====================${NC}"
    echo ""
    echo "Usage: $0 <input_audio> <config_yaml> <output_dir> [additional_options]"
    echo ""
    echo "Required Arguments:"
    echo "  input_audio     Input .wav audio file to chunk"
    echo "  config_yaml     YAML configuration file defining chunk boundaries"  
    echo "  output_dir      Output directory for chunk files"
    echo ""
    echo "Optional Arguments:"
    echo "  --fade-in MS    Fade in duration in milliseconds"
    echo "  --fade-out MS   Fade out duration in milliseconds"
    echo "  --padding MS    Silence padding duration in milliseconds"
    echo "  --verbose       Enable verbose output"
    echo ""
    echo "Examples:"
    echo "  $0 audio.wav config.yaml output_chunks/"
    echo "  $0 audio.wav config.yaml output_chunks/ --fade-in 500 --verbose"
    exit 1
fi

# Check if running from the correct directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "src/speech_mine" ]]; then
    print_error "This script must be run from the speech-mine project root directory"
    print_info "Please cd to the directory containing pyproject.toml"
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed or not in PATH"
    print_info "Install uv with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

INPUT_AUDIO="$1"
CONFIG_YAML="$2"
OUTPUT_DIR="$3"
shift 3

# Validate required files
if [[ ! -f "$INPUT_AUDIO" ]]; then
    print_error "Audio file not found: $INPUT_AUDIO"
    exit 1
fi

if [[ ! -f "$CONFIG_YAML" ]]; then
    print_error "Config file not found: $CONFIG_YAML"
    exit 1
fi

print_info "Starting audio chunking..."
echo -e "${BLUE}Parameters:${NC}"
echo -e "  Audio File: ${YELLOW}$INPUT_AUDIO${NC}"
echo -e "  Config File: ${YELLOW}$CONFIG_YAML${NC}"
echo -e "  Output Directory: ${YELLOW}$OUTPUT_DIR${NC}"
echo ""

# Execute the chunking command using uv run
print_info "Executing chunking..."
if uv run python -m speech_mine.pickaxe.cli_chunk "$INPUT_AUDIO" "$CONFIG_YAML" "$OUTPUT_DIR" "$@"; then
    echo ""
    print_success "Audio chunking completed successfully!"
else
    echo ""
    print_error "Audio chunking failed!"
    exit 1
fi
