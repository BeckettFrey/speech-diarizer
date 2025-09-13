#!/bin/bash

# speech_search.sh - Script wrapper for speech mining CLI
# Usage: ./scripts/speech_search.sh [arguments]
# 
# This script provides a convenient wrapper around the speech-mine CLI
# for searching transcripts using fuzzy matching.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default values
DEFAULT_SIMILARITY_MIN=0.5
DEFAULT_SIMILARITY_MAX=1.0
DEFAULT_TOP_K=10
DEFAULT_OUTPUT_TYPE="utterance"

# Function to print colored output
print_info() {
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

# Function to show usage
show_usage() {
    cat << EOF
${BLUE}Speech Mining Search Script${NC}
${BLUE}===========================${NC}

Usage: $0 <query> <csv_file> [options]

Required Arguments:
  query                Search query string (word, phrase, or sentence)
  csv_file            Path to CSV file containing transcript data

Optional Arguments:
  --json <file>       Path to JSON metadata file
  --similarity-min    Minimum similarity threshold (0.0-1.0, default: ${DEFAULT_SIMILARITY_MIN})
  --similarity-max    Maximum similarity threshold (0.0-1.0, default: ${DEFAULT_SIMILARITY_MAX})
  --top-k             Maximum number of results (default: ${DEFAULT_TOP_K})
  --output-type       Output format: 'utterance' or 'timestamp' (default: ${DEFAULT_OUTPUT_TYPE})
  --save-path         Path to save JSON output file (optional)
  --pretty            Display results in human-readable format
  --help              Show this help message

Examples:
  # Basic search
  $0 "hello world" transcript.csv

  # Advanced search with custom parameters
  $0 "meeting discussion" data.csv --json metadata.json --similarity-min 0.7 --top-k 5

  # Search with pretty output
  $0 "presentation" data.csv --pretty

  # Search with timestamp output and save results
  $0 "presentation" data.csv --output-type timestamp --save-path results.json

  # Search with similarity range
  $0 "west end" transcript.csv --similarity-min 0.6 --similarity-max 0.9

EOF
}

# Function to format and display pretty results
display_pretty_results() {
    local json_output="$1"
    
    if [[ ! -f "$json_output" ]]; then
        print_error "Could not find results file for pretty display"
        return 1
    fi
    
    echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                           SEARCH RESULTS                           ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}\n"
    
    # Use Python to parse and format the JSON results
    python3 << EOF
import json
import sys

def format_time(seconds):
    """Format seconds as MM:SS.sss"""
    if not isinstance(seconds, (int, float)):
        return str(seconds)
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes:02d}:{secs:06.3f}"

