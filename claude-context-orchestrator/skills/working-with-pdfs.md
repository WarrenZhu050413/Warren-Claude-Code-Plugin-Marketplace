# Working with PDF Files: A Comprehensive Guide

## Mental Model: PDF is a Page-Description Language

**🧠 Core Concept**: PDF (Portable Document Format) is NOT just a "document" - it's a **programming language** that describes how to draw a page.

**Think of PDF like PostScript:**
- PDF = Instructions for drawing text, shapes, images on a page
- PDF files contain **objects** (text, fonts, images, graphics)
- Objects reference each other (like pointers in C)
- **Streams** contain compressed data (images, fonts, content)
- Each page is rendered independently

**What this means:**
- PDFs are **paginated** - each page is self-contained
- **No inherent structure** - text can be drawn in any order
- **Fonts are embedded** - ensures consistent appearance everywhere
- **Images are embedded** - no external dependencies
- **Difficult to edit** - need to understand object references
- **Perfect for print** - exact pixel-perfect rendering

**Practical implications:**
```bash
# Prove it: PDF is text-based (mostly)
strings document.pdf | head -50
# You'll see: %PDF-1.7, /Type /Page, /Font, /Image, etc.

# Extract the structure
pdfinfo document.pdf  # Metadata
pdftk document.pdf dump_data  # Internal structure
```

**PDF vs DOCX:**
| PDF | DOCX |
|-----|------|
| Page description language | Document structure (XML) |
| Fixed layout | Reflowable content |
| Perfect for distribution | Perfect for editing |
| Fonts embedded | Fonts referenced |
| Hard to extract structured data | Easy to extract structured data |
| No revision history | Track changes built-in |

---

## The PDF Ecosystem: Choose Your Tool

| **Task** | **Best Tool** | **Why** |
|----------|---------------|---------|
| Create new PDF | `reportlab` (Python) or `pdf-lib` (JS) | Programmatic control, reusable |
| Read/extract text | `pdfplumber` (Python) | Best table extraction |
| Merge/split/rotate | `qpdf` (CLI) or `pypdf` (Python) | Fast, reliable |
| Fill forms | Python scripts (fillable) or annotations (non-fillable) | Handles both types |
| Convert to images | `pdftoppm` (CLI) or `pypdfium2` (Python) | High quality, fast |
| Extract images | `pdfimages` (CLI) | Direct extraction, original quality |
| OCR scanned PDFs | `pytesseract` + `pdf2image` | Industry standard |
| Encrypt/decrypt | `qpdf` (CLI) or `pypdf` (Python) | Secure, well-tested |
| Optimize/compress | `qpdf --optimize` or Ghostscript | Reduces file size |
| Inspect internals | `qpdf --show-object` | Debugging |

---

## Part 1: Reading PDFs

### Quick Text Extraction

**Use Case**: Get all text from a PDF.

```bash
# Method 1: pdftotext (fastest, preserves layout)
pdftotext -layout document.pdf output.txt

# Method 2: pdftotext (simple, one column)
pdftotext document.pdf output.txt

# Extract specific pages (1-5)
pdftotext -f 1 -l 5 document.pdf output.txt

# Extract with bounding box info (for structured extraction)
pdftotext -bbox-layout document.pdf output.xml
```

**Python approach:**
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"Page {i+1}:\n{text}\n")
```

### Extracting Metadata

**What's inside PDF metadata?**
- Title, author, subject, keywords
- Creation date, modification date
- Creator application (e.g., "Microsoft Word")
- PDF version (1.4, 1.7, 2.0)
- Page count, page size
- Encryption status

```bash
# Method 1: pdfinfo (CLI)
pdfinfo document.pdf

# Method 2: qpdf
qpdf --show-metadata document.pdf
```

**Python approach:**
```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
meta = reader.metadata

print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
print(f"Producer: {meta.producer}")
print(f"Created: {meta.creation_date}")
print(f"Modified: {meta.modification_date}")
print(f"Pages: {len(reader.pages)}")
```

**Why PDFs have metadata:**
- **Searchability**: Find documents by author, subject
- **Legal compliance**: Track authorship, creation dates
- **Workflow**: Identify document versions, software used
- **Copyright**: Establish intellectual property rights

### Extracting Tables

**Use Case**: Convert PDF tables to Excel/CSV.

**Python with pdfplumber (BEST for tables):**
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("report.pdf") as pdf:
    all_tables = []

    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table exists
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

    # Combine all tables
    if all_tables:
        combined = pd.concat(all_tables, ignore_index=True)
        combined.to_excel("extracted_tables.xlsx", index=False)
        combined.to_csv("extracted_tables.csv", index=False)
```

