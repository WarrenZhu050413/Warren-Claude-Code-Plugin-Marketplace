---
name: pdftext
description: Extract text from PDFs for LLM consumption using AI-powered or traditional tools. Use when converting academic PDFs to markdown, extracting structured content (headers/tables/lists), batch processing research papers, preparing PDFs for RAG systems, or when mentions of "pdf extraction", "pdf to text", "pdf to markdown", "docling", "pymupdf", "pdfplumber" appear. Provides Docling (AI-powered, structure-preserving, 97.9% table accuracy) and traditional tools (PyMuPDF for speed, pdfplumber for quality). All processing is on-device with no API calls.
license: Apache 2.0 (see LICENSE.txt)
---

# PDF Text Extraction

## Tool Selection

| Tool | Speed | Quality | Structure | Use When |
|------|-------|---------|-----------|----------|
| **Docling** | 0.43s/page | Good | ✓ Yes | Need headers/tables/lists, academic PDFs, LLM consumption |
| **PyMuPDF** | 0.01s/page | Excellent | ✗ No | Speed critical, simple text extraction, good enough quality |
| **pdfplumber** | 0.44s/page | Perfect | ✗ No | Maximum fidelity needed, slow acceptable |

**Decision:**
- Academic research → Docling (structure preservation)
- Batch processing → PyMuPDF (60x faster)
- Critical accuracy → pdfplumber (0 quality issues)

## Installation

```bash
# Create virtual environment
python3 -m venv pdf_env
source pdf_env/bin/activate

# Install Docling (AI-powered, recommended)
pip install docling

# Install traditional tools
pip install pymupdf pdfplumber
```

**First run downloads ML models** (~500MB-1GB, cached locally, no API calls).

## Basic Usage

### Docling (Structure-Preserving)

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()  # Reuse for multiple PDFs
result = converter.convert("paper.pdf")
markdown = result.document.export_to_markdown()

# Save output
with open("paper.md", "w") as f:
    f.write(markdown)
```

**Output includes:** Headers (##), tables (|...|), lists (- ...), image markers.

### PyMuPDF (Fast)

```python
import fitz

doc = fitz.open("paper.pdf")
text = "\n".join(page.get_text() for page in doc)
doc.close()

with open("paper.txt", "w") as f:
    f.write(text)
```

### pdfplumber (Highest Quality)

```python
import pdfplumber

with pdfplumber.open("paper.pdf") as pdf:
    text = "\n".join(page.extract_text() or "" for page in pdf.pages)

with open("paper.txt", "w") as f:
    f.write(text)
```

## Batch Processing

See `examples/batch_convert.py` for ready-to-use script.

**Pattern:**
```python
from pathlib import Path
from docling.document_converter import DocumentConverter

converter = DocumentConverter()  # Initialize once
for pdf in Path("./pdfs").glob("*.pdf"):
    result = converter.convert(str(pdf))
    markdown = result.document.export_to_markdown()
    Path(f"./output/{pdf.stem}.md").write_text(markdown)
```

**Performance tip:** Reuse converter instance. Reinitializing wastes time.

## Quality Considerations

**Common issues:**
- Ligatures: `/uniFB03` → "ffi" (post-process with regex)
- Excessive whitespace: 50-90 instances (Docling has fewer)
- Hyphenation breaks: End-of-line hyphens may remain

**Quality metrics script:** See `examples/quality_analysis.py`

**Benchmarks:** See `references/benchmarks.md` for enterprise production data.

## Troubleshooting

**Slow first run:** ML models downloading (15-30s). Subsequent runs fast.

**Out of memory:** Reduce concurrent conversions, process large PDFs individually.

**Missing tables:** Ensure `do_table_structure=True` in Docling options.

**Garbled text:** PDF encoding issue. Apply ligature fixes post-processing.

## Privacy

**All tools run on-device.** No API calls, no data sent externally. Docling downloads models once, caches locally (~500MB-1GB).

## References

- Tool comparison: `references/tool-comparison.md`
- Quality metrics: `references/quality-metrics.md`
- Production benchmarks: `references/benchmarks.md`