try:
    with open('$json_output', 'r') as f:
        data = json.load(f)
    
    results = data.get('results', [])
    search_params = data.get('search_parameters', {})
    output_type = search_params.get('output_type', 'utterance')
    
    if not results:
        print("\033[1;33m[NO RESULTS]\033[0m No matches found for the query.")
        sys.exit(0)
    
    for i, result in enumerate(results, 1):
        # Header for each result
        print(f"\033[1;36m{'─' * 67}\033[0m")
        print(f"\033[1;36mResult #{i:2d}\033[0m")
        print(f"\033[1;36m{'─' * 67}\033[0m")
        
        # Similarity score
        similarity = result.get('similarity_score', 'N/A')
        if isinstance(similarity, (int, float)):
            similarity_color = '\033[1;32m' if similarity >= 0.8 else '\033[1;33m' if similarity >= 0.6 else '\033[1;31m'
            print(f"  \033[1;37mSimilarity:\033[0m {similarity_color}{similarity:.3f}\033[0m")
        else:
            print(f"  \033[1;37mSimilarity:\033[0m {similarity}")
        
        # Matched text
        matched_text = result.get('matched_text', result.get('text', 'N/A'))
        print(f"  \033[1;37mMatched Text:\033[0m \033[0;37m\"{matched_text}\"\033[0m")
        
        # Time information
        if output_type == 'timestamp':
            time_window = result.get('time_window', {})
            if time_window:
                start_time = time_window.get('start_time')
                end_time = time_window.get('end_time')
                duration = time_window.get('duration')
                if start_time is not None and end_time is not None:
                    print(f"  \033[1;37mTime Window:\033[0m \033[0;35m{format_time(start_time)}\033[0m → \033[0;35m{format_time(end_time)}\033[0m (\033[0;33m{duration:.3f}s\033[0m)")
        else:  # utterance format
            time_span = result.get('time_span', {})
            if time_span:
                start_time = time_span.get('start')
                end_time = time_span.get('end')
                duration = time_span.get('duration')
                if start_time is not None and end_time is not None:
                    print(f"  \033[1;37mTime Span:\033[0m \033[0;35m{format_time(start_time)}\033[0m → \033[0;35m{format_time(end_time)}\033[0m (\033[0;33m{duration:.3f}s\033[0m)")
        
        # Speaker and context information
        context = result.get('context', {})
        if context:
            speaker = context.get('speaker')
            if speaker:
                print(f"  \033[1;37mSpeaker:\033[0m \033[0;36m{speaker}\033[0m")
            
            full_text = context.get('full_segment_text')
            if full_text and full_text != matched_text:
                # Truncate long context text
                if len(full_text) > 80:
                    full_text = full_text[:77] + "..."
                print(f"  \033[1;37mContext:\033[0m \033[0;90m\"{full_text}\"\033[0m")
        
        # Utterance number for utterance format
        if output_type == 'utterance':
            utterance_num = result.get('utterance_number')
            if utterance_num is not None:
                print(f"  \033[1;37mUtterance #:\033[0m \033[0;33m{utterance_num}\033[0m")
        
        print()  # Empty line between results
    
    # Summary
    total_results = len(results)
    print(f"\033[1;36m{'═' * 67}\033[0m")
    print(f"\033[1;36mSUMMARY:\033[0m Found \033[1;32m{total_results}\033[0m result{'s' if total_results != 1 else ''}")
    print(f"\033[1;36m{'═' * 67}\033[0m")

except Exception as e:
    print(f"\033[1;31m[ERROR]\033[0m Failed to parse results: {e}")
    sys.exit(1)
EOF
}

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

# Parse command line arguments
if [[ $# -lt 2 ]] || [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    show_usage
    exit 0
fi

# Required arguments
QUERY="$1"
CSV_FILE="$2"
shift 2

# Optional arguments with defaults
JSON_FILE=""
SIMILARITY_MIN="$DEFAULT_SIMILARITY_MIN"
SIMILARITY_MAX="$DEFAULT_SIMILARITY_MAX"
TOP_K="$DEFAULT_TOP_K"
OUTPUT_TYPE="$DEFAULT_OUTPUT_TYPE"
SAVE_PATH=""
PRETTY_OUTPUT=false

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_FILE="$2"
            shift 2
            ;;
        --similarity-min)
            SIMILARITY_MIN="$2"
            shift 2
            ;;
        --similarity-max)
            SIMILARITY_MAX="$2"
            shift 2
            ;;
        --top-k)
            TOP_K="$2"
            shift 2
            ;;
        --output-type)
            OUTPUT_TYPE="$2"
            shift 2
            ;;
        --save-path)
            SAVE_PATH="$2"
            shift 2
            ;;
        --pretty)
            PRETTY_OUTPUT=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required files
if [[ ! -f "$CSV_FILE" ]]; then
    print_error "CSV file not found: $CSV_FILE"
    exit 1
fi

if [[ -n "$JSON_FILE" ]] && [[ ! -f "$JSON_FILE" ]]; then
    print_error "JSON file not found: $JSON_FILE"
    exit 1
fi

# Validate similarity range
if ! python3 -c "
import sys
try:
    min_sim, max_sim = float('$SIMILARITY_MIN'), float('$SIMILARITY_MAX')
    if not (0.0 <= min_sim <= max_sim <= 1.0):
        sys.exit(1)
