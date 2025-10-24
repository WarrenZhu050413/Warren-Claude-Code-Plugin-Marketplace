#!/bin/bash
# Spanish Learning TTS Generator
# Usage: ./generate-tts.sh "text" [voice] [lang_code] [speed]

set -e

# Parse arguments
TEXT="${1:?Error: Text required. Usage: $0 \"text\" [voice] [lang_code] [speed]}"
VOICE="${2:-am_michael}"
LANG_CODE="${3:-e}"
SPEED="${4:-0.8}"
SERVER_URL="http://127.0.0.1:9876"

# Validate language code
case "$LANG_CODE" in
    a|b|e|f|h|i|j|p|z) ;;
    *)
        echo "❌ Invalid language code: $LANG_CODE"
        echo "Valid codes: a(English) b(British) e(Spanish) f(French) h(Hindi) i(Italian) j(Japanese) p(Portuguese) z(Chinese)"
        exit 1
        ;;
esac

# Language names function (workaround for sh compatibility)
get_lang_name() {
    case "$1" in
        a) echo "American English" ;;
        b) echo "British English" ;;
        e) echo "Spanish" ;;
        f) echo "French" ;;
        h) echo "Hindi" ;;
        i) echo "Italian" ;;
        j) echo "Japanese" ;;
        p) echo "Portuguese" ;;
        z) echo "Mandarin Chinese" ;;
        *) echo "Unknown" ;;
    esac
}

# Check if server is running
if ! curl -s "$SERVER_URL/languages" > /dev/null 2>&1; then
    echo "🚀 Starting mlx-audio server on port 9876..."
    nohup python3 -m mlx_audio.server --port 9876 > /tmp/mlx_audio_server.log 2>&1 &
    SERVER_PID=$!

    # Wait for server to start (max 20 seconds)
    for i in {1..40}; do
        if curl -s "$SERVER_URL/languages" > /dev/null 2>&1; then
            echo "✅ Server ready"
            break
        fi
        if [ $i -eq 40 ]; then
            echo "❌ Server failed to start after 20 seconds"
            echo "Check logs: tail -f /tmp/mlx_audio_server.log"
            exit 1
        fi
        sleep 0.5
    done
fi

# Generate audio
LANG_NAME=$(get_lang_name "$LANG_CODE")
echo "🎙️  Generating $LANG_NAME audio..."
RESPONSE=$(curl -s -X POST "$SERVER_URL/tts" \
    -d "text=$TEXT" \
    -d "voice=$VOICE" \
    -d "speed=$SPEED" \
    -d "language=$LANG_CODE" \
    -d "model=mlx-community/Kokoro-82M-4bit")

# Check for errors
if echo "$RESPONSE" | grep -q '"error"'; then
    echo "❌ TTS generation failed"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

# Extract filename
FILENAME=$(echo "$RESPONSE" | python3 -c "import json, sys; print(json.load(sys.stdin).get('filename', ''))" 2>/dev/null)
if [ -z "$FILENAME" ]; then
    echo "❌ No audio filename in response"
    exit 1
fi

# Download audio
OUTPUT="/tmp/tts_$(date +%s).wav"
echo "📥 Downloading audio..."
curl -s "$SERVER_URL/audio/$FILENAME" -o "$OUTPUT"

# Display info
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎤 Voice: $VOICE ($LANG_NAME, ${SPEED}x)"
echo "📝 Text: \"$TEXT\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Play audio
if [ -f "$OUTPUT" ]; then
    echo "▶️  Playing audio..."
    if command -v afplay > /dev/null; then
        afplay "$OUTPUT"
    elif command -v play > /dev/null; then
        play "$OUTPUT"
    elif command -v mpv > /dev/null; then
        mpv "$OUTPUT" --no-video
    else
        echo "⚠️  No audio player found. Audio saved to: $OUTPUT"
        exit 0
    fi
    echo "✅ Playback complete"
    rm "$OUTPUT"
else
    echo "❌ Audio file not created"
    exit 1
fi
