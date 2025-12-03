# PDF Extraction Quality Metrics

## Key Metrics

### 1. Consecutive Spaces
**What:** Multiple spaces in sequence (2+)
**Pattern:** `  +`
**Impact:** Formatting artifacts, token waste
**Good:** < 50 occurrences
**Bad:** > 100 occurrences

### 2. Excessive Newlines
**What:** 4+ consecutive newlines
**Pattern:** `\n{4,}`
**Impact:** Page breaks treated as whitespace
**Good:** < 20 occurrences
**Bad:** > 50 occurrences

### 3. Control Characters
**What:** Non-printable characters
**Pattern:** `[\x00-\x08\x0b\x0c\x0e-\x1f]`
**Impact:** Parsing errors, display issues
**Good:** 0 occurrences
**Bad:** > 0 occurrences

### 4. Garbled Characters
**What:** Replacement characters (�)
**Pattern:** `[�\ufffd]`
**Impact:** Lost information, encoding failures
**Good:** 0 occurrences
**Bad:** > 0 occurrences

### 5. Hyphenation Breaks
**What:** End-of-line hyphens not joined
**Pattern:** `\w+-\n\w+`
**Impact:** Word splitting affects search
**Good:** < 10 occurrences
**Bad:** > 50 occurrences

### 6. Ligature Encoding
**What:** Special character combinations
**Examples:** `/uniFB00` (ff), `/uniFB01` (fi), `/uniFB03` (ffi)
**Impact:** Search failures, readability
**Fix:** Post-process with regex replacement

## Quality Score Formula

```python
total_issues = (
    consecutive_spaces +
    excessive_newlines +
    control_chars +
    garbled_chars
)

quality_score = garbled_chars * 10 + total_issues
# Lower is better
```

**Ranking:**
- Excellent: < 10 score
- Good: 10-50 score
- Fair: 50-100 score
- Poor: > 100 score

## Analysis Script

```python
import re

def analyze_quality(text):
    """Analyze PDF extraction quality."""
    return {
        'chars': len(text),
        'words': len(text.split()),
        'consecutive_spaces': len(re.findall(r'  +', text)),
        'excessive_newlines': len(re.findall(r'\n{4,}', text)),
        'control_chars': len(re.findall(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text)),
        'garbled_chars': len(re.findall(r'[�\ufffd]', text)),
        'hyphen_breaks': len(re.findall(r'\w+-\n\w+', text))
    }

# Usage
text = open("extracted.txt").read()
metrics = analyze_quality(text)
print(f"Quality score: {metrics['garbled_chars'] * 10 + metrics['consecutive_spaces'] + metrics['excessive_newlines']}")
```

## Test Results (90-page Academic PDF)

| Tool | Total Issues | Garbled | Quality Score | Rating |
|------|--------------|---------|---------------|--------|
| pdfplumber | 0 | 0 | 0 | Excellent |
| PyMuPDF | 1 | 0 | 1 | Excellent |
| Docling | 50 | 0 | 50 | Good |
| pdftotext | 90 | 0 | 90 | Fair |
| pdfminer | 45 | 0 | 45 | Good |
| pypdf | 120 | 5 | 170 | Poor |

## Content Completeness

### Phrase Coverage Analysis

Extract 3-word phrases from each tool's output:

```python
def extract_phrases(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    return {' '.join(words[i:i+3]) for i in range(len(words)-2)}

common = set.intersection(*[extract_phrases(t) for t in texts.values()])
```

**Results:**
- Common phrases: 10,587 (captured by all tools)
- Docling unique: 17,170 phrases (most complete)
- pdfplumber unique: 8,229 phrases (conservative)

## Cleaning Strategies

### Fix Ligatures

```python
def fix_ligatures(text):
    """Fix PDF ligature encoding."""
    replacements = {
        r'/uniFB00': 'ff',
        r'/uniFB01': 'fi',
        r'/uniFB02': 'fl',
        r'/uniFB03': 'ffi',
        r'/uniFB04': 'ffl',
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)
    return text
```

### Normalize Whitespace

```python
def normalize_whitespace(text):
    """Clean excessive whitespace."""
    text = re.sub(r'  +', ' ', text)  # Multiple spaces → single
    text = re.sub(r'\n{4,}', '\n\n\n', text)  # Many newlines → max 3
    return text.strip()
```

### Join Hyphenated Words

```python
def join_hyphens(text):
    """Join end-of-line hyphenated words."""
    return re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
```
