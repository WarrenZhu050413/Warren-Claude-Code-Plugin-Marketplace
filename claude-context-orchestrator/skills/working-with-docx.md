# Working with DOCX Files: A Comprehensive Guide

## Mental Model: DOCX is a ZIP Archive of XML

**🧠 Core Concept**: A .docx file isn't actually a "document" - it's a **ZIP file containing XML files** that describe your document.

```bash
# Prove it: Rename and unzip any .docx file
cp document.docx document.zip
unzip -q document.zip -d unpacked
tree unpacked
```

**What you'll see:**
```
unpacked/
├── [Content_Types].xml      # Tells Office what file types are inside
├── _rels/                   # Relationships between files
│   └── .rels
└── word/
    ├── document.xml         # ⭐ YOUR ACTUAL DOCUMENT CONTENT
    ├── styles.xml           # Font styles, heading styles, etc.
    ├── numbering.xml        # List numbering definitions
    ├── comments.xml         # Comments and tracked changes
    ├── media/               # Embedded images
    │   └── image1.png
    └── _rels/
        └── document.xml.rels  # Links to images, hyperlinks
```

**This means:**
- No proprietary binary format - it's all text-based XML
- You can edit Word documents with text tools (grep, sed, Python)
- Understanding XML structure = understanding Word documents
- But: XML is verbose and easy to break if you're not careful

---

## The DOCX Ecosystem: Choose Your Tool

| **Task** | **Best Tool** | **Why** |
|----------|---------------|---------|
| Create new document | `docx` (JavaScript) | Clean API, modern, well-documented |
| Read text only | `pandoc` | Preserves structure, shows tracked changes |
| Edit existing document | Python + OOXML library | Direct XML access, handles complexity |
| Track changes (redlining) | Python + Document class | Auto-handles infrastructure |
| Extract images | `unzip` + file operations | Direct access to media folder |
| Convert to PDF | `soffice` (LibreOffice) | Headless conversion |
| CLI inspection | `pandoc`, `xmllint` | Quick text extraction, validation |

---

## Part 1: Reading DOCX Files

### Quick Text Extraction

**Use Case**: You just need to read the text, maybe preserve headings/lists.

```bash
# Basic text extraction (fastest)
pandoc document.docx -o output.md

# Preserve tracked changes
pandoc --track-changes=all document.docx -o review.md
# Options: accept (show final), reject (show original), all (show markup)

# Just print to stdout
pandoc document.docx -t plain
```

**When to use**:
- Converting docs to markdown for version control
- Extracting text for analysis
- Reviewing tracked changes in readable format

### Inspecting the XML Structure

**Use Case**: You need to understand the document structure, find specific elements, or debug XML issues.

```bash
# Unpack the document
python ooxml/scripts/unpack.py document.docx unpacked/

# View main content (formatted for readability)
xmllint --format unpacked/word/document.xml | less

# Search for specific text
grep -n "contract term" unpacked/word/document.xml

# Search for tracked changes
grep -n "<w:ins" unpacked/word/document.xml  # Insertions
grep -n "<w:del" unpacked/word/document.xml  # Deletions

# Find all headings
grep "<w:pStyle w:val=\"Heading" unpacked/word/document.xml
```

**When to use**:
- Before editing: understand document structure
- Debugging: why isn't my edit working?
- Learning: see how Word represents different elements

### Extracting Images

**Use Case**: Get all images from a document.

```bash
# Method 1: Direct extraction (fastest)
unzip -j document.docx word/media/* -d images/

# Method 2: Using pdfimages (requires PDF conversion first)
soffice --headless --convert-to pdf document.docx
pdfimages -j document.pdf image
# Creates: image-000.jpg, image-001.jpg, etc.
```

### Understanding Document Structure with Examples

**Paragraph with text:**
```xml
<w:p>
  <w:r><w:t>This is a simple paragraph.</w:t></w:r>
</w:p>
```
- `<w:p>` = paragraph
- `<w:r>` = run (contiguous text with same formatting)
- `<w:t>` = text content

