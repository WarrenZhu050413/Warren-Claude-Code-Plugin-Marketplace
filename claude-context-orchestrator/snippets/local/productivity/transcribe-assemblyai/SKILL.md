---
name: "AssemblyAI Transcription"
description: "Use when transcribing audio files with speaker diarization. Triggers on TRANSCRIBE keyword."
pattern: "\\b(TRANSCRIBE)\\b[.,;:!?]?"
---

# AssemblyAI Audio Transcription with Speaker Diarization

## Default Behavior

When the user says "TRANSCRIBE" without specifying a file, **automatically find the latest audio file in `~/Downloads/`**:

```bash
/bin/ls -lt ~/Downloads/ | grep -iE '\.(m4a|mp3|mp4|wav|flac|ogg|webm|mov|avi|mkv)$' | head -1
```

Then transcribe that file. Always confirm which file you found before proceeding.

## Environment

- **Python venv**: `/Users/wz/Desktop/.venv` (assemblyai is installed here)
- **API key**: `REDACTED_ASSEMBLYAI_KEY`

## Required Configuration (CRITICAL)

The API **requires** `speech_models` parameter. Without it, transcription will fail with:
> `"speech_models" must be a non-empty list containing one or more of: "universal-3-pro", "universal-2"`

**Always use this config:**
```python
config=aai.TranscriptionConfig(
    speaker_labels=True,
    speech_models=['universal-3-pro', 'universal-2'],
    language_detection=True
)
```

## Workflow: Transcribe and Save

**Always pipe output directly to file** to avoid large terminal output.

### Step 1: Transcribe to temp file

First transcribe to a temp file next to the audio (using the original audio filename):

```bash
cd /Users/wz/Desktop && source .venv/bin/activate && python3 -c "
import assemblyai as aai
aai.settings.api_key = 'REDACTED_ASSEMBLYAI_KEY'

transcript = aai.Transcriber().transcribe(
    '/path/to/audio.m4a',
    config=aai.TranscriptionConfig(
        speaker_labels=True,
        speech_models=['universal-3-pro', 'universal-2'],
        language_detection=True
    )
)

if transcript.status == aai.TranscriptStatus.error:
    print(f'ERROR: {transcript.error}')
else:
    for u in transcript.utterances:
        print(f'Speaker {u.speaker}: {u.text}')
        print()
" > '/path/to/AudioFileName - transcript.md' 2>&1
```

**Important**: Use `2>&1` to capture errors to the file too, and check the file for errors after.

**Timeout**: Set bash timeout to 300000ms (5 min) since transcription can take a while for long audio.

### Step 2: Content-based rename

After transcription, **read the transcript** and rename the file based on its content:

1. Read the transcript to understand what it's about
2. Generate a descriptive filename: `YYYY-MM-DD - <Topic Summary>.md`
   - Use today's date (or recording date if known from filename)
   - Topic summary should be 3-6 words, Title Case, describing the main subject
   - Examples:
     - `2026-02-05 - Product Permissions Architecture Discussion.md`
     - `2026-01-28 - Client Onboarding Call.md`
     - `2026-02-03 - Weekly Team Standup.md`
3. Rename the temp transcript file to the content-based name (in same directory)

### Step 3: Archive to ~/.transcripts/

**Always** copy the final transcript to `~/.transcripts/` with intelligent grouping by subdirectory:

| Subdirectory | When to use |
|---|---|
| `work/poly/` | Poly/Baoyuan property management business calls |
| `work/meetings/` | General work meetings, standups |
| `work/interviews/` | Job interviews, candidate screens |
| `personal/` | Personal calls, conversations |
| `academic/` | Lectures, office hours, study groups |
| `misc/` | Anything that doesn't fit above |

```bash
mkdir -p ~/.transcripts/<subdirectory>
cp '/path/to/YYYY-MM-DD - Topic Summary.md' ~/.transcripts/<subdirectory>/
```

Use your best judgment to categorize. When unsure, use `misc/`.

### Step 4: Contextual copy (if applicable)

If there's an obvious project-specific location where the transcript belongs, **also** copy it there. Use judgment:

- If discussing a specific codebase project and you're in that repo → `./claude_files/` or a relevant docs folder
- If it's a client/contact call → check if a `contacts/` directory exists for that client
- If no obvious project context → skip this step (the `~/.transcripts/` archive is sufficient)

## Pricing

| Feature | Cost |
|---------|------|
| Core transcription | $0.37/hour ($0.00617/min) |
| Speaker diarization | +$0.36/hour ($0.006/min) |
| **Total with diarization** | **$0.73/hour (~$0.012/min)** |

## Supported Formats

Audio: mp3, mp4, wav, flac, ogg, webm, m4a
Video: mp4, mov, avi, mkv (extracts audio)
Max file size: 5GB

## Common Options

```python
config = aai.TranscriptionConfig(
    speaker_labels=True,                    # Enable diarization (always use)
    speech_models=['universal-3-pro', 'universal-2'],  # REQUIRED
    language_detection=True,                # Auto-detect language
    speakers_expected=2,                    # Hint for expected speakers (optional)
    punctuate=True,                         # Add punctuation
    format_text=True,                       # Format numbers, dates, etc.
    word_boost=["specific", "terms"],       # Boost recognition of specific words
)
```

## Speaker Identification

After transcription, **identify speakers by name if obvious from context**:
- If the user provides context about who the speakers are, label them accordingly (e.g., "Warren:", "Jenny:")
- If identity is obvious from the conversation content (e.g., someone says their name, references their role, or the context makes it clear), label them
- If identity is **not** obvious, leave as generic "Speaker A:", "Speaker B:" etc.—do not guess. Only ask the user if they volunteer the info or if it's needed for the task

When renaming speakers, do a find-and-replace across the entire transcript.

## Post-Transcription Summary

After all copies are done, provide a brief summary:
- **Speakers**: Number detected, with identified names if known
- **Language**: Detected language
- **Topics**: Key subjects discussed
- **Action items**: Any commitments or next steps mentioned
- **Filed to**: List all locations the transcript was saved/copied to