**Advanced table extraction (custom settings):**
```python
import pdfplumber

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]

    # Custom settings for complex tables
    table_settings = {
        "vertical_strategy": "lines",      # Detect vertical edges
        "horizontal_strategy": "lines",    # Detect horizontal edges
        "snap_tolerance": 3,                # Snap nearby lines
        "intersection_tolerance": 15        # Tolerance for intersections
    }

    tables = page.extract_tables(table_settings)

    # Visual debugging: see how pdfplumber detected the table
    img = page.to_image(resolution=150)
    img.debug_tablefinder()
    img.save("table_debug.png")
```

### Extracting Images

**Method 1: pdfimages (fastest, original quality)**
```bash
# Extract all images (preserves original format)
pdfimages -all document.pdf images/img
# Creates: images/img-000.jpg, images/img-001.png, etc.

# Extract as JPEG only
pdfimages -j document.pdf images/img

# Extract with page numbers in filename
pdfimages -p document.pdf images/page

# List images without extracting
pdfimages -list document.pdf
```

**Method 2: Convert pages to images (for visualization)**
```bash
# Convert entire PDF to PNG images (one per page)
pdftoppm -png -r 150 document.pdf page
# Creates: page-1.png, page-2.png, etc.

# High resolution (300 DPI)
pdftoppm -png -r 300 document.pdf page

# Specific pages (2-5)
pdftoppm -png -r 150 -f 2 -l 5 document.pdf page

# JPEG output with quality control
pdftoppm -jpeg -jpegopt quality=90 -r 200 document.pdf page
```

**Python approach (render pages to images):**
```python
import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument("document.pdf")

for i, page in enumerate(pdf):
    # Render at 2x resolution
    bitmap = page.render(scale=2.0, rotation=0)

    # Convert to PIL Image
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.png", "PNG")

    # Or as JPEG
    img.save(f"page_{i+1}.jpg", "JPEG", quality=90)
```

### OCR for Scanned PDFs

**Use Case**: Extract text from scanned documents (images, not searchable text).

```python
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path("scanned.pdf", dpi=300)

# OCR each page
text = ""
for i, image in enumerate(images):
    page_text = pytesseract.image_to_string(image, lang='eng')
    text += f"\n--- Page {i+1} ---\n{page_text}"

# Save extracted text
with open("ocr_output.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

**Multi-language OCR:**
```python
# Install language packs: sudo apt-get install tesseract-ocr-spa tesseract-ocr-fra

# Spanish OCR
page_text = pytesseract.image_to_string(image, lang='spa')

# Multiple languages
page_text = pytesseract.image_to_string(image, lang='eng+spa')
```

---

## Part 2: Creating PDFs

### Python with reportlab - For Reports and Documents

**Mental Model**: reportlab = Canvas for drawing + Platypus for document flow

**Simple PDF creation:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter  # 612 x 792 points (8.5" x 11")

# Draw text (x, y coordinates from bottom-left)
c.drawString(100, height - 100, "Hello, World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Draw a line
c.line(100, height - 140, 400, height - 140)

# Draw a rectangle
c.rect(100, height - 200, 300, 50)

# Save
c.save()
```

**Professional multi-page document:**
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

# Create document
doc = SimpleDocTemplate("report.pdf", pagesize=letter,
                        leftMargin=inch, rightMargin=inch,
                        topMargin=inch, bottomMargin=inch)

styles = getSampleStyleSheet()
story = []

# Title
title = Paragraph("Quarterly Sales Report", styles['Title'])
story.append(title)
story.append(Spacer(1, 0.3*inch))

# Body text
body_text = "This report covers Q1 2025 sales performance across all regions."
story.append(Paragraph(body_text, styles['Normal']))
story.append(Spacer(1, 0.2*inch))

# Table
data = [
    ['Region', 'Q1 Sales', 'Q2 Sales', 'Growth'],
    ['North', '$120K', '$135K', '12.5%'],
    ['South', '$85K', '$92K', '8.2%'],
    ['East', '$110K', '$125K', '13.6%'],
    ['West', '$95K', '$105K', '10.5%']
]

table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
table.setStyle(TableStyle([
    # Header row
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 14),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

    # Data rows
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 1), (-1, -1), 12),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
story.append(table)

# New page
story.append(PageBreak())

# Page 2 content
story.append(Paragraph("Detailed Analysis", styles['Heading1']))
story.append(Paragraph("See appendix for full breakdown.", styles['Normal']))

