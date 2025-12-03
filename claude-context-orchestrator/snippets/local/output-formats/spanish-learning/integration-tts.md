# TTS Integration - CLI Usage

## Setup (One Time)

### 1. Install mlx-audio

```bash
pip install mlx-audio
```

Optional language support:
```bash
pip install misaki[ja]    # For Japanese
pip install misaki[zh]    # For Chinese
```

### 2. Make script executable

```bash
chmod +x ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/snippets/local/output-formats/spanish-learning/scripts/generate-tts.sh
```

### 3. Create alias for easy access

```bash
# Add to ~/.zshrc or ~/.bashrc
alias tts='~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/snippets/local/output-formats/spanish-learning/scripts/generate-tts.sh'
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

---

## CLI Usage

### Basic Command

```bash
./generate-tts.sh "Spanish text"
```

Or with alias:
```bash
tts "Spanish text"
```

### Full Command Format

```bash
./generate-tts.sh "text" [voice] [lang_code] [speed]
```

**Parameters:**
1. `text` - **REQUIRED** - The text to pronounce
2. `voice` - Optional, default: `am_michael`
3. `lang_code` - Optional, default: `e` (Spanish)
4. `speed` - Optional, default: `0.8`

---

## Examples

### Spanish (Defaults)

```bash
tts "Hola, ¿cómo estás?"
```

### Spanish with Custom Voice

```bash
tts "Me gustaría aprender español" "af_heart" "e" "0.8"
```

### Spanish Slower

```bash
tts "Efectivamente" "am_michael" "e" "0.5"
```

### Spanish Faster

```bash
tts "¿Cómo se dice esto?" "am_michael" "e" "1.2"
```

### Other Languages

```bash
tts "Bonjour" "af_nova" "f" "0.8"        # French
tts "Ciao" "af_bella" "i" "1.0"          # Italian
tts "Olá" "am_michael" "p" "0.8"         # Portuguese
```

---

## Voice Options

### American Voices

**Female:**
- `af_heart` ⭐ Warm, friendly (default alternative)
- `af_nova` - Clear, precise (best for pronunciation)
- `af_bella` - Expressive
- `af_sky` - Bright
- `af_sarah` - Gentle

**Male:**
- `am_michael` ⭐ Authoritative (default for learning)
- `am_adam` - Strong
- `am_eric` - Friendly

### British Voices

**Female:**
- `bf_emma` - Elegant
- `bf_isabella` - Sophisticated

**Male:**
- `bm_george` - Distinguished
- `bm_lewis` - Professional

---

## Language Codes

| Code | Language | Best Voices | Speed |
|------|----------|-------------|-------|
| `a` | American English | af_heart, am_michael | 1.0x |
| `b` | British English | bf_emma, bm_george | 1.0x |
| `e` | **Spanish** | **am_michael**, af_heart | **0.8x** |
| `f` | French | af_nova, bf_emma | 0.8x |
| `h` | Hindi | af_heart, am_michael | 0.9x |
| `i` | Italian | af_bella, am_adam | 1.0x |
| `j` | Japanese | af_nova, af_heart | 1.0x |
| `p` | Portuguese | am_michael, af_heart | 0.8x |
| `z` | Mandarin Chinese | am_michael, af_heart | 0.9x |

---

## Speed Reference

| Speed | Use Case | Example |
|-------|----------|---------|
| **0.5x** | Very slow (difficult words) | `tts "algoritmo" "am_michael" "e" "0.5"` |
| **0.7x** | Slow (complete beginner) | `tts "efectivamente" "am_michael" "e" "0.7"` |
| **0.8x** | Learner pace (A2 level) ⭐ | `tts "Quiero aprender" "am_michael" "e" "0.8"` |
| **1.0x** | Natural speed | `tts "Hola" "am_michael" "e" "1.0"` |
| **1.2x** | Faster (advanced learners) | `tts "La educación es importante" "am_michael" "e" "1.2"` |
| **1.5x** | Fast | `tts "texto rápido" "am_michael" "e" "1.5"` |
| **2.0x** | Very fast (speed listening) | `tts "speed-listening practice" "am_michael" "e" "2.0"` |

---

## Server Management

### Check if Server is Running

```bash
curl http://127.0.0.1:9876/languages
```

If you get JSON response, server is ready. If not, the script starts it automatically.

### Start Server Manually

```bash
python3 -m mlx_audio.server --port 9876 > /tmp/mlx_audio_server.log 2>&1 &
```

### Monitor Server Logs

```bash
tail -f /tmp/mlx_audio_server.log
```

### Stop Server

```bash
pkill -f "mlx_audio.server"
```

### Check if Port 9876 is In Use

```bash
lsof -i :9876
```

---

## Troubleshooting

### Command Not Found

**Make sure script is executable:**
```bash
chmod +x ~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/snippets/local/output-formats/spanish-learning/scripts/generate-tts.sh
```

**Use full path if alias not set up:**
```bash
~/.claude/plugins/marketplaces/warren-claude-code-plugin-marketplace/claude-context-orchestrator/snippets/local/output-formats/spanish-learning/scripts/generate-tts.sh "text"
```

### mlx-audio Not Installed

```bash
pip install mlx-audio
```

### Server Won't Start

**Check if mlx-audio is properly installed:**
```bash
python3 -c "import mlx_audio; print('✅ OK')"
```

**Check if port 9876 is in use:**
```bash
lsof -i :9876
kill $(lsof -t -i:9876)  # Kill if needed
```

**Start server manually and watch logs:**
```bash
python3 -m mlx_audio.server --port 9876
tail -f /tmp/mlx_audio_server.log  # In another terminal
```

### Audio Generation Fails

**Verify server is responding:**
```bash
curl http://127.0.0.1:9876/languages
```

**Check server logs:**
```bash
tail -f /tmp/mlx_audio_server.log
```

**Try with simpler text:**
```bash
tts "Hola"
```

### No Audio Player Found

The script supports:
- `afplay` (macOS default)
- `play` (SoX)
- `mpv`

Install one if needed:
```bash
# macOS
brew install mpv

# Linux
sudo apt install mpv  # Ubuntu/Debian
sudo pacman -S mpv    # Arch
```

---

## Performance Notes

**Typical timing:**
- Server already running: ~1-2 seconds
- Server first start: ~6-10 seconds (model loads)
- Subsequent calls: ~1-2 seconds (cached)

**Optimization:**
- Server stays running in background
- No need to restart between calls
- Keep text under 3 sentences for faster generation

---

## Environment Variables (Optional)

You can set defaults in your shell profile:

```bash
# Add to ~/.zshrc or ~/.bashrc
export TTS_VOICE="am_michael"
export TTS_LANG="e"
export TTS_SPEED="0.8"
```

Then use with defaults:
```bash
tts "Tu texto aquí"
```
