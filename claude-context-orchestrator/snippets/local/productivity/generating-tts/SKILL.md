---
name: generating-tts
description: Generate and play multilingual text-to-speech audio using mlx-audio with Kokoro model. Use when user asks to hear pronunciation, speak text aloud, or wants audio for language learning. Supports 9 languages (English, Spanish, French, Italian, Portuguese, Hindi, Japanese, Chinese) and 11 voices with speed control.
---

# Text-to-Speech Generation Skill

## When to Use

Trigger: User asks to hear pronunciation, say something aloud, or wants audio for language learning.

## Supported Languages

| Code | Language | Notes |
|------|----------|-------|
| `a` | American English | Default |
| `b` | British English | |
| `e` | Spanish | |
| `f` | French | |
| `h` | Hindi | |
| `i` | Italian | |
| `j` | Japanese | Requires `pip install misaki[ja]` |
| `p` | Portuguese (Brazilian) | |
| `z` | Mandarin Chinese | Requires `pip install misaki[zh]` |

## Available Voices

**Pattern:** `[language][gender]_[name]` (e.g., `af_heart` = American Female Heart)

**American Female:**
- `af_heart` - Warm, friendly ⭐ **Default**
- `af_nova` - Clear, precise (best for pronunciation)
- `af_bella` - Expressive
- `af_sky` - Bright
- `af_sarah` - Gentle

**American Male:**
- `am_adam` - Strong
- `am_michael` - Authoritative (great for language learning)
- `am_eric` - Friendly

**British Female:**
- `bf_emma` - Elegant
- `bf_isabella` - Sophisticated

**British Male:**
- `bm_george` - Distinguished
- `bm_lewis` - Professional

## Speed Control

Range: 0.5x to 2.0x (default 1.0x)

- **0.5-0.8x**: Slow, for difficult pronunciation or beginners
- **1.0x**: Natural pace
- **1.2-1.5x**: Faster, for advanced learners
- **1.8-2.0x**: Very fast, speed listening

## Prerequisites & Setup

### Required Installation

Before using TTS, install mlx-audio:

```bash
pip install mlx-audio
```

### Optional Language Support

For Japanese and Chinese, install additional components:

```bash
pip install misaki[ja]    # For Japanese
pip install misaki[zh]    # For Chinese
```

### Server Startup

The `generate_tts` function automatically starts the mlx-audio server if it's not running, but you can also start it manually:

```bash
# Start server on port 9876 (runs in background)
mlx_audio.server --port 9876 &

# Or start with log output to monitor
mlx_audio.server --port 9876 > /tmp/mlx_audio_server_9876.log 2>&1 &
```

**First run startup time:** 6-10 seconds (model loads and caches)
**Subsequent calls:** 1-2 seconds per audio generation

### Verify Server is Running

```bash
# Check if server is responding
curl http://127.0.0.1:9876/languages

# If you get JSON response, server is ready
```

## Implementation

### Bash Function

```bash
generate_tts() {
    local text="$1"
    local voice="${2:-af_heart}"
    local lang_code="${3:-a}"
    local speed="${4:-1.0}"
    local server_url="http://127.0.0.1:9876"

    # Validate
    [ -z "$text" ] && { echo "❌ No text provided"; return 1; }

    case "$lang_code" in
        a|b|e|f|h|i|j|p|z) ;;
        *) echo "❌ Invalid language code: $lang_code"; return 1 ;;
    esac

    # Language names
    declare -A lang_names=([a]="American English" [b]="British English" [e]="Spanish" [f]="French" [h]="Hindi" [i]="Italian" [j]="Japanese" [p]="Portuguese" [z]="Mandarin Chinese")

    # Start server if needed
    if ! curl -s "$server_url/languages" > /dev/null 2>&1; then
        echo "🚀 Starting mlx-audio server..."
        nohup mlx_audio.server --port 9876 > /tmp/mlx_audio_server_9876.log 2>&1 &

        for i in {1..20}; do
            curl -s "$server_url/languages" > /dev/null 2>&1 && { echo "✅ Server ready"; break; }
            sleep 0.5
        done

        curl -s "$server_url/languages" > /dev/null 2>&1 || { echo "❌ Server failed. Check: tail -f /tmp/mlx_audio_server_9876.log"; return 1; }
    fi

    # Generate audio
    echo "🎙️  Generating ${lang_names[$lang_code]} audio..."
    local response=$(curl -s -X POST "$server_url/tts" \
      -d "text=$text" -d "voice=$voice" -d "speed=$speed" \
      -d "language=$lang_code" -d "model=mlx-community/Kokoro-82M-4bit")

    # Extract filename
    echo "$response" | grep -q '"error"' && { echo "❌ TTS failed"; return 1; }
    local filename=$(echo "$response" | python3 -c "import json, sys; print(json.load(sys.stdin)['filename'])" 2>/dev/null)
    [ -z "$filename" ] && { echo "❌ No audio filename"; return 1; }

    # Download and play
    local output="/tmp/tts_$(date +%s).wav"
    curl -s "$server_url/audio/$filename" -o "$output"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎤 ${voice} says (${lang_names[$lang_code]}, ${speed}x):"
    echo "   \"$text\""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    echo "▶️  Playing audio..."
    afplay "$output"
    echo "✅ Playback complete"
    rm "$output"
}

export -f generate_tts
```