# Build PDF
doc.build(story)
```

**Adding images:**
```python
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image

# Add image to story
img = Image("logo.png", width=2*inch, height=1*inch)
story.append(img)
```

### JavaScript with pdf-lib - For Forms and Modification

**Mental Model**: pdf-lib = Load, modify, save - works in Node.js and browsers

**Basic PDF creation:**
```javascript
import { PDFDocument, rgb, StandardFonts } from 'pdf-lib';
import fs from 'fs';

async function createPDF() {
    const pdfDoc = await PDFDocument.create();
    const page = pdfDoc.addPage([595, 842]); // A4 size in points
    const { width, height } = page.getSize();

    // Embed font
    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);

    // Draw text
    page.drawText('Hello, World!', {
        x: 50,
        y: height - 50,
        size: 24,
        font: font,
        color: rgb(0, 0, 0)
    });

    // Draw rectangle
    page.drawRectangle({
        x: 50,
        y: height - 150,
        width: 200,
        height: 100,
        borderColor: rgb(0, 0, 0),
        borderWidth: 2
    });

    // Save
    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('created.pdf', pdfBytes);
}

createPDF();
```

**Load and modify existing PDF:**
```javascript
import { PDFDocument } from 'pdf-lib';
import fs from 'fs';

async function modifyPDF() {
    // Load existing PDF
    const existingPdfBytes = fs.readFileSync('input.pdf');
    const pdfDoc = await PDFDocument.load(existingPdfBytes);

    // Get first page
    const pages = pdfDoc.getPages();
    const firstPage = pages[0];

    // Add text to existing page
    firstPage.drawText('CONFIDENTIAL', {
        x: 50,
        y: 50,
        size: 12,
        color: rgb(1, 0, 0)
    });

    // Add new page
    const newPage = pdfDoc.addPage([600, 400]);
    newPage.drawText('Appendix', { x: 100, y: 300, size: 18 });

    // Save modified PDF
    const pdfBytes = await pdfDoc.save();
    fs.writeFileSync('modified.pdf', pdfBytes);
}

modifyPDF();
```

---

## Part 3: Common PDF Operations

### Merge PDFs

**CLI (fastest):**
```bash
# Method 1: qpdf
qpdf --empty --pages file1.pdf file2.pdf file3.pdf -- merged.pdf

# Method 2: pdftk (if available)
pdftk file1.pdf file2.pdf file3.pdf cat output merged.pdf
```

**Python:**
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()

for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

### Split PDFs

**CLI:**
```bash
# Split into individual pages
qpdf input.pdf --pages . 1 -- page_1.pdf
qpdf input.pdf --pages . 2 -- page_2.pdf

# Split into groups of 3 pages
qpdf --split-pages=3 input.pdf output_group_%02d.pdf

# Split by page ranges
qpdf input.pdf --pages . 1-5 -- pages_1_to_5.pdf
qpdf input.pdf --pages . 6-10 -- pages_6_to_10.pdf
```

**Python:**
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")

# Split each page into separate file
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)

    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

### Rotate Pages

**CLI:**
```bash
# Rotate first page 90 degrees clockwise
qpdf input.pdf output.pdf --rotate=+90:1

# Rotate all pages 180 degrees
qpdf input.pdf output.pdf --rotate=180:1-z

# Rotate pages 2-5 counterclockwise
qpdf input.pdf output.pdf --rotate=-90:2-5
```

**Python:**
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.rotate(90)  # Rotate 90 degrees clockwise
    writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### Encrypt/Decrypt PDFs

**CLI:**
```bash
# Encrypt with password
qpdf --encrypt user_password owner_password 256 -- input.pdf encrypted.pdf

# Encrypt with permissions (no printing, no modification)
qpdf --encrypt user_pw owner_pw 256 --print=none --modify=none -- input.pdf secure.pdf

# Decrypt (requires password)
qpdf --password=secret123 --decrypt encrypted.pdf decrypted.pdf

# Check encryption status
qpdf --show-encryption encrypted.pdf
```

**Python:**
```python
from pypdf import PdfReader, PdfWriter

# Encrypt
reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password protection
writer.encrypt(user_password="userpass", owner_password="ownerpass")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)

# Decrypt
reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    reader.decrypt("userpass")

# Now you can read the content
text = reader.pages[0].extract_text()
```

### Add Watermark

**Python:**
```python
from pypdf import PdfReader, PdfWriter

# Create or load watermark PDF
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Optimize/Compress PDFs