**Why multiple `<w:r>` elements?** Each formatting change creates a new run:
```xml
<w:p>
  <w:r><w:t>Normal text </w:t></w:r>
  <w:r><w:rPr><w:b/></w:rPr><w:t>bold text</w:t></w:r>
  <w:r><w:t> back to normal</w:t></w:r>
</w:p>
```

**Heading:**
```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="Heading1"/>  <!-- References style in styles.xml -->
  </w:pPr>
  <w:r><w:t>Chapter 1: Introduction</w:t></w:r>
</w:p>
```

**Numbered list item:**
```xml
<w:p>
  <w:pPr>
    <w:pStyle w:val="ListParagraph"/>
    <w:numPr>
      <w:ilvl w:val="0"/>     <!-- Level 0 = top level -->
      <w:numId w:val="1"/>    <!-- Which numbering definition to use -->
    </w:numPr>
  </w:pPr>
  <w:r><w:t>First item</w:t></w:r>
</w:p>
```

**Key insight**: Different `numId` = independent lists (both restart at 1). Same `numId` = continues numbering.

---

## Part 2: Creating New DOCX Documents

### JavaScript (docx library) - Recommended for New Documents

**Mental Model**: Build documents like React components - compose `Paragraph`, `TextRun`, `Table` elements.

**Installation:**
```bash
npm install -g docx
```

**Minimal Example:**
```javascript
const { Document, Packer, Paragraph, TextRun } = require('docx');
const fs = require('fs');

const doc = new Document({
  sections: [{
    children: [
      new Paragraph({
        children: [new TextRun("Hello, World!")]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("document.docx", buffer);
});
```

**Professional Document with Styles:**
```javascript
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = require('docx');
const fs = require('fs');

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: "Arial", size: 24 } }  // 12pt default
    },
    paragraphStyles: [
      {
        id: "Heading1",
        name: "Heading 1",
        basedOn: "Normal",
        run: { size: 32, bold: true, color: "000000" },  // 16pt
        paragraph: {
          spacing: { before: 240, after: 240 },
          outlineLevel: 0  // Required for table of contents
        }
      }
    ]
  },
  sections: [{
    properties: {
      page: {
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }  // 1" margins
      }
    },
    children: [
      new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun("Introduction")]
      }),
      new Paragraph({
        children: [new TextRun("This is the content of the document.")]
      })
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => fs.writeFileSync("professional.docx", buffer));
```

**CRITICAL: Common Mistakes**
```javascript
// ❌ WRONG: Using \n for line breaks
new Paragraph({ children: [new TextRun("Line 1\nLine 2")] })

// ✅ CORRECT: Separate paragraphs
new Paragraph({ children: [new TextRun("Line 1")] }),
new Paragraph({ children: [new TextRun("Line 2")] })

// ❌ WRONG: Unicode bullets
new TextRun("• Item 1")

// ✅ CORRECT: Proper numbering config
const doc = new Document({
  numbering: {
    config: [{
      reference: "bullet-list",
      levels: [{
        level: 0,
        format: LevelFormat.BULLET,
        text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } }
      }]
    }]
  },
  sections: [{
    children: [
      new Paragraph({
        numbering: { reference: "bullet-list", level: 0 },
        children: [new TextRun("Item 1")]
      })
    ]
  }]
});
```

**Tables with Proper Formatting:**
```javascript
const { Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType, VerticalAlign } = require('docx');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const cellBorders = { top: border, bottom: border, left: border, right: border };

new Table({
  columnWidths: [4680, 4680],  // DXA units (1440 = 1 inch)
  margins: { top: 100, bottom: 100, left: 180, right: 180 },
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },  // ALWAYS use CLEAR
          verticalAlign: VerticalAlign.CENTER,
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "Column 1", bold: true })]
          })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          shading: { fill: "D5E8F0", type: ShadingType.CLEAR },
          children: [new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "Column 2", bold: true })]
          })]
        })
      ]
    }),
    new TableRow({
      children: [
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          children: [new Paragraph({ children: [new TextRun("Data 1")] })]
        }),
        new TableCell({
          borders: cellBorders,
          width: { size: 4680, type: WidthType.DXA },
          children: [new Paragraph({ children: [new TextRun("Data 2")] })]
        })
      ]
    })
  ]
})
```

