# Audio Chunking Utility

The audio chunking utility allows you to split long .wav audio files into smaller chunks based on YAML configuration.

## Features

- **YAML Configuration**: Define chunk boundaries and optional names in a simple YAML format
- **Sequential Naming**: Chunks are named with sequential indices based on start time
- **Audio Effects**: Optional fade in/out and silence padding
- **Validation**: Comprehensive validation of chunk boundaries and configuration
- **CLI Interface**: Easy-to-use command-line interface

## Usage

### CLI Interface

```bash
# Basic usage
chunk-audio audio.wav config.yaml output_dir/

# With audio effects
chunk-audio audio.wav config.yaml output_dir/ --fade-in 500 --fade-out 500 --padding 100
```

### Python API

```python
from speech_mine.pickaxe.chunk import chunk_audio_file

# Basic usage
output_files = chunk_audio_file("audio.wav", "config.yaml", "output_dir/")

# With audio effects
output_files = chunk_audio_file(
    "audio.wav", "config.yaml", "output_dir/",
    fade_in=500, fade_out=500, silence_padding=100
)
```

## Configuration Format

Create a YAML file defining your chunks:

```yaml
chunks:
  # Chunk with name
  - start: 0.0
    end: 30.0
    name: "intro"
  
  # Chunk without name
  - start: 30.0
    end: 120.0
  
  # Another named chunk
  - start: 120.0
    end: 180.0
    name: "conclusion"
```

### Output Files

Files are named based on their start time order:
- `0.intro.wav` (start: 0.0s)
- `1.wav` (start: 30.0s, no name)
- `2.conclusion.wav` (start: 120.0s)

## Validation Rules

The utility validates your configuration:

1. **Unique Start Times**: No two chunks can have the same start time
2. **Valid Time Ranges**: End time must be greater than start time
3. **Duration Bounds**: Chunks cannot exceed the audio file duration
4. **Non-negative Times**: Start times cannot be negative
5. **Required Fields**: Each chunk must have `start` and `end` fields

## Dependencies

- `pydub`: Audio processing
- `PyYAML`: YAML configuration parsing

Install with: `pip install pydub PyYAML`

## Example

See `example_chunk_config.yaml` for a complete configuration example.