**CLI (best compression):**
```bash
# Method 1: qpdf optimization
qpdf --optimize-level=all input.pdf optimized.pdf

# Method 2: Ghostscript (aggressive compression)
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf input.pdf

# PDF settings options:
# /screen   - Low resolution (72 dpi), smallest size
# /ebook    - Medium resolution (150 dpi)
# /printer  - High resolution (300 dpi)
# /prepress - High quality (300 dpi, color preserved)
```

---

## Part 4: PDF Forms

### Understanding PDF Forms

**Two types of forms:**

1. **Fillable forms**: Have actual form fields defined in PDF structure
   - Text fields, checkboxes, radio buttons, dropdowns
   - Can be filled programmatically or in PDF readers
   - Data can be extracted back out

2. **Non-fillable forms**: Visual representation only
   - Lines, boxes drawn on page (not interactive)
   - Must add text annotations to fill
   - Common in older/scanned documents

**Check if PDF has fillable fields:**
```bash
python scripts/check_fillable_fields.py document.pdf
```

### Fillable Forms Workflow

**Step 1: Extract field information**
```bash
python scripts/extract_form_field_info.py input.pdf field_info.json
```

**Output (field_info.json):**
```json
[
  {
    "field_id": "last_name",
    "page": 1,
    "rect": [100, 500, 300, 520],
    "type": "text"
  },
  {
    "field_id": "checkbox_citizen",
    "page": 1,
    "type": "checkbox",
    "checked_value": "/On",
    "unchecked_value": "/Off"
  },
  {
    "field_id": "country_select",
    "page": 2,
    "type": "choice",
    "choice_options": [
      {"value": "USA", "text": "United States"},
      {"value": "CAN", "text": "Canada"}
    ]
  }
]
```

**Step 2: Create field values**
```json
[
  {
    "field_id": "last_name",
    "description": "User's last name",
    "page": 1,
    "value": "Johnson"
  },
  {
    "field_id": "checkbox_citizen",
    "description": "Check if US citizen",
    "page": 1,
    "value": "/On"
  }
]
```

**Step 3: Fill the form**
```bash
python scripts/fill_fillable_fields.py input.pdf field_values.json output.pdf
```

### Non-Fillable Forms Workflow

**Step 1: Convert to images**
```bash
python scripts/convert_pdf_to_images.py form.pdf images/
```

**Step 2: Analyze and create fields.json**
```json
{
  "pages": [
    {
      "page_number": 1,
      "image_width": 2550,
      "image_height": 3300
    }
  ],
  "form_fields": [
    {
      "page_number": 1,
      "description": "User's last name",
      "field_label": "Last Name:",
      "label_bounding_box": [100, 200, 200, 220],
      "entry_bounding_box": [210, 200, 400, 220],
      "entry_text": {
        "text": "Johnson",
        "font_size": 12,
        "font_color": "000000"
      }
    },
    {
      "page_number": 1,
      "description": "Checkbox for yes",
      "field_label": "Yes",
      "label_bounding_box": [100, 300, 140, 320],
      "entry_bounding_box": [145, 300, 165, 320],
      "entry_text": {
        "text": "X"
      }
    }
  ]
}
```

**Step 3: Validate bounding boxes**
```bash
# Create validation images
python scripts/create_validation_image.py 1 fields.json images/page-1.png validation-1.png

# Check for intersections
python scripts/check_bounding_boxes.py fields.json
```

**Step 4: Fill the form**
```bash
python scripts/fill_pdf_form_with_annotations.py input.pdf fields.json output.pdf
```

---

## Part 5: PDF Internals

### PDF Object Structure

**Mental Model**: PDF = Tree of objects

```
Catalog (Root)
├── Pages (Page Tree)
│   ├── Page 1
│   │   ├── Contents (Stream with drawing instructions)
│   │   ├── Resources
│   │   │   ├── Fonts
│   │   │   └── Images
│   │   └── MediaBox [0 0 612 792]
│   └── Page 2
├── Metadata
└── Outlines (Bookmarks)
```

**Inspect PDF structure:**
```bash
# Show all objects
qpdf --show-object=all input.pdf

# Show specific object (e.g., object 5)
qpdf --show-object=5 input.pdf

# Show page structure
qpdf --show-pages input.pdf
```

**PDF object types:**
- **Name**: `/Type /Page`
- **Number**: `42` or `3.14`
- **String**: `(Hello)` or `<48656C6C6F>` (hex)
- **Array**: `[1 2 3]`
- **Dictionary**: `<< /Type /Page /MediaBox [0 0 612 792] >>`
- **Stream**: Compressed binary data (images, fonts, content)
- **Reference**: `5 0 R` (points to object 5)

