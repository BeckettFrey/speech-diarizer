#!/bin/bash

# batch_format.sh - Batch format CSV transcripts to pretty text files
# Usage: ./scripts/batch_format.sh [input_directory] [output_directory]
# If no arguments provided, processes current directory

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default directories
INPUT_DIR="${1:-.}"
OUTPUT_DIR="${2:-${INPUT_DIR}}"

echo -e "${BLUE}🚀 Speech Diarizer Batch Formatter${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "Input directory:  ${YELLOW}${INPUT_DIR}${NC}"
echo -e "Output directory: ${YELLOW}${OUTPUT_DIR}${NC}"
echo ""

# Check if input directory exists
if [[ ! -d "$INPUT_DIR" ]]; then
    echo -e "${RED}❌ Error: Input directory '$INPUT_DIR' does not exist${NC}"
    exit 1
fi

# Create output directory if it doesn't exist
if [[ ! -d "$OUTPUT_DIR" ]]; then
    echo -e "${YELLOW}📁 Creating output directory: $OUTPUT_DIR${NC}"
    mkdir -p "$OUTPUT_DIR"
fi

# Find all CSV files (excluding metadata files)
csv_files=($(find "$INPUT_DIR" -maxdepth 1 -name "*.csv" ! -name "*_metadata.csv" | sort))

if [[ ${#csv_files[@]} -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  No CSV files found in '$INPUT_DIR'${NC}"
    echo -e "${BLUE}💡 Make sure you have CSV files from speech-mine extract command${NC}"
    exit 0
fi

echo -e "${GREEN}📊 Found ${#csv_files[@]} CSV file(s) to process:${NC}"
for file in "${csv_files[@]}"; do
    basename_file=$(basename "$file")
    echo -e "  • ${basename_file}"
done
echo ""

# Process each CSV file
success_count=0
error_count=0

for csv_file in "${csv_files[@]}"; do
    basename_csv=$(basename "$csv_file" .csv)
    output_file="$OUTPUT_DIR/${basename_csv}_pretty.txt"
    
    echo -e "${BLUE}📝 Processing: ${basename_csv}.csv${NC}"
    
    # Run the format command
    if uv run speech-mine format "$csv_file" "$output_file"; then
        echo -e "${GREEN}✅ Success: ${basename_csv}_pretty.txt${NC}"
        ((success_count++))
    else
        echo -e "${RED}❌ Failed: ${basename_csv}.csv${NC}"
        ((error_count++))
    fi
    echo ""
done

# Summary
echo -e "${BLUE}📈 Batch Processing Complete${NC}"
echo -e "${BLUE}===========================${NC}"
echo -e "${GREEN}✅ Successful: $success_count${NC}"
if [[ $error_count -gt 0 ]]; then
    echo -e "${RED}❌ Failed: $error_count${NC}"
fi
echo -e "${BLUE}📁 Output location: ${OUTPUT_DIR}${NC}"

# List generated files
if [[ $success_count -gt 0 ]]; then
    echo ""
    echo -e "${GREEN}📄 Generated files:${NC}"
    find "$OUTPUT_DIR" -name "*_pretty.txt" -newer "$0" 2>/dev/null | sort | while read file; do
        basename_file=$(basename "$file")
        file_size=$(du -h "$file" | cut -f1)
        echo -e "  • ${basename_file} (${file_size})"
    done
fi

if [[ $error_count -eq 0 ]]; then
    echo -e "${GREEN}🎉 All files processed successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some files had errors. Check the output above.${NC}"
    exit 1
fi