**Adding Images:**
```javascript
const { ImageRun } = require('docx');
const fs = require('fs');

new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: "png",  // REQUIRED: must specify type
    data: fs.readFileSync("logo.png"),
    transformation: { width: 200, height: 150 },
    altText: {
      title: "Company Logo",
      description: "Logo for Acme Corp",
      name: "Logo"
    }
  })]
})
```

---

## Part 3: Editing Existing DOCX Documents

### Python + OOXML Library - For Complex Edits

**Mental Model**: Unpack → Modify XML → Repack

**Workflow:**
```bash
# 1. Unpack
python ooxml/scripts/unpack.py original.docx unpacked/

# 2. Edit (with Python script - see below)
PYTHONPATH=/path/to/docx/skill python edit_script.py

# 3. Repack
python ooxml/scripts/pack.py unpacked/ modified.docx
```

**Basic Edit Script:**
```python
from scripts.document import Document

# Initialize (creates temp copy, auto-setup infrastructure)
doc = Document('unpacked')

# Find and replace text
node = doc["word/document.xml"].get_node(tag="w:r", contains="old text")
doc["word/document.xml"].replace_node(
    node,
    '<w:r><w:t>new text</w:t></w:r>'
)

# Save
doc.save()  # Copies back to 'unpacked', validates XML
```

**Finding Nodes (Multiple Methods):**
```python
# By text content
node = doc["word/document.xml"].get_node(tag="w:p", contains="Introduction")

# By line number (useful after grepping)
node = doc["word/document.xml"].get_node(tag="w:p", line_number=42)

# By line range (when text appears multiple times)
node = doc["word/document.xml"].get_node(
    tag="w:r",
    contains="Section",
    line_number=range(100, 200)
)

# By attributes (e.g., specific tracked change)
node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "5"})
```

**Complex Example: Adding a Heading**
```python
from scripts.document import Document

doc = Document('unpacked')

# Find where to insert (after a specific paragraph)
target = doc["word/document.xml"].get_node(tag="w:p", contains="End of intro")

# Insert new heading
doc["word/document.xml"].insert_after(
    target,
    '''<w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>New Section</w:t></w:r>
    </w:p>'''
)

doc.save()
```

---

## Part 4: Tracked Changes (Redlining)

**Mental Model**: Track changes = wrapping text in `<w:ins>` (insertion) or `<w:del>` (deletion) tags.

**Workflow:**
```bash
# 1. Get readable version with changes marked
pandoc --track-changes=all document.docx -o current.md

# 2. Review what needs changing
# 3. Unpack document
python ooxml/scripts/unpack.py document.docx unpacked/

# 4. Implement tracked changes (Python)
PYTHONPATH=/path/to/docx/skill python redline.py

# 5. Repack
python ooxml/scripts/pack.py unpacked/ reviewed.docx

# 6. Verify
pandoc --track-changes=all reviewed.docx -o verification.md
```

**Simple Tracked Change:**
```python
from scripts.document import Document

doc = Document('unpacked', track_revisions=True)

# Change "30 days" to "45 days" - MINIMAL EDIT
node = doc["word/document.xml"].get_node(tag="w:r", contains="within 30 days")

# Extract formatting from original
rpr = ""
tags = node.getElementsByTagName("w:rPr")
if tags:
    rpr = tags[0].toxml()

# Only mark what actually changed
replacement = f'''
<w:r w:rsidR="00AB12CD">{rpr}<w:t>within </w:t></w:r>
<w:del><w:r>{rpr}<w:delText>30</w:delText></w:r></w:del>
<w:ins><w:r>{rpr}<w:t>45</w:t></w:r></w:ins>
<w:r w:rsidR="00AB12CD">{rpr}<w:t> days</w:t></w:r>
'''

doc["word/document.xml"].replace_node(node, replacement)
doc.save()
```