### Content Streams

**What are content streams?**
- Instructions for drawing a page
- Postscript-like language
- Compressed with Flate (zlib)

**Example content stream:**
```
BT                    % Begin Text
/F1 12 Tf             % Set Font F1 at 12pt
100 700 Td            % Move to position (100, 700)
(Hello, World!) Tj    % Show text
ET                    % End Text

q                     % Save graphics state
1 0 0 1 50 50 cm      % Translate to (50, 50)
200 0 0 200 0 0 cm    % Scale
/Im1 Do               % Draw image Im1
Q                     % Restore graphics state
```

**Extract raw content stream:**
```bash
qpdf --show-object=5 --filtered-stream-data input.pdf
```

### Fonts in PDFs

**Font types:**
1. **Type 1**: PostScript fonts (legacy)
2. **TrueType**: Standard fonts (.ttf)
3. **Type 3**: User-defined fonts
4. **CID Fonts**: For CJK languages (Chinese, Japanese, Korean)

**Font embedding:**
- **Embedded**: Font data included in PDF → Perfect rendering everywhere
- **Not embedded**: References system fonts → May look different on other systems

**Why embed fonts?**
- **Portability**: Document looks identical everywhere
- **Legal compliance**: Some fonts require embedding license
- **File size**: Trade-off between size and consistency

**Check font embedding:**
```bash
pdffonts document.pdf
```

**Output:**
```
name                                 type              embedded
ABCDEE+Arial                         TrueType          yes
Times-Roman                          Type 1            no
```

### Compression in PDFs

**Stream compression methods:**
- **FlateDecode**: zlib/deflate (most common)
- **DCTDecode**: JPEG compression (for images)
- **CCITTFaxDecode**: Fax compression (B&W images)
- **LZWDecode**: LZW compression (legacy)

**Object-level compression (PDF 1.5+):**
- Multiple objects compressed together
- Reduces file size significantly

**Decompress streams:**
```bash
# Extract uncompressed streams
qpdf --qdf --object-streams=disable input.pdf uncompressed.pdf
```

### Cross-Reference Table (xref)

**What is xref?**
- Index of all objects in PDF
- Maps object number → byte offset in file
- Allows random access to any object

**Traditional xref:**
```
xref
0 6
0000000000 65535 f
0000000015 00000 n
0000000074 00000 n
0000000182 00000 n
0000000251 00000 n
0000000512 00000 n
```

**Compressed xref (PDF 1.5+):**
- Cross-reference stream object
- Saves space in large PDFs

---

## Part 6: Advanced Techniques

### Extract Text with Coordinates

**Why coordinates matter?**
- Extract text from specific regions (e.g., header, footer)
- Build structured data from unstructured PDFs
- Detect text alignment (left, right, center)

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    # Get all characters with coordinates
    chars = page.chars
    for char in chars[:20]:  # First 20 characters
        print(f"'{char['text']}' at x={char['x0']:.1f}, y={char['y0']:.1f}")

    # Extract text from bounding box (left, top, right, bottom)
    # Note: y=0 is at TOP of page in pdfplumber
    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
    print(f"Text in box: {bbox_text}")
```

### Batch Processing with Error Handling

```python
import os
import glob
from pypdf import PdfReader, PdfWriter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_all_pdfs(directory):
    """Merge all PDFs in directory with error handling."""
    pdf_files = sorted(glob.glob(os.path.join(directory, "*.pdf")))

    writer = PdfWriter()

    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)

            # Check if encrypted
            if reader.is_encrypted:
                logger.warning(f"Skipping encrypted file: {pdf_file}")
                continue

            # Add all pages
            for page in reader.pages:
                writer.add_page(page)

            logger.info(f"✓ Processed: {pdf_file}")

        except Exception as e:
            logger.error(f"✗ Failed: {pdf_file} - {e}")
            continue

    # Save merged PDF
    output_path = os.path.join(directory, "merged_all.pdf")
    with open(output_path, "wb") as output:
        writer.write(output)

    logger.info(f"✓ Saved merged PDF: {output_path}")

# Usage
merge_all_pdfs("/path/to/pdfs")
```

### PDF Cropping

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

# Get first page
page = reader.pages[0]

# Original mediabox
print(f"Original: {page.mediabox}")

# Crop (left, bottom, right, top) in points
page.mediabox.left = 50
page.mediabox.bottom = 50
page.mediabox.right = 550
page.mediabox.top = 750

print(f"Cropped: {page.mediabox}")

writer.add_page(page)

with open("cropped.pdf", "wb") as output:
    writer.write(output)
```

