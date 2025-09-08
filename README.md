# Speech Diarizer

A Python tool for extracting transcripts from audio files with speaker diarization and word-level timestamps. Combines faster-whisper for transcription with pyannote speaker diarization to create detailed, timestamped transcripts with secondary movie-style formatting.

## Requirements

- Python 3.11+
- HuggingFace access token (for pyannote models)
- GPU recommended for faster processing
- Audio files in .wav format

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone <repository-url>
cd speech-diarizer

# Install dependencies and create virtual environment
uv sync
```

## Usage Examples

### Primary CLI Commands (Recommended)

#### Basic Usage
```bash
# Show all available commands
uv run speech-diarizer --help

# Extract transcript from audio file
uv run speech-diarizer extract meeting.wav output.csv --hf-token YOUR_HUGGINGFACE_TOKEN

# Format CSV to readable movie-style script
uv run speech-diarizer format output.csv formatted_script.txt
```

#### Alternative Entry Points
```bash
# Direct audio extraction
uv run extract-audio meeting.wav output.csv --hf-token YOUR_TOKEN

# Direct script formatting  
uv run format-script output.csv script.txt
```

### Complete Workflow Examples

#### Meeting Transcription
```bash
# 1. Extract with known speaker count (best accuracy)
uv run speech-diarizer extract meeting.wav transcript.csv \
  --hf-token YOUR_TOKEN \
  --num-speakers 4 \
  --model large-v3 \
  --compute-type float32

# 2. Format to readable script
uv run speech-diarizer format transcript.csv meeting_script.txt

# 3. Create custom speaker names template
uv run speech-diarizer format transcript.csv script.txt --create-template

# 4. Format with custom speaker names
uv run speech-diarizer format transcript.csv final_script.txt \
  --speakers transcript_speaker_names.json
```

#### Interview Processing (2 speakers)
```bash
# Perfect for interviews
uv run speech-diarizer extract interview.wav interview.csv \
  --hf-token YOUR_TOKEN \
  --num-speakers 2 \
  --model medium \
  --compute-type float32

uv run speech-diarizer format interview.csv interview_script.txt
```

#### CPU-Only Processing
```bash
# For systems without GPU
uv run speech-diarizer extract audio.wav output.csv \
  --hf-token YOUR_TOKEN \
  --model base \
  --device cpu \
  --compute-type float32 \
  --num-speakers 2
```

### Advanced Usage

```bash
# Use specific Whisper model and GPU with known number of speakers
uv run speech-diarizer extract interview.wav results.csv \
  --hf-token YOUR_TOKEN \
  --model large-v3 \
  --device cuda \
  --num-speakers 2 \
  --compute-type float16 \
  --verbose

# Use smaller model for faster CPU processing
uv run speech-diarizer extract podcast.wav transcript.csv \
  --hf-token YOUR_TOKEN \
  --model base \
  --device cpu \
  --compute-type float32 \
  --min-speakers 2 \
  --max-speakers 4

# Meeting with exact number of known speakers (best accuracy)
uv run speech-diarizer extract meeting.wav transcript.csv \
  --hf-token YOUR_TOKEN \
  --num-speakers 5 \
  --model medium \
  --compute-type float32

# Format with custom speaker names
echo '{"SPEAKER_00":"Alice","SPEAKER_01":"Bob"}' > speakers.json
uv run speech-diarizer format transcript.csv script.txt --speakers speakers.json
```

### Batch Processing
```bash
# Process multiple files
for audio_file in *.wav; do
  base_name="${audio_file%.wav}"
  echo "Processing $audio_file..."
  
  # Extract transcript
  uv run speech-diarizer extract "$audio_file" "${base_name}.csv" \
    --hf-token YOUR_TOKEN \
    --model medium \
    --compute-type float32 \
    --num-speakers 2
  
  # Format script
  uv run speech-diarizer format "${base_name}.csv" "${base_name}_script.txt"
done
```

### Model Options

Available Whisper models (smaller = faster, larger = more accurate):
- `tiny`: Fastest, least accurate
- `base`: Good balance for quick processing  
- `small`: Better accuracy, moderate speed
- `medium`: Good accuracy and speed
- `large-v3`: Best accuracy (default)
- `turbo`: Fast and accurate

### Device and Compute Type Options

**Device Options:**
- `auto`: Automatically detect best device (default)
- `cuda`: Force GPU usage (requires NVIDIA GPU)
- `cpu`: Force CPU usage

**Compute Type Options:**
- `float32`: CPU-compatible, slower but works everywhere (recommended for CPU)
- `float16`: GPU-optimized, faster (recommended for CUDA)
- `int8`: Fastest, slightly lower accuracy

**⚠️ Important:** Use `--compute-type float32` when running on CPU to avoid errors!

## Speaker Optimization

### Improving Accuracy with Known Speaker Counts

**Best accuracy - exact number of speakers:**
```bash
uv run speech-diarizer extract meeting.wav output.csv \
  --hf-token $HF_TOKEN \
  --num-speakers 3 \
  --compute-type float32
```

**Range-based speaker detection:**
```bash
uv run speech-diarizer extract conference.wav output.csv \
  --hf-token $HF_TOKEN \
  --min-speakers 2 \
  --max-speakers 8 \
  --compute-type float32