except ValueError:
    sys.exit(1)
" 2>/dev/null; then
    print_error "Invalid similarity range. Both values must be between 0.0 and 1.0, with min <= max"
    exit 1
fi

# Validate output type
if [[ "$OUTPUT_TYPE" != "utterance" ]] && [[ "$OUTPUT_TYPE" != "timestamp" ]]; then
    print_error "Invalid output type: $OUTPUT_TYPE. Must be 'utterance' or 'timestamp'"
    exit 1
fi

# Validate top-k
if ! [[ "$TOP_K" =~ ^[0-9]+$ ]] || [[ "$TOP_K" -lt 1 ]]; then
    print_error "Invalid top-k value: $TOP_K. Must be a positive integer"
    exit 1
fi

# If pretty output is requested and no save path is specified, create a temp file
TEMP_FILE=""
if [[ "$PRETTY_OUTPUT" == true ]] && [[ -z "$SAVE_PATH" ]]; then
    TEMP_FILE=$(mktemp)
    SAVE_PATH="$TEMP_FILE"
fi

# Build command arguments
CMD_ARGS=(
    "search"
    "$QUERY"
    "$CSV_FILE"
)

if [[ -n "$JSON_FILE" ]]; then
    CMD_ARGS+=("$JSON_FILE")
fi

CMD_ARGS+=(
    "--similarity-range" "$SIMILARITY_MIN" "$SIMILARITY_MAX"
    "--top-k" "$TOP_K"
    "--output-type" "$OUTPUT_TYPE"
)

if [[ -n "$SAVE_PATH" ]]; then
    CMD_ARGS+=("--save-path" "$SAVE_PATH")
fi

# Print search parameters
print_info "Starting speech mining search..."
echo -e "${BLUE}Search Parameters:${NC}"
echo -e "  Query: ${YELLOW}'$QUERY'${NC}"
echo -e "  CSV File: ${YELLOW}$CSV_FILE${NC}"
if [[ -n "$JSON_FILE" ]]; then
    echo -e "  JSON File: ${YELLOW}$JSON_FILE${NC}"
fi
echo -e "  Similarity Range: ${YELLOW}$SIMILARITY_MIN - $SIMILARITY_MAX${NC}"
echo -e "  Top K Results: ${YELLOW}$TOP_K${NC}"
echo -e "  Output Type: ${YELLOW}$OUTPUT_TYPE${NC}"
if [[ -n "$SAVE_PATH" ]] && [[ -z "$TEMP_FILE" ]]; then
    echo -e "  Save Path: ${YELLOW}$SAVE_PATH${NC}"
fi
if [[ "$PRETTY_OUTPUT" == true ]]; then
    echo -e "  Pretty Output: ${YELLOW}Enabled${NC}"
fi
echo ""

# Execute the search command
print_info "Executing search..."
if uv run python -m speech_mine.cli "${CMD_ARGS[@]}"; then
    echo ""
    print_success "Search completed successfully!"
    
    # Display pretty results if requested
    if [[ "$PRETTY_OUTPUT" == true ]] && [[ -n "$SAVE_PATH" ]]; then
        display_pretty_results "$SAVE_PATH"
    elif [[ -n "$SAVE_PATH" ]] && [[ -z "$TEMP_FILE" ]]; then
        if [[ -f "$SAVE_PATH" ]]; then
            file_size=$(du -h "$SAVE_PATH" | cut -f1)
            print_info "Results saved to: $SAVE_PATH (${file_size})"
        fi
    fi
    
    # Clean up temp file
    if [[ -n "$TEMP_FILE" ]] && [[ -f "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi
else
    echo ""
    print_error "Search failed!"
    
    # Clean up temp file on failure
    if [[ -n "$TEMP_FILE" ]] && [[ -f "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
    fi
    
    exit 1
fi