### Rendering PDFs to Images (High Quality)

```python
import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument("document.pdf")

for i, page in enumerate(pdf):
    # High resolution (300 DPI equivalent)
    bitmap = page.render(scale=300/72, rotation=0)

    # Convert to PIL Image
    img = bitmap.to_pil()

    # Save as PNG (lossless)
    img.save(f"page_{i+1}_high_res.png", "PNG")

    # Save as JPEG (compressed)
    img.save(f"page_{i+1}.jpg", "JPEG", quality=95, optimize=True)
```

---

## Part 7: Command-Line Tools Reference

### pdftotext (poppler-utils)

```bash
# Basic text extraction
pdftotext document.pdf output.txt

# Preserve layout (column-aware)
pdftotext -layout document.pdf output.txt

# Extract specific pages (1-based)
pdftotext -f 5 -l 10 document.pdf output.txt

# Extract with bounding box info (XML output)
pdftotext -bbox-layout document.pdf output.xml

# Fixed width (for alignment)
pdftotext -fixed 80 document.pdf output.txt

# Extract to stdout
pdftotext document.pdf -
```

### pdftoppm (poppler-utils)

```bash
# Convert to PNG images
pdftoppm -png -r 150 document.pdf page

# High resolution JPEG
pdftoppm -jpeg -jpegopt quality=95 -r 300 document.pdf page

# Specific pages only
pdftoppm -png -r 150 -f 1 -l 5 document.pdf page

# Scale output (50% size)
pdftoppm -png -scale-to 612 document.pdf page

# Grayscale output
pdftoppm -gray -r 150 document.pdf page
```

### pdfimages (poppler-utils)

```bash
# Extract all images (original format)
pdfimages -all document.pdf images/img

# Extract as JPEG only
pdfimages -j document.pdf images/img

# Include page numbers in filename
pdfimages -p document.pdf images/page

# List images without extracting
pdfimages -list document.pdf
```

### qpdf

```bash
# Optimize PDF
qpdf --optimize-level=all input.pdf optimized.pdf

# Linearize (for web streaming)
qpdf --linearize input.pdf web_optimized.pdf

# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages_1_to_5.pdf
qpdf input.pdf --pages . 6-z -- pages_6_to_end.pdf

# Extract specific pages from multiple PDFs
qpdf --empty --pages doc1.pdf 1-3 doc2.pdf 5,7,9 -- combined.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1
qpdf input.pdf output.pdf --rotate=180:1-z

# Encrypt
qpdf --encrypt user_pw owner_pw 256 -- input.pdf encrypted.pdf

# Decrypt
qpdf --password=secret --decrypt encrypted.pdf decrypted.pdf

# Check PDF structure
qpdf --check input.pdf

# Show detailed structure
qpdf --show-object=all input.pdf > structure.txt

# Fix corrupted PDF
qpdf --replace-input damaged.pdf
```

### pdfinfo (poppler-utils)

```bash
# Show metadata
pdfinfo document.pdf

# Output:
# Title:          Report 2025
# Author:         John Doe
# Creator:        Microsoft Word
# Producer:       Adobe PDF Library
# CreationDate:   Mon Jan 15 10:30:00 2025
# Pages:          25
# Encrypted:      no
# Page size:      612 x 792 pts (letter)
# File size:      2.5 MB
```

### Ghostscript (gs)

```bash
# Compress PDF
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH -sOutputFile=compressed.pdf input.pdf

# Convert PDF to images (all pages)
gs -dNOPAUSE -dBATCH -sDEVICE=png16m -r300 \
   -sOutputFile=page_%03d.png input.pdf

# Convert specific pages
gs -dFirstPage=1 -dLastPage=5 -sDEVICE=jpeg -r150 \
   -sOutputFile=page_%d.jpg input.pdf

# Merge PDFs
gs -dNOPAUSE -sDEVICE=pdfwrite -sOutputFile=merged.pdf -dBATCH \
   file1.pdf file2.pdf file3.pdf
```

---

## Part 8: Real-World Use Cases

### Use Case 1: Extract Invoice Data to CSV