**CRITICAL PRINCIPLE: Minimal Edits**
```python
# ❌ WRONG: Replacing entire sentence
'<w:del><w:r><w:delText>The contract term is 30 days.</w:delText></w:r></w:del>' +
'<w:ins><w:r><w:t>The contract term is 45 days.</w:t></w:r></w:ins>'

# ✅ CORRECT: Only mark what changed
'<w:r w:rsidR="00AB"><w:t>The contract term is </w:t></w:r>' +
'<w:del><w:r><w:delText>30</w:delText></w:r></w:del>' +
'<w:ins><w:r><w:t>45</w:t></w:r></w:ins>' +
'<w:r w:rsidR="00AB"><w:t> days.</w:t></w:r>'
```

**Adding Comments:**
```python
# Add comment on a tracked change
doc = Document('unpacked')

start_node = doc["word/document.xml"].get_node(tag="w:del", attrs={"w:id": "1"})
end_node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "2"})

doc.add_comment(
    start=start_node,
    end=end_node,
    text="Changed to align with new policy"
)

doc.save()
```

---

## Part 5: Common Pitfalls and How to Avoid Them

### 1. Text Split Across Multiple `<w:r>` Elements

**Problem**: You search for "Hello World" but it's stored as:
```xml
<w:r><w:t>Hello </w:t></w:r>
<w:r><w:t>World</w:t></w:r>
```

**Solution**: Always grep the XML first to see actual structure.
```bash
grep -A 2 -B 2 "Hello" unpacked/word/document.xml
```

### 2. Invalid XML After Editing

**Problem**: Missing closing tags, wrong element nesting.

**Prevention**:
- Always use `doc.save()` which validates by default
- Test with a copy first
- Use `xmllint --noout unpacked/word/document.xml` to validate

### 3. Corrupted Documents After Editing

**Symptoms**: Word says "file is corrupted" or shows repair dialog.

**Common causes:**
- Forgot to update `[Content_Types].xml` after adding images
- Forgot to update `word/_rels/document.xml.rels` for relationships
- Invalid XML structure (e.g., PageBreak outside Paragraph)

**Fix**:
- Use the Document library - it handles infrastructure automatically
- For manual edits, check both files after adding images/hyperlinks

### 4. Tracked Changes Not Showing

**Problem**: Added `<w:ins>`/`<w:del>` tags but changes don't appear in Word.

**Causes**:
- `<w:trackRevisions/>` not enabled in `word/settings.xml`
- Missing required attributes (w:id, w:author, w:date)
- RSID values not in hex format

**Fix**: Use `Document('unpacked', track_revisions=True)` - handles all of this.

### 5. Lists Not Working

**Problem**: Bullets show as plain text or numbering doesn't restart.

**Cause**: Different `numId` values = independent lists.

**Solution**:
- Same `numId` = continues from previous (1, 2, 3... then 4, 5, 6...)
- Different `numId` = restarts at 1 (1, 2, 3... then 1, 2, 3...)

### 6. Images Don't Display or Page Overflows

**Problem**: Image appears as placeholder or pushes content off page.

**Fix**: Calculate dimensions to fit page width (6.5" usable with 1" margins):
```python
from PIL import Image

img = Image.open('image.png')
width_emus = int(6.5 * 914400)  # 6.5" in EMUs (914400 EMUs per inch)
height_emus = int(width_emus * img.size[1] / img.size[0])  # Maintain aspect ratio
```

---

## Part 6: Command-Line Tools Reference