### Usage

```bash
generate_tts "text" "voice" "lang_code" "speed"

# Examples
generate_tts "Hello"                                    # Default (English, af_heart, 1.0x)
generate_tts "Hola" "am_michael" "e" "0.8"             # Spanish, slower
generate_tts "Bonjour" "bf_emma" "f" "1.0"             # French, British voice
generate_tts "Ciao" "af_bella" "i" "1.0"               # Italian
```

## Workflow

When user requests TTS:

1. **Extract text** to speak
2. **Determine language** from context
3. **Choose voice:**
   - Default: `af_heart`
   - Clear pronunciation: `af_nova`
   - Language learning: `am_michael`
4. **Set speed:**
   - Beginners: 0.8x
   - Normal: 1.0x
   - Advanced: 1.2x
5. **Call generate_tts** with parameters

## Voice Selection Guide

| Use Case | Voice | Reason |
|----------|-------|--------|
| General | `af_heart` | Warm, approachable |
| Clear pronunciation | `af_nova` | Precise |
| Language learning | `am_michael` | Authoritative |
| Professional | `bf_emma`, `bm_george` | Distinguished |

| Language | Best Voices | Speed |
|----------|------------|-------|
| Spanish/Portuguese/Chinese | `am_michael`, `af_heart` | 0.8-1.0x |
| French | `af_nova`, `bf_emma` | 0.8x |
| Italian | `af_bella`, `am_adam` | 1.0x |
| Japanese | `af_nova`, `af_heart` | 1.0x |

## Best Practices

**DO:**
- Show text before playing
- Use appropriate speed for context
- Keep text moderate length (1-3 sentences)
- Generate only when user requests

**DON'T:**
- Auto-generate without request
- Use very long text (split into chunks)
- Mix languages in one call

## Example Interactions

**Pronunciation:**
```
User: "How do you pronounce 'entrepreneur'?"
Claude: "The word 'entrepreneur' is pronounced: /ˌɑːntrəprəˈnɜːr/"
[Calls: generate_tts "entrepreneur" "af_nova" "a" "0.8"]
```

**Language Learning:**
```
User: "How do you say 'good morning' in Spanish?"
Claude: "In Spanish: **Buenos días** (buenos = good, días = days/morning)"
[Calls: generate_tts "Buenos días" "am_michael" "e" "0.8"]
```

## Troubleshooting

### Server Won't Start

**1. Check if mlx-audio is installed:**
```bash
python3 -c "import mlx_audio; print('✅ mlx-audio installed')"
```

**2. If not installed, install it:**
```bash
pip install mlx-audio
```

**3. Check if port 9876 is in use:**
```bash
lsof -i :9876                    # List what's using the port
kill $(lsof -t -i:9876)          # Kill existing process
```

**4. Start server manually and monitor logs:**
```bash
mlx_audio.server --port 9876 > /tmp/mlx_audio_server_9876.log 2>&1 &
tail -f /tmp/mlx_audio_server_9876.log  # Watch startup logs
```

**5. If server still fails to start:**
- Check available disk space (model cache requires ~2GB)
- Verify Python 3.9+ is installed
- Try on a machine with better hardware (requires GPU/CPU acceleration)

### TTS Generation Fails

**Server is running but audio generation fails:**
1. Check server logs: `tail -f /tmp/mlx_audio_server_9876.log`
2. Verify curl can reach server: `curl http://127.0.0.1:9876/languages`
3. Check if text is valid (not empty, properly quoted)

### Audio Not Playing

**File generated but won't play:**
```bash
# Test afplay works on macOS
afplay /System/Library/Sounds/Glass.aiff

# Check if audio files are being created
ls -lh /tmp/tts_*.wav
```

### Missing Language Dependencies

Install optional language support if needed:
```bash
pip install misaki[ja]           # For Japanese
pip install misaki[zh]           # For Chinese
```

## Performance Notes

**Typical timing:**
- Server already running: ~1-2 seconds per call
- Server cold start: ~6-10 seconds (model loads once)
- First generation: ~3-5 seconds (model cached in memory)
- Subsequent calls: ~1-2 seconds (model cached)

**Memory usage:**
- Server baseline: ~200MB
- Running model: ~2GB RAM
- Cache: ~2GB disk

**Optimization tips:**
- Start server once at session beginning if doing multiple TTS calls
- Keep text moderate length (1-3 sentences) for faster generation
- Don't stop server between calls - it stays ready in background