```python
import pdfplumber
import pandas as pd
import re

def extract_invoice_data(pdf_path):
    """Extract invoice line items to CSV."""
    with pdfplumber.open(pdf_path) as pdf:
        all_tables = []

        for page in pdf.pages:
            # Extract tables
            tables = page.extract_tables()

            for table in tables:
                # Convert to DataFrame
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

        # Combine and save
        if all_tables:
            result = pd.concat(all_tables, ignore_index=True)
            result.to_csv("invoice_data.csv", index=False)
            return result

# Usage
df = extract_invoice_data("invoice.pdf")
print(df.head())
```

### Use Case 2: Batch Convert Documents to PDF/A (Archive Format)

```bash
#!/bin/bash
# Convert all PDFs to PDF/A format (ISO 19005)

for file in *.pdf; do
    output="${file%.pdf}_pdfa.pdf"

    gs -dPDFA=1 -dBATCH -dNOPAUSE -dNOOUTERSAVE \
       -sProcessColorModel=DeviceRGB -sDEVICE=pdfwrite \
       -sOutputFile="$output" "$file"

    echo "✓ Converted: $file -> $output"
done
```

### Use Case 3: Generate Reports from Data

```python
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas as pd

def generate_sales_report(data_csv, output_pdf):
    """Generate PDF report from CSV data."""
    # Load data
    df = pd.read_csv(data_csv)

    # Create PDF
    doc = SimpleDocTemplate(output_pdf)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph("Monthly Sales Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.5*inch))

    # Summary stats
    summary = f"Total Sales: ${df['Amount'].sum():,.2f}"
    story.append(Paragraph(summary, styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))

    # Convert DataFrame to list for table
    table_data = [df.columns.tolist()] + df.values.tolist()

    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)

    # Build PDF
    doc.build(story)

# Usage
generate_sales_report("sales_data.csv", "sales_report.pdf")
```

### Use Case 4: Redact Sensitive Information

```python
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def create_redaction_overlay(page_size, redaction_boxes):
    """Create overlay with black rectangles for redaction."""
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)

    # Draw black rectangles
    can.setFillColorRGB(0, 0, 0)
    for box in redaction_boxes:
        # box = (x, y, width, height)
        can.rect(box[0], box[1], box[2], box[3], fill=1)

    can.save()
    packet.seek(0)
    return packet

def redact_pdf(input_pdf, output_pdf, redaction_boxes):
    """Apply redaction to PDF."""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Get page size
    page = reader.pages[0]
    page_size = (page.mediabox.width, page.mediabox.height)

    # Create redaction overlay
    overlay_pdf = create_redaction_overlay(page_size, redaction_boxes)
    overlay = PdfReader(overlay_pdf).pages[0]

    # Apply to all pages
    for page in reader.pages:
        page.merge_page(overlay)
        writer.add_page(page)

    with open(output_pdf, "wb") as output:
        writer.write(output)

# Usage: Redact SSN at specific location
redaction_boxes = [
    (100, 500, 200, 20),  # (x, y, width, height)
]
redact_pdf("document.pdf", "redacted.pdf", redaction_boxes)
```

---

## Part 9: Performance Optimization

### For Large PDFs (100+ MB)

**Problem**: Loading entire PDF consumes too much memory.

**Solutions:**
```python
# 1. Process pages individually
from pypdf import PdfReader

reader = PdfReader("large.pdf")
for i, page in enumerate(reader.pages):
    # Process one page at a time
    text = page.extract_text()
    # Save or process immediately
    with open(f"page_{i+1}.txt", "w") as f:
        f.write(text)

# 2. Use qpdf to split first
# Split into chunks of 10 pages
# qpdf --split-pages=10 large.pdf chunk.pdf

# 3. Stream processing (CLI)
# Extract text without loading full PDF
# pdftotext large.pdf - | head -100
```

### For Text Extraction Speed

**Benchmark (1000 page PDF):**
- `pdftotext`: **3 seconds** ⭐ Fastest
- `pdfplumber`: 45 seconds (structured data extraction)
- `pypdf`: 60 seconds (basic extraction)

**Recommendation:**
- Use `pdftotext` for plain text
- Use `pdfplumber` only when you need tables/coordinates
- Avoid `pypdf.extract_text()` for large documents

### For Image Extraction

**Fastest method:**
```bash
# Direct extraction (original quality, no re-encoding)
pdfimages -all document.pdf images/img
# 10x faster than rendering pages
```

**When to render pages:**
- When images are embedded in graphics
- When you need specific DPI
- When combining multiple elements into one image

---

## Part 10: Troubleshooting

### Problem: Can't Extract Text (Scanned PDF)

**Diagnosis:**
```bash
pdftotext test.pdf -
# If empty or garbage → scanned PDF
```