```

### Speaker Parameter Guidelines

| Parameter | Description | When to Use |
|-----------|-------------|-------------|
| `--num_speakers N` | Exact number of speakers | When you know exactly how many speakers (best accuracy) |
| `--min_speakers N` | Minimum speakers (default: 1) | Set to 2+ if you know multiple people speak |
| `--max_speakers N` | Maximum speakers | Limit false speaker detection in noisy audio |

**💡 Pro tip**: Specifying `--num_speakers` when you know the exact count can improve accuracy by 15-30%!

## Output Format

The tool generates multiple output files:

### CSV File (`output.csv`)
Contains both segment-level and word-level data:

| Column | Description |
|--------|-------------|
| `type` | "segment" or "word" |
| `speaker` | Speaker identifier (SPEAKER_00, SPEAKER_01, etc.) |
| `start` | Start timestamp in seconds |
| `end` | End timestamp in seconds |
| `text` | Full segment text |
| `word` | Individual word (for word-type rows) |
| `word_position` | Position of word in segment |
| `confidence` | Confidence score (0-1) |
| `overlap_duration` | Speaker overlap duration |

### Formatted Script File (`script.txt`)
Human-readable movie-style script format:
```
================================================================================
                                   TRANSCRIPT
================================================================================

RECORDING DETAILS:
----------------------------------------
File: meeting.wav
Duration: 30:45
Language: ENGLISH (confidence: 95.2%)
Speakers: 3
Processed: 2025-09-08 16:35:00

CAST:
----------------------------------------
SPEAKER A
SPEAKER B  
SPEAKER C

TRANSCRIPT:
----------------------------------------

[00:00 - 00:05] SPEAKER A:
    Good morning everyone, let's start the meeting.

[00:06 - 00:12] SPEAKER B:
    Thanks for organizing this. I have the quarterly
    report ready to share.

    [...3 second pause...]

[00:15 - 00:22] SPEAKER C:
    Perfect, I'd like to hear about the sales numbers
    first.
```

### Metadata File (`output_metadata.json`)
Contains processing information:

```json
{
  "audio_file": "meeting.wav",
  "language": "en",
  "language_probability": 0.95,
  "duration": 1800.0,
  "total_segments": 234,
  "total_words": 3456,
  "speakers": ["SPEAKER_00", "SPEAKER_01", "SPEAKER_02"],
  "processing_timestamp": "2025-09-08 14:30:00"
}
```

## Setup Requirements

### HuggingFace Token
1. Create account at [HuggingFace](https://huggingface.co)
2. Go to Settings → Access Tokens
3. Create a new token with read permissions
4. Accept the user agreement at [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)

### Audio File Requirements
- Format: .wav files only
- Quality: 16kHz+ sample rate recommended
- Duration: No specific limits (longer files take more time)
- Channels: Mono or stereo supported

### Performance vs. Accuracy Trade-offs

| Model | Speed | Accuracy | Best For |
|-------|-------|----------|----------|
| `tiny` | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick tests, drafts |
| `base` | ⚡⚡⚡⚡ | ⭐⭐⭐ | Fast processing, good quality |
| `small` | ⚡⚡⚡ | ⭐⭐⭐⭐ | Balanced speed/accuracy |
| `medium` | ⚡⚡ | ⭐⭐⭐⭐ | Good quality, reasonable speed |
| `large-v3` | ⚡ | ⭐⭐⭐⭐⭐ | Best quality, slow |

## Troubleshooting

### Quick Fixes

```bash
# ❌ This fails on CPU:
uv run speech-diarizer extract audio.wav out.csv --hf-token TOKEN

# ✅ This works on CPU:
uv run speech-diarizer extract audio.wav out.csv --hf-token TOKEN --compute-type float32

# ✅ This works on any system:
uv run speech-diarizer extract audio.wav out.csv --hf-token TOKEN --device cpu --compute-type float32 --model base
```

## Quick Start Examples

| Use Case | Command | Notes |
|----------|---------|-------|
| **Basic extraction (CPU)** | `uv run speech-diarizer extract audio.wav out.csv --hf-token TOKEN --compute-type float32` | Safe for all systems |
| **2-person interview** | `uv run speech-diarizer extract interview.wav out.csv --hf-token TOKEN --num-speakers 2 --compute-type float32` | Exact count for best accuracy |
| **Meeting (known attendees)** | `uv run speech-diarizer extract meeting.wav out.csv --hf-token TOKEN --num-speakers 5 --compute-type float32` | Count participants beforehand |
| **Fast processing** | `uv run speech-diarizer extract audio.wav out.csv --hf-token TOKEN --model base --compute-type float32` | Trade accuracy for speed |
| **Format transcript** | `uv run speech-diarizer format transcript.csv script.txt` | Create readable script |
| **GPU processing** | `uv run speech-diarizer extract audio.wav out.csv --hf-token TOKEN --device cuda --compute-type float16` | Faster with GPU |

### Environment Setup
```bash
# Set token once (optional)
export HF_TOKEN="your_huggingface_token"

# Then you can omit --hf-token:
uv run speech-diarizer extract audio.wav out.csv --compute-type float32
```

## License

TBD