# TODO This file will house a utility to break long audio files into chunks for processing, using this modfle one can save all the chunks for an intiial .wav file to directory, the configuration will be given as a yaml that defines all the boundaries, and optionally a name for each chunk, if a name is given then it names the chunk wav file {index}.{name}.wav otherwise it will just name it {index}.wav the index is in reference to its start time, sooner start time for that chunk leavws it earlier in the sequence, start times cannot be the same for multiple chunks

# Ex.

# chunks:
#   - start: 0.0
#     end: 30.0
#     name: "intro"  # optional
#   - start: 30.0 
#     end: 120.0
#     name: "main_discussion"

# Audio Processing:
# use pydub
# Audio format support: just wav files

# File Organization:
# Index calculation: You mentioned index is based on start time - should it be:

# Sequential integers (0, 1, 2, ...) optional post_fix liek 0_{postfix}.wav
# Output directory structure: place the chunks in a specified output directory, creating it if it doesn't exist.

# Filename collision handling: Two chunks should never have the same filename becuase start time cant be identical and they are named according to there index based on start time, add validation to ensure yaml is correct before proceeding with anything else.

# Functionality:
# Fade in/out: Should chunks have fade in/fade out applied at boundaries?

# Silence padding: Should there be any padding with silence at chunk boundaries?

# Validation: Should the tool validate that chunk boundaries don't exceed the audio file duration?

# Could you clarify these points so I can implement the chunking utility according to your needs?