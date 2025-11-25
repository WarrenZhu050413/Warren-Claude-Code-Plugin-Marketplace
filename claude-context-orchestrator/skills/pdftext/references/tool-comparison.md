# PDF Tool Comparison

## Summary Table

| Tool | Type | Speed | Quality Issues | Garbled | Structure | License |
|------|------|-------|----------------|---------|-----------|---------|
| **Docling** | ML | 0.43s/page | 50 | 0 | ✓ Yes | Apache 2.0 |
| **PyMuPDF** | Traditional | 0.01s/page | 1 | 0 | ✗ No | AGPL |
| **pdfplumber** | Traditional | 0.44s/page | 0 | 0 | ✗ No | MIT |
| **pdftotext** | Traditional | 0.007s/page | 90 | 0 | ✗ No | GPL |
| **pdfminer.six** | Traditional | 0.15s/page | 45 | 0 | ✗ No | MIT |
| **pypdf** | Traditional | 0.25s/page | 120 | 5 | ✗ No | BSD |

*Test environment: 90-page academic PDF, 1.9 MB*

## Detailed Comparison

### Docling (Recommended for Academic PDFs)

**Advantages:**
- Only tool that preserves structure (headers, tables, lists)
- AI-powered layout understanding via RT-DETR + TableFormer
- Markdown output perfect for LLMs
- 97.9% table accuracy in enterprise benchmarks
- On-device processing (no API calls)

**Disadvantages:**
- Slower than PyMuPDF (40x)
- Requires 500MB-1GB model download
- Some ligature encoding issues

**Use when:**
- Document structure is essential
- Processing academic papers with tables
- Preparing content for RAG systems
- LLM consumption is primary goal

### PyMuPDF (Recommended for Speed)

**Advantages:**
- Fastest tool (60x faster than pdfplumber)
- Excellent quality (only 1 issue in test)
- Clean output with minimal artifacts
- C-based, highly optimized

**Disadvantages:**
- No structure preservation
- AGPL license (restrictive for commercial use)
- Flat text output

**Use when:**
- Speed is critical
- Simple text extraction sufficient
- Batch processing large datasets
- Structure preservation not needed

### pdfplumber (Recommended for Quality)

**Advantages:**
- Perfect quality (0 issues)
- Character-level spatial analysis
- Geometric table detection
- MIT license

**Disadvantages:**
- Very slow (60x slower than PyMuPDF)
- No markdown structure output
- CPU-intensive

**Use when:**
- Maximum fidelity required
- Quality more important than speed
- Processing critical documents
- Slow processing acceptable

## Traditional vs ML-Based

### Traditional Tools

**How they work:**
- Parse PDF internal structure
- Extract embedded text objects
- Follow PDF specification rules

**Advantages:**
- Fast (no ML inference)
- Small footprint (no model files)
- Deterministic output

**Disadvantages:**
- No layout understanding
- Cannot handle borderless tables
- Lose document hierarchy

### ML-Based Tools (Docling)

**How they work:**
- Computer vision to "see" document layout
- RT-DETR detects layout regions
- TableFormer understands table structure
- Hybrid: ML for layout + PDF parsing for text

**Advantages:**
- Understands visual layout
- Handles complex multi-column layouts
- Preserves semantic structure
- Works with borderless tables

**Disadvantages:**
- Slower (ML inference time)
- Larger footprint (model files)
- Non-deterministic output

## Architecture Details

### Docling Pipeline

1. **PDF Backend** - Extracts raw content and positions
2. **AI Models** - Analyze layout and structure
   - RT-DETR: Layout analysis (44-633ms/page)
   - TableFormer: Table structure (400ms-1.74s/table)
3. **Assembly** - Combines understanding with text

### pdfplumber Architecture

1. **Built on pdfminer.six** - Character-level extraction
2. **Spatial clustering** - Groups chars into words/lines
3. **Geometric detection** - Finds tables from lines/rectangles
4. **Character objects** - Full metadata (position, font, size, color)

## Enterprise Benchmarks (2025 Procycons)

| Tool | Table Accuracy | Text Fidelity | Speed (s/page) |
|------|----------------|---------------|----------------|
| Docling | 97.9% | 100% | 6.28 |
| Marker | 89.2% | 98.5% | 8.45 |
| MinerU | 92.1% | 99.2% | 12.33 |
| Unstructured.io | 75.0% | 95.8% | 51.02 |
| LlamaParse | 88.5% | 97.3% | 6.00 |

*Source: Procycons Enterprise PDF Processing Benchmark 2025*