**Solution: OCR**
```python
import pytesseract
from pdf2image import convert_from_path

images = convert_from_path("scanned.pdf", dpi=300)
text = ""
for image in images:
    text += pytesseract.image_to_string(image)

with open("ocr_output.txt", "w") as f:
    f.write(text)
```

### Problem: PDF is Encrypted

**Diagnosis:**
```bash
qpdf --show-encryption document.pdf
# Output: "File is encrypted"
```

**Solution:**
```python
from pypdf import PdfReader

reader = PdfReader("encrypted.pdf")
if reader.is_encrypted:
    success = reader.decrypt("password")
    if success:
        text = reader.pages[0].extract_text()
    else:
        print("Wrong password")
```

### Problem: PDF is Corrupted

**Diagnosis:**
```bash
qpdf --check corrupted.pdf
# Output: "warning: file is damaged"
```

**Solutions:**
```bash
# Method 1: qpdf repair
qpdf --replace-input corrupted.pdf

# Method 2: Ghostscript reprocessing
gs -o repaired.pdf -sDEVICE=pdfwrite corrupted.pdf

# Method 3: Convert to images and back to PDF
pdftoppm -png corrupted.pdf page
convert page-*.png recovered.pdf  # ImageMagick
```

### Problem: Fonts Not Embedded

**Check:**
```bash
pdffonts document.pdf
# Look for "no" in embedded column
```

**Why it matters:**
- Document may look different on other systems
- Text extraction might fail
- Printing issues

**Solution: Re-create with embedded fonts**
```bash
gs -dNOPAUSE -dBATCH -sDEVICE=pdfwrite \
   -dEmbedAllFonts=true \
   -sOutputFile=embedded.pdf input.pdf
```

### Problem: File Size Too Large

**Diagnosis:**
```bash
pdfinfo document.pdf
# Check: File size: 50 MB
```

**Solutions:**
```bash
# Method 1: qpdf optimize
qpdf --optimize-level=all large.pdf optimized.pdf

# Method 2: Ghostscript compression
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=compressed.pdf large.pdf

# Method 3: Remove embedded images (if acceptable)
gs -sDEVICE=pdfwrite -dPDFSETTINGS=/screen \
   -sOutputFile=small.pdf large.pdf
```

---

## Quick Reference

| **Task** | **Command/Code** |
|----------|------------------|
| Extract text | `pdftotext -layout doc.pdf output.txt` |
| Extract tables | `pdfplumber` (Python) |
| Extract images | `pdfimages -all doc.pdf img` |
| Convert to images | `pdftoppm -png -r 150 doc.pdf page` |
| Merge PDFs | `qpdf --empty --pages *.pdf -- merged.pdf` |
| Split pages | `qpdf doc.pdf --pages . 1-5 -- split.pdf` |
| Rotate | `qpdf doc.pdf out.pdf --rotate=+90:1` |
| Encrypt | `qpdf --encrypt pass pass 256 -- in.pdf out.pdf` |
| Decrypt | `qpdf --password=pass --decrypt in.pdf out.pdf` |
| Optimize | `qpdf --optimize-level=all in.pdf out.pdf` |
| Compress | `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/ebook in.pdf out.pdf` |
| Get metadata | `pdfinfo doc.pdf` |
| Check structure | `qpdf --check doc.pdf` |
| OCR scanned PDF | `pytesseract` + `pdf2image` (Python) |

---

## Summary: The Three Mental Models

1. **PDF = Page-Description Language** → Instructions for drawing, not structured data
2. **PDF = Tree of Objects** → Catalog → Pages → Content streams + Resources
3. **Embedded vs Referenced** → Fonts/images embedded = portable, no dependencies

**Choose your tool:**
- **Creating?** → `reportlab` (Python) or `pdf-lib` (JavaScript)
- **Reading text?** → `pdftotext` (CLI) or `pdfplumber` (Python)
- **Manipulating?** → `qpdf` (CLI) or `pypdf` (Python)
- **Forms?** → Python scripts + field extraction
- **Converting?** → `pdftoppm` or `pypdfium2`

---

**Recommended Reading:**

Now that you understand PDFs, read the downloaded books:
- **PDF Explained** (Whitington) - Deep dive into PDF structure
- **Developing with PDF** (Rosenthol) - Practical development guide

**Next steps:**
- Explore the `scripts/` directory in the PDF skill for ready-to-use tools
- Try form filling workflow with a real PDF
- Experiment with creating professional reports using reportlab