### pandoc
```bash
# Convert to markdown
pandoc document.docx -o output.md

# Convert to plain text
pandoc document.docx -t plain

# Show tracked changes
pandoc --track-changes=all document.docx -o review.md
pandoc --track-changes=accept document.docx -o final.md
pandoc --track-changes=reject document.docx -o original.md

# Extract specific sections (if using headers)
pandoc document.docx --extract-media=media/ -o output.md
```

### soffice (LibreOffice)
```bash
# Convert to PDF
soffice --headless --convert-to pdf document.docx

# Convert to HTML
soffice --headless --convert-to html document.docx

# Batch convert all DOCX in directory
soffice --headless --convert-to pdf *.docx
```

### xmllint
```bash
# Validate XML
xmllint --noout unpacked/word/document.xml

# Format XML for readability
xmllint --format unpacked/word/document.xml > formatted.xml

# Extract specific elements
xmllint --xpath "//w:p[w:pPr/w:pStyle[@w:val='Heading1']]" unpacked/word/document.xml
```

### unzip
```bash
# Extract all files
unzip document.docx -d unpacked/

# Extract only XML files (no images)
unzip document.docx '*.xml' -d unpacked/

# Extract only images
unzip -j document.docx 'word/media/*' -d images/

# List contents without extracting
unzip -l document.docx
```

---

## Part 7: Office Open XML (OOXML) Internals

### File Structure Explained

**`[Content_Types].xml`** - Declares all file types in the archive
```xml
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/word/document.xml"
            ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
```
**When to edit**: Adding new file types (e.g., new image format)

**`_rels/.rels`** - Relationships at package level
```xml
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
              Target="word/document.xml"/>
```
**Purpose**: Tells Office where the main document is

**`word/document.xml`** - Main document content
- Contains all paragraphs, tables, text
- References styles, numbering, images via IDs
- Largest and most important file

**`word/styles.xml`** - Style definitions
```xml
<w:style w:type="paragraph" w:styleId="Heading1">
  <w:name w:val="Heading 1"/>
  <w:basedOn w:val="Normal"/>
  <w:rPr>
    <w:sz w:val="32"/>  <!-- 16pt font size (size in half-points) -->
    <w:b/>              <!-- Bold -->
  </w:rPr>
</w:style>
```
**When to edit**: Creating custom styles, changing default fonts

**`word/numbering.xml`** - List numbering definitions
```xml
<w:num w:numId="1">
  <w:abstractNumId w:val="1"/>
</w:num>
<w:abstractNum w:abstractNumId="1">
  <w:lvl w:ilvl="0">
    <w:start w:val="1"/>
    <w:numFmt w:val="decimal"/>
    <w:lvlText w:val="%1."/>
  </w:lvl>
</w:abstractNum>
```
**Purpose**: Defines how lists are numbered

**`word/_rels/document.xml.rels`** - Document relationships
```xml
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
              Target="media/image1.png"/>
<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
              Target="https://example.com" TargetMode="External"/>
```
**When to edit**: Adding images, hyperlinks

**`word/comments.xml`** - Comments and annotations
```xml
<w:comments>
  <w:comment w:id="0" w:author="John Doe" w:date="2025-10-27T10:00:00Z">
    <w:p><w:r><w:t>This needs revision</w:t></w:r></w:p>
  </w:comment>
</w:comments>
```

**`word/settings.xml`** - Document settings
```xml
<w:settings>
  <w:trackRevisions/>  <!-- Enable tracked changes -->
  <w:defaultTabStop w:val="720"/>  <!-- 0.5" default tab stops -->
</w:settings>
```

### Namespaces Reference

```xml
xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"
xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"
```

**Prefixes:**
- `w:` = WordprocessingML (document content)
- `r:` = Relationships (linking files)
- `wp:` = WordprocessingDrawing (images, shapes)
- `a:` = DrawingML (graphics)
- `pic:` = Picture (image properties)

### Measurements in OOXML

**DXA (twentieths of a point):**
- 1440 DXA = 1 inch = 72 points
- Letter width with 1" margins = 9360 DXA (6.5 inches)

**EMU (English Metric Units):**
- 914400 EMU = 1 inch
- Used for images and shapes

