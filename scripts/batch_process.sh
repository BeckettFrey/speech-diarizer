#!/bin/bash

# Batch transcription script for speech-diarizer
# Usage: ./batch_process.sh [input_directory] [output_directory]

# Configurable parameters
HF_TOKEN=
MODEL="small"
NUM_SPEAKERS=4
COMPUTE_TYPE="float32"

# Default directories
INPUT_DIR="${1:-$HOME/Desktop/2309_M_BF Raw Audio}"
OUTPUT_DIR="${2:-./output}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    print_error "Input directory does not exist: $INPUT_DIR"
    echo "Usage: $0 [input_directory] [output_directory]"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Count total audio files
total_files=$(find "$INPUT_DIR" -type f \( -iname "*.wav" -o -iname "*.mp3" -o -iname "*.m4a" -o -iname "*.flac" -o -iname "*.aac" \) | wc -l)

if [ "$total_files" -eq 0 ]; then
    print_warning "No audio files found in: $INPUT_DIR"
    print_status "Looking for files with extensions: .wav, .mp3, .m4a, .flac, .aac"
    exit 1
fi

print_status "Found $total_files audio files to process"
print_status "Input directory: $INPUT_DIR"
print_status "Output directory: $OUTPUT_DIR"
print_status "Model: $MODEL, Speakers: $NUM_SPEAKERS, Compute type: $COMPUTE_TYPE"
echo ""

# Counter for processed files
processed=0
failed=0

# Process each audio file
find "$INPUT_DIR" -type f \( -iname "*.wav" -o -iname "*.mp3" -o -iname "*.m4a" -o -iname "*.flac" -o -iname "*.aac" \) | while read -r audio_file; do
    # Get filename without path and extension
    filename=$(basename "$audio_file")
    filename_no_ext="${filename%.*}"
    
    # Create output filename with _pretty suffix
    output_file="$OUTPUT_DIR/${filename_no_ext}_pretty.csv"
    
    # Skip if output already exists
    if [ -f "$output_file" ]; then
        print_warning "Output already exists, skipping: $output_file"
        continue
    fi
    
    processed=$((processed + 1))
    print_status "Processing ($processed/$total_files): $filename"
    
    # Run the transcription command
    if uv run speech-diarizer extract "$audio_file" "$output_file" \
        --model "$MODEL" \
        --num-speakers "$NUM_SPEAKERS" \
        --hf-token "$HF_TOKEN" \
        --compute-type "$COMPUTE_TYPE"; then
        
        print_success "Completed: $output_file"
    else
        failed=$((failed + 1))
        print_error "Failed to process: $filename"
    fi
    
    echo ""
done

# Final summary
echo "=================================================="
print_status "Batch processing completed!"
print_success "Successfully processed: $((processed - failed)) files"
if [ "$failed" -gt 0 ]; then
    print_error "Failed: $failed files"
fi
print_status "Output files saved to: $OUTPUT_DIR"