# PDF Extraction Benchmarks

## Enterprise Benchmark (2025 Procycons)

Production-grade comparison of ML-based PDF extraction tools.

| Tool | Table Accuracy | Text Fidelity | Speed (s/page) | Memory (GB) |
|------|----------------|---------------|----------------|-------------|
| **Docling** | **97.9%** | **100%** | 6.28 | 2.1 |
| Marker | 89.2% | 98.5% | 8.45 | 3.5 |
| MinerU | 92.1% | 99.2% | 12.33 | 4.2 |
| Unstructured.io | 75.0% | 95.8% | 51.02 | 1.8 |
| PyMuPDF4LLM | 82.3% | 97.1% | 4.12 | 1.2 |
| LlamaParse | 88.5% | 97.3% | 6.00 | N/A (cloud) |

**Test corpus:** 500 academic papers, business reports, financial statements (mixed complexity)

**Key finding:** Docling leads in table accuracy with competitive speed. Unstructured.io despite popularity has poor performance.

*Source: Procycons Enterprise PDF Processing Benchmark 2025*

## Academic PDF Test (This Research)

Real-world testing on distributed cognition literature.

### Test Environment

- **PDFs:** 4 academic books
- **Total size:** 98.2 MB
- **Pages:** ~400 pages combined
- **Content:** Multi-column layouts, tables, figures, references

### Test Results

#### Speed (90-page PDF, 1.9 MB)

| Tool | Total Time | Per Page | Speedup |
|------|------------|----------|---------|
| pdftotext | 0.63s | 0.007s/page | 60x |
| PyMuPDF | 1.18s | 0.013s/page | 33x |
| Docling | 38.86s | 0.432s/page | 1x |
| pdfplumber | 38.91s | 0.432s/page | 1x |

#### Quality (Issues per document)

| Tool | Consecutive Spaces | Excessive Newlines | Control Chars | Garbled | Total |
|------|-------------------|-------------------|---------------|---------|-------|
| pdfplumber | 0 | 0 | 0 | 0 | **0** |
| PyMuPDF | 1 | 0 | 0 | 0 | **1** |
| Docling | 48 | 2 | 0 | 0 | **50** |
| pdftotext | 85 | 5 | 0 | 0 | **90** |

#### Structure Preservation

| Tool | Headers | Tables | Lists | Images |
|------|---------|--------|-------|--------|
| Docling | ✓ 36 | ✓ 16 rows | ✓ 307 items | ✓ 4 markers |
| PyMuPDF | ✗ | ✗ | ✗ | ✗ |
| pdfplumber | ✗ | ✗ | ✗ | ✗ |
| pdftotext | ✗ | ✗ | ✗ | ✗ |

**Key finding:** Docling is the ONLY tool that preserves document structure.

## Production Recommendations

### By Use Case

**Academic research / Literature review:**
- **Primary:** Docling (structure essential)
- **Secondary:** PyMuPDF (speed for large batches)

**RAG system ingestion:**
- **Recommended:** Docling (semantic structure preserved)
- **Alternative:** PyMuPDF + post-processing

**Quick text extraction:**
- **Recommended:** PyMuPDF (60x faster)
- **Alternative:** pdftotext (fastest, lower quality)

**Maximum quality (legal, financial):**
- **Recommended:** pdfplumber (perfect quality)
- **Alternative:** Docling (structure + good quality)

### By Document Type

**Academic papers:** Docling (tables, multi-column, references)
**Books/ebooks:** PyMuPDF (simple linear text)
**Business reports:** Docling (tables, charts, sections)
**Scanned documents:** Docling with OCR enabled
**Legal contracts:** pdfplumber (maximum fidelity)

## ML Model Performance (Docling)

### RT-DETR (Layout Detection)

- **Speed:** 44-633ms per page
- **Accuracy:** ~95% layout element detection
- **Detects:** Text blocks, headers, tables, figures, captions

### TableFormer (Table Structure)

- **Speed:** 400ms-1.74s per table
- **Accuracy:** 97.9% cell-level accuracy
- **Handles:** Borderless tables, merged cells, nested tables

## Cloud vs On-Device

| Tool | Processing | Privacy | Cost | Speed |
|------|-----------|---------|------|-------|
| Docling | On-device | ✓ Private | Free | 0.43s/page |
| LlamaParse | Cloud API | ✗ Sends data | $0.003/page | 6s/page |
| Claude Vision | Cloud API | ✗ Sends data | $0.0075/page | Variable |
| Mathpix | Cloud API | ✗ Sends data | $0.004/page | 4s/page |

**Recommendation:** Use on-device (Docling) for sensitive/unpublished academic work.

## Benchmark Methodology

### Speed Testing

```python
import time

start = time.time()
result = converter.convert(pdf_path)
elapsed = time.time() - start
per_page = elapsed / page_count
```

### Quality Testing

```python
# Count quality issues
consecutive_spaces = len(re.findall(r'  +', text))
excessive_newlines = len(re.findall(r'\n{4,}', text))
control_chars = len(re.findall(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text))
garbled_chars = len(re.findall(r'[�\ufffd]', text))

total_issues = consecutive_spaces + excessive_newlines + control_chars + garbled_chars
```

### Structure Testing

```python
# Count markdown elements
headers = len(re.findall(r'^#{1,6}\s+.+$', markdown, re.MULTILINE))
tables = len(re.findall(r'\|.+\|', markdown))
lists = len(re.findall(r'^\s*[-*]\s+', markdown, re.MULTILINE))
```