**Half-points:**
- Font sizes in `<w:sz>` use half-points
- `<w:sz w:val="24"/>` = 12pt font

**Conversion reference:**
```
1 inch = 1440 DXA = 914400 EMU = 72 points
12pt font = size 24 (half-points)
1" margin = 1440 DXA
```

---

## Part 8: Real-World Use Cases

### Use Case 1: Batch Converting Documents to PDF

**Scenario**: Convert 100 .docx files to PDF for distribution.

```bash
# LibreOffice headless conversion
for file in *.docx; do
  soffice --headless --convert-to pdf "$file"
done
```

### Use Case 2: Extracting All Tables to Excel

**Scenario**: Extract tables from a report into spreadsheet.

```bash
# Convert to markdown (preserves tables)
pandoc report.docx -o report.md

# Tables in markdown can be imported to Excel or converted with:
pandoc report.md -t xlsx -o tables.xlsx
```

### Use Case 3: Automated Contract Generation

**Scenario**: Generate personalized contracts from template.

```javascript
const { Document, Packer, Paragraph, TextRun } = require('docx');
const fs = require('fs');

function generateContract(clientName, amount, date) {
  const doc = new Document({
    sections: [{
      children: [
        new Paragraph({
          children: [new TextRun({
            text: "SERVICE AGREEMENT",
            bold: true,
            size: 32
          })]
        }),
        new Paragraph({
          children: [new TextRun(`This agreement is made on ${date} between Company and ${clientName}.`)]
        }),
        new Paragraph({
          children: [new TextRun(`Total contract value: $${amount}`)]
        })
      ]
    }]
  });

  return Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync(`contract_${clientName.replace(/\s/g, '_')}.docx`, buffer);
  });
}

// Generate multiple contracts
generateContract("John Doe", "50,000", "2025-10-27");
generateContract("Jane Smith", "75,000", "2025-10-27");
```

### Use Case 4: Legal Document Review with Tracked Changes

**Scenario**: Review and redline a legal agreement.

```python
from scripts.document import Document

doc = Document('unpacked/contract.docx', track_revisions=True)

# Change payment terms
node = doc["word/document.xml"].get_node(tag="w:r", contains="Net 30")
rpr = tags[0].toxml() if (tags := node.getElementsByTagName("w:rPr")) else ""

replacement = f'''
<w:del><w:r>{rpr}<w:delText>Net 30</w:delText></w:r></w:del>
<w:ins><w:r>{rpr}<w:t>Net 45</w:t></w:r></w:ins>
'''
doc["word/document.xml"].replace_node(node, replacement)

# Add comment explaining change
change_node = doc["word/document.xml"].get_node(tag="w:ins", attrs={"w:id": "1"})
doc.add_comment(
    start=change_node,
    end=change_node,
    text="Extended payment terms per client request 2025-10-27"
)

doc.save()
```

### Use Case 5: Extracting Comments for Review

**Scenario**: Extract all comments to a summary document.

```bash
# Get markdown with all content
pandoc document.docx -o review.md

# Extract just comments (manual from comments.xml)
xmllint --xpath "//w:comment" unpacked/word/comments.xml
```

---

## Part 9: Performance and Best Practices

### Memory Considerations

**Problem**: Large documents (>100MB) can consume significant memory.

**Solutions:**
- For text extraction: Use pandoc (streams data)
- For editing: Edit specific sections, not entire document
- Process in batches if converting many files

### Validation Best Practices

**Always validate after editing:**
```bash
# XML validation
xmllint --noout unpacked/word/document.xml

# Document validation (open in Word)
soffice --headless --convert-to pdf modified.docx
# If conversion succeeds, document is likely valid
```

### Version Control

**What to version:**
- ✅ Source markdown/plain text
- ✅ Template files
- ❌ Generated .docx files (binary, hard to diff)

**Convert for diffing:**
```bash
# Before committing, create text version
pandoc document.docx -o document.md
git add document.md
```

### Security Considerations

**DOCX files can contain:**
- Macros (`.docm` files)
- Hidden text (white text on white background)
- Metadata (author names, edit history, file paths)
- Embedded objects (can execute code)

**Sanitize before sharing:**
```python
# Remove comments, tracked changes, metadata
from scripts.document import Document

doc = Document('unpacked')

# Delete comments.xml if exists
import os
comments_path = os.path.join(doc.unpacked_path, 'word/comments.xml')
if os.path.exists(comments_path):
    os.remove(comments_path)

# Accept all tracked changes (remove <w:ins>, <w:del> tags)
# ... (requires more complex DOM manipulation)

doc.save()
```

---

## Part 10: Troubleshooting Guide

### Problem: "File is corrupted" when opening

**Diagnosis:**
```bash
# Check if it's actually a ZIP
unzip -t document.docx

# Validate XML
xmllint --noout unpacked/word/document.xml
```

**Common fixes:**
- Missing `[Content_Types].xml` entry for new media
- Invalid XML (unclosed tags)
- Missing relationship in `_rels` files

### Problem: Tracked changes don't appear

**Check:**
```bash
# Is track changes enabled?
grep trackRevisions unpacked/word/settings.xml

# Are changes properly formatted?
grep -A 5 "<w:ins" unpacked/word/document.xml
```

**Fix:**
```python
doc = Document('unpacked', track_revisions=True)  # Enables tracking
```

### Problem: Images don't display

**Check:**
```bash
# Does image file exist?
ls unpacked/word/media/

# Is relationship defined?
grep "image" unpacked/word/_rels/document.xml.rels

# Is content type registered?
grep "png" unpacked/[Content_Types].xml
```

### Problem: Styles not applying

**Check:**
```bash
# Does style exist in styles.xml?
grep "Heading1" unpacked/word/styles.xml

# Is style referenced correctly in document?
grep "Heading1" unpacked/word/document.xml
```

---

## Quick Reference: Common Operations

| **Task** | **Command/Code** |
|----------|------------------|
| Extract text | `pandoc doc.docx -o output.md` |
| Unpack DOCX | `python ooxml/scripts/unpack.py doc.docx unpacked/` |
| Repack DOCX | `python ooxml/scripts/pack.py unpacked/ new.docx` |
| Convert to PDF | `soffice --headless --convert-to pdf doc.docx` |
| Extract images | `unzip -j doc.docx 'word/media/*' -d images/` |
| Validate XML | `xmllint --noout unpacked/word/document.xml` |
| Show tracked changes | `pandoc --track-changes=all doc.docx -o review.md` |
| Find text in XML | `grep -n "search text" unpacked/word/document.xml` |

---

## Next Steps

**To learn more:**
1. **Read the books**: "Python for Excel" covers openpyxl (similar to python-docx)
2. **Explore examples**: Unpack real documents to see how Word creates complex structures
3. **Practice**: Start with simple edits (text replacement) before tracking changes
4. **Check official docs**: ECMA-376 specification for complete OOXML reference

**Common next questions:**
- "How do I work with Excel files?" → See "Python for Excel" book
- "How do I work with PowerPoint?" → Similar OOXML structure, use `python-pptx`
- "How do I automate Office on Windows?" → Look into COM automation with `pywin32`

---

## Summary: The Three Mental Models

1. **DOCX = ZIP of XML files** → You can unzip, edit XML, rezip
2. **Text = `<w:p>` + `<w:r>` + `<w:t>`** → Paragraph, Run, Text
3. **Track Changes = Wrapping in `<w:ins>` / `<w:del>`** → Markup, not replacement

**Choose your tool:**
- **Creating new?** → `docx` (JavaScript)
- **Reading only?** → `pandoc`
- **Editing existing?** → Python OOXML library
- **Tracking changes?** → Python Document class

---

**That's it!** You now understand how DOCX files work under the hood, what tools to use for each task, and how to avoid common pitfalls.
