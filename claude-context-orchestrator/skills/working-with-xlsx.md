# Working with XLSX Files: A Comprehensive Guide

## Mental Model: XLSX is Also a ZIP Archive of XML

**🧠 Core Concept**: Just like DOCX, an .xlsx file isn't actually a spreadsheet - it's a **ZIP file containing XML files** that describe your workbook.

```bash
# Prove it: Unzip any .xlsx file
cp spreadsheet.xlsx spreadsheet.zip
unzip -q spreadsheet.zip -d unpacked
tree unpacked
```

**What you'll see:**
```
unpacked/
├── [Content_Types].xml      # File type declarations
├── _rels/                   # Relationships between files
│   └── .rels
├── docProps/                # Document properties (metadata)
│   ├── app.xml
│   └── core.xml
└── xl/                      # ⭐ YOUR ACTUAL WORKBOOK
    ├── workbook.xml         # Workbook structure
    ├── worksheets/
    │   ├── sheet1.xml       # Sheet 1 data
    │   ├── sheet2.xml       # Sheet 2 data
    │   └── _rels/
    ├── sharedStrings.xml    # Shared text values
    ├── styles.xml           # Cell formatting, fonts, colors
    ├── calcChain.xml        # Formula calculation order
    └── _rels/
```

**This means:**
- XLSX uses **Office Open XML** (same as DOCX, PPTX)
- All text-based XML - no binary formats
- Formulas stored as strings (not evaluated values)
- Styles defined separately and referenced
- Can edit with text tools (carefully!)

**XLSX vs CSV:**
| XLSX | CSV |
|------|-----|
| Multiple sheets | Single table |
| Formulas preserved | Only values |
| Rich formatting (fonts, colors) | Plain text |
| Charts, images, comments | Data only |
| File size larger | File size smaller |
| Requires library to read | Easy to parse |

---

## The XLSX Ecosystem: Choose Your Tool

| **Task** | **Best Tool** | **Why** |
|----------|---------------|---------|
| Data analysis | `pandas` | Fast, powerful, perfect for data science |
| Create new workbook | `openpyxl` or `XlsxWriter` | Full Excel feature support |
| Preserve formulas | `openpyxl` | Reads/writes formulas without evaluating |
| Read-only (large files) | `openpyxl` (read_only=True) | Memory efficient |
| Write-only (large exports) | `openpyxl` (write_only=True) or `XlsxWriter` | Fast writing |
| Charts and graphs | `openpyxl` or `XlsxWriter` | Built-in chart support |
| Recalculate formulas | LibreOffice (`recalc.py` script) | Actual Excel engine |
| Quick inspection | `pandas.read_excel()` | One-liner data preview |
| Automation with Excel app | `xlwings` (requires Excel) | Direct Excel automation |
| Compatibility (old Excel) | `xlrd`, `xlwt` | For .xls files (Excel 97-2003) |

---

## Part 1: Reading Excel Files

### Quick Data Loading with pandas

**Use Case**: Load data for analysis.

```python
import pandas as pd

# Read first sheet
df = pd.read_excel("data.xlsx")
print(df.head())

# Read specific sheet by name
df = pd.read_excel("data.xlsx", sheet_name="Sales")

# Read specific sheet by index (0-based)
df = pd.read_excel("data.xlsx", sheet_name=1)

# Read all sheets into dictionary
all_sheets = pd.read_excel("data.xlsx", sheet_name=None)
for sheet_name, df in all_sheets.items():
    print(f"\n{sheet_name}:")
    print(df.head())

# Read specific columns only (faster for large files)
df = pd.read_excel("data.xlsx", usecols=["Name", "Age", "Salary"])

# Read with specific data types
df = pd.read_excel("data.xlsx", dtype={"ID": str, "Amount": float})

# Skip rows at top
df = pd.read_excel("data.xlsx", header=2)  # Use row 3 as header

# Parse dates automatically
df = pd.read_excel("data.xlsx", parse_dates=["Date", "Timestamp"])
```

### Reading with openpyxl (Preserves Formulas)

**Use Case**: Need formulas, formatting, or cell-level access.

```python
from openpyxl import load_workbook

# Load workbook
wb = load_workbook("spreadsheet.xlsx")

# Access sheets
print(wb.sheetnames)  # ['Sheet1', 'Sheet2', 'Summary']
sheet = wb['Sheet1']  # By name
sheet = wb.active     # Active sheet

# Read cell values
value = sheet['A1'].value
value = sheet.cell(row=1, column=1).value  # Same as above

# Read range
for row in sheet['A1:C3']:
    for cell in row:
        print(cell.value, end="\t")
    print()

# Read formula (not calculated value)
formula = sheet['B5'].value  # Might be "=SUM(B2:B4)"

# Read calculated values (WARNING: loses formulas on save!)
wb = load_workbook("spreadsheet.xlsx", data_only=True)
calculated_value = sheet['B5'].value  # Actual number

# Iterate all rows
for row in sheet.iter_rows(min_row=2, values_only=True):
    print(row)  # (value1, value2, value3, ...)

# Get dimensions
print(f"Max row: {sheet.max_row}")
print(f"Max column: {sheet.max_column}")
```

### Reading Cell Formatting

```python
from openpyxl import load_workbook

wb = load_workbook("formatted.xlsx")
sheet = wb.active

cell = sheet['A1']

# Font
print(f"Font: {cell.font.name}, Size: {cell.font.size}")
print(f"Bold: {cell.font.bold}, Italic: {cell.font.italic}")
print(f"Color: {cell.font.color}")

# Fill (background)
print(f"Fill: {cell.fill.start_color}")

# Alignment
print(f"Horizontal: {cell.alignment.horizontal}")
print(f"Vertical: {cell.alignment.vertical}")

# Number format
print(f"Number format: {cell.number_format}")
```

---

## Part 2: Creating Excel Files

### With pandas (Simple Data Export)

**Use Case**: Export DataFrame to Excel quickly.

```python
import pandas as pd

# Create DataFrame
df = pd.DataFrame({
    'Product': ['Widget', 'Gadget', 'Doohickey'],
    'Price': [10.99, 24.99, 5.49],
    'Stock': [150, 87, 203]
})

# Write to Excel
df.to_excel("output.xlsx", index=False)

# Write multiple sheets
with pd.ExcelWriter("multi_sheet.xlsx") as writer:
    df.to_excel(writer, sheet_name="Products", index=False)
    df.head(2).to_excel(writer, sheet_name="Summary", index=False)

# With basic formatting (requires openpyxl)
with pd.ExcelWriter("formatted.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Data", index=False)

    # Access workbook for formatting
    workbook = writer.book
    worksheet = writer.sheets["Data"]

    # Auto-adjust column widths
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        worksheet.column_dimensions[column_letter].width = max_length + 2
```

### With openpyxl (Full Control)

**Use Case**: Create workbooks with formulas, formatting, multiple sheets.

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = Workbook()
sheet = wb.active
sheet.title = "Sales Report"

# Headers
headers = ["Product", "Q1", "Q2", "Q3", "Q4", "Total"]
sheet.append(headers)

# Format headers
header_font = Font(bold=True, color="FFFFFF")
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

for cell in sheet[1]:
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center")

# Data rows
data = [
    ["Widget", 1000, 1200, 1100, 1300],
    ["Gadget", 800, 850, 900, 950],
    ["Doohickey", 600, 650, 700, 750]
]

for row in data:
    sheet.append(row)

# Add formulas for Total column (column F)
for row in range(2, sheet.max_row + 1):
    sheet[f'F{row}'] = f'=SUM(B{row}:E{row})'

# Format numbers as currency
from openpyxl.styles import numbers
for row in range(2, sheet.max_row + 1):
    for col in ['B', 'C', 'D', 'E', 'F']:
        sheet[f'{col}{row}'].number_format = '$#,##0'

# Add totals row
last_row = sheet.max_row + 1
sheet[f'A{last_row}'] = "Total"
sheet[f'A{last_row}'].font = Font(bold=True)

for col in ['B', 'C', 'D', 'E', 'F']:
    sheet[f'{col}{last_row}'] = f'=SUM({col}2:{col}{last_row-1})'
    sheet[f'{col}{last_row}'].font = Font(bold=True)
    sheet[f'{col}{last_row}'].number_format = '$#,##0'

# Column widths
sheet.column_dimensions['A'].width = 15
for col in ['B', 'C', 'D', 'E', 'F']:
    sheet.column_dimensions[col].width = 12

# Save
wb.save("sales_report.xlsx")
```

**After creating formulas, ALWAYS recalculate:**
```bash
python recalc.py sales_report.xlsx
```

### Financial Model with Color Coding

**Use Case**: Create professional financial models following industry standards.

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet.title = "Financial Model"

# Define colors (RGB)
blue_font = Font(color="0000FF")    # Hardcoded inputs
black_font = Font(color="000000")   # Formulas
green_font = Font(color="008000")   # Links to other sheets
red_font = Font(color="FF0000")     # External links
yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

# Assumptions section
sheet['A1'] = "Key Assumptions"
sheet['A1'].font = Font(bold=True, size=14)

sheet['A3'] = "Revenue Growth Rate"
sheet['B3'] = 0.15  # 15%
sheet['B3'].font = blue_font  # Blue = user input
sheet['B3'].number_format = '0.0%'

sheet['A4'] = "COGS as % of Revenue"
sheet['B4'] = 0.40  # 40%
sheet['B4'].font = blue_font
sheet['B4'].number_format = '0.0%'

# Revenue projection
sheet['A7'] = "Revenue Projection"
sheet['A7'].font = Font(bold=True)

# Years
years = ["2024", "2025", "2026", "2027", "2028"]
for i, year in enumerate(years, start=2):
    col = chr(65 + i)  # B, C, D, E, F
    sheet[f'{col}8'] = year

# Base revenue
sheet['A9'] = "Revenue ($mm)"
sheet['B9'] = 100  # Base year
sheet['B9'].font = blue_font
sheet['B9'].number_format = '$#,##0;($#,##0);-'

# Growth formula
for i, col in enumerate(['C', 'D', 'E', 'F'], start=1):
    prev_col = chr(ord(col) - 1)
    sheet[f'{col}9'] = f'={prev_col}9*(1+$B$3)'
    sheet[f'{col}9'].font = black_font  # Black = formula
    sheet[f'{col}9'].number_format = '$#,##0;($#,##0);-'

# COGS
sheet['A10'] = "COGS ($mm)"
for col in ['B', 'C', 'D', 'E', 'F']:
    sheet[f'{col}10'] = f'={col}9*$B$4'
    sheet[f'{col}10'].font = black_font
    sheet[f'{col}10'].number_format = '$#,##0;($#,##0);-'

# Gross Profit
sheet['A11'] = "Gross Profit ($mm)"
for col in ['B', 'C', 'D', 'E', 'F']:
    sheet[f'{col}11'] = f'={col}9-{col}10'
    sheet[f'{col}11'].font = black_font
    sheet[f'{col}11'].number_format = '$#,##0;($#,##0);-'

# Gross Margin %
sheet['A12'] = "Gross Margin %"
for col in ['B', 'C', 'D', 'E', 'F']:
    sheet[f'{col}12'] = f'={col}11/{col}9'
    sheet[f'{col}12'].font = black_font
    sheet[f'{col}12'].number_format = '0.0%'

# Column widths
sheet.column_dimensions['A'].width = 20
for col in ['B', 'C', 'D', 'E', 'F']:
    sheet.column_dimensions[col].width = 12

wb.save("financial_model.xlsx")
```

---

## Part 3: Formulas and Formatting

### Excel Formulas (Critical Rules)

**❌ WRONG: Hardcoding values**
```python
# BAD: Calculating in Python
total = sum([100, 200, 300])
sheet['D5'] = total  # Hardcodes 600
```

**✅ CORRECT: Using Excel formulas**
```python
# GOOD: Let Excel calculate
sheet['D5'] = '=SUM(D2:D4)'
```

**Common formulas:**
```python
# Math
sheet['C1'] = '=A1+B1'        # Addition
sheet['C1'] = '=A1-B1'        # Subtraction
sheet['C1'] = '=A1*B1'        # Multiplication
sheet['C1'] = '=A1/B1'        # Division
sheet['C1'] = '=A1^2'         # Power

# Aggregation
sheet['C1'] = '=SUM(A1:A10)'      # Sum range
sheet['C1'] = '=AVERAGE(A1:A10)'  # Average
sheet['C1'] = '=MAX(A1:A10)'      # Maximum
sheet['C1'] = '=MIN(A1:A10)'      # Minimum
sheet['C1'] = '=COUNT(A1:A10)'    # Count numbers
sheet['C1'] = '=COUNTA(A1:A10)'   # Count non-empty cells

# Logical
sheet['C1'] = '=IF(A1>100,"High","Low")'
sheet['C1'] = '=AND(A1>0,B1<100)'
sheet['C1'] = '=OR(A1>100,B1<50)'

# Text
sheet['C1'] = '=CONCATENATE(A1," ",B1)'
sheet['C1'] = '=LEFT(A1,5)'       # First 5 chars
sheet['C1'] = '=RIGHT(A1,3)'      # Last 3 chars
sheet['C1'] = '=LEN(A1)'          # Length
sheet['C1'] = '=UPPER(A1)'        # Uppercase

# Lookup
sheet['C1'] = '=VLOOKUP(A1,Table!A:C,2,FALSE)'  # Vertical lookup
sheet['C1'] = '=INDEX(A1:C10,5,2)'              # Get value at row 5, col 2
sheet['C1'] = '=MATCH(A1,B1:B10,0)'             # Find position

# Error handling
sheet['C1'] = '=IFERROR(A1/B1,0)'  # Return 0 if division error
sheet['C1'] = '=IFNA(VLOOKUP(A1,Table!A:C,2,0),"Not Found")'

# Cross-sheet references
sheet['C1'] = '=Sheet2!A1'         # Reference other sheet
sheet['C1'] = '=SUM(Sheet2!A1:A10)'
```

### Cell Formatting

**Number formats:**
```python
from openpyxl.styles import numbers

# Currency
cell.number_format = '$#,##0.00'
cell.number_format = '$#,##0;($#,##0);-'  # Negatives in parentheses, zeros as dash

# Percentage
cell.number_format = '0.0%'    # 15.0%
cell.number_format = '0.00%'   # 15.25%

# Thousands
cell.number_format = '#,##0'   # 1,234

# Date
cell.number_format = 'mm/dd/yyyy'
cell.number_format = 'dd-mmm-yy'  # 27-Oct-25
cell.number_format = 'mmmm d, yyyy'  # October 27, 2025

# Time
cell.number_format = 'h:mm AM/PM'

# Custom
cell.number_format = '[Blue]#,##0;[Red](#,##0)'  # Blue positive, red negative
```

**Font and colors:**
```python
from openpyxl.styles import Font, PatternFill

# Font
cell.font = Font(
    name="Arial",
    size=12,
    bold=True,
    italic=False,
    color="FF0000"  # Red (hex RRGGBB)
)

# Background color
cell.fill = PatternFill(
    start_color="FFFF00",  # Yellow
    end_color="FFFF00",
    fill_type="solid"
)
```

**Alignment and borders:**
```python
from openpyxl.styles import Alignment, Border, Side

# Alignment
cell.alignment = Alignment(
    horizontal="center",  # left, center, right
    vertical="center",    # top, center, bottom
    wrap_text=True
)

# Borders
thin_border = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)
cell.border = thin_border
```

---

## Part 4: Advanced Features

### Charts

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

wb = Workbook()
sheet = wb.active

# Sample data
rows = [
    ["Product", "Sales"],
    ["Widget", 1000],
    ["Gadget", 850],
    ["Doohickey", 720]
]

for row in rows:
    sheet.append(row)

# Create chart
chart = BarChart()
chart.type = "col"  # Column chart
chart.style = 10
chart.title = "Sales by Product"
chart.y_axis.title = "Sales"
chart.x_axis.title = "Product"

# Data for chart
data = Reference(sheet, min_col=2, min_row=1, max_row=4)
cats = Reference(sheet, min_col=1, min_row=2, max_row=4)

chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)

# Add chart to sheet
sheet.add_chart(chart, "D2")

wb.save("chart_example.xlsx")
```

**Other chart types:**
```python
from openpyxl.chart import LineChart, PieChart, ScatterChart, AreaChart

# Line chart
chart = LineChart()

# Pie chart
chart = PieChart()

# Scatter plot
chart = ScatterChart()

# Area chart
chart = AreaChart()
```

### Conditional Formatting

```python
from openpyxl import Workbook
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, DataBarRule
from openpyxl.styles import PatternFill, Font

wb = Workbook()
sheet = wb.active

# Add data
for i in range(1, 11):
    sheet[f'A{i}'] = i * 10

# Color scale (red to yellow to green)
color_scale = ColorScaleRule(
    start_type="min", start_color="FF0000",  # Red
    mid_type="percentile", mid_value=50, mid_color="FFFF00",  # Yellow
    end_type="max", end_color="00FF00"  # Green
)
sheet.conditional_formatting.add("A1:A10", color_scale)

# Highlight cells greater than 50
red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
white_font = Font(color="FFFFFF")

rule = CellIsRule(operator="greaterThan", formula=['50'], fill=red_fill, font=white_font)
sheet.conditional_formatting.add("A1:A10", rule)

# Data bars
data_bar = DataBarRule(
    start_type="min", start_value=0,
    end_type="max", end_value=100,
    color="6495ED"  # Blue
)
sheet.conditional_formatting.add("A1:A10", data_bar)

wb.save("conditional_format.xlsx")
```

### Data Validation (Dropdowns)

```python
from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation

wb = Workbook()
sheet = wb.active

# Create dropdown list
dv = DataValidation(type="list", formula1='"Low,Medium,High"', allow_blank=False)
dv.error = "Invalid selection"
dv.errorTitle = "Invalid Input"
dv.prompt = "Please select from the list"
dv.promptTitle = "Priority Level"

# Add to sheet
sheet.add_data_validation(dv)

# Apply to range
dv.add("B2:B100")

# Number validation
num_dv = DataValidation(type="whole", operator="between", formula1=1, formula2=100)
sheet.add_data_validation(num_dv)
num_dv.add("C2:C100")

wb.save("validation.xlsx")
```

### Freeze Panes

```python
# Freeze top row
sheet.freeze_panes = "A2"

# Freeze first column
sheet.freeze_panes = "B1"

# Freeze both (top row and first column)
sheet.freeze_panes = "B2"

# Freeze first 3 rows and 2 columns
sheet.freeze_panes = "C4"
```

---

## Part 5: Data Analysis with pandas

### Loading and Exploring

```python
import pandas as pd

df = pd.read_excel("sales_data.xlsx")

# Quick overview
df.head()           # First 5 rows
df.tail()           # Last 5 rows
df.info()           # Column types, non-null counts
df.describe()       # Statistical summary
df.shape            # (rows, columns)

# Column operations
df.columns          # Column names
df.dtypes           # Data types
df['Sales'].unique()  # Unique values in column
df['Sales'].value_counts()  # Count by value
```

### Data Manipulation

```python
# Filter rows
high_sales = df[df['Sales'] > 1000]
recent = df[df['Date'] > '2025-01-01']
filtered = df[(df['Region'] == 'North') & (df['Sales'] > 500)]

# Select columns
subset = df[['Product', 'Sales']]

# Sort
sorted_df = df.sort_values('Sales', ascending=False)
sorted_df = df.sort_values(['Region', 'Sales'], ascending=[True, False])

# Group and aggregate
by_region = df.groupby('Region')['Sales'].sum()
summary = df.groupby('Product').agg({
    'Sales': ['sum', 'mean', 'count'],
    'Profit': 'sum'
})

# Add columns
df['Profit_Margin'] = df['Profit'] / df['Sales']
df['Year'] = pd.to_datetime(df['Date']).dt.year

# Merge DataFrames
merged = pd.merge(df1, df2, on='Product', how='inner')
# how='left', 'right', 'outer', 'inner'
```

### Pivot Tables

```python
# Create pivot table
pivot = pd.pivot_table(
    df,
    values='Sales',
    index='Product',
    columns='Region',
    aggfunc='sum',
    fill_value=0
)

# Multiple aggregations
pivot = pd.pivot_table(
    df,
    values=['Sales', 'Profit'],
    index='Product',
    columns='Year',
    aggfunc={'Sales': 'sum', 'Profit': 'mean'}
)

# Export pivot to Excel
pivot.to_excel("pivot_results.xlsx")
```

### Exporting with Formatting

```python
import pandas as pd

df = pd.DataFrame({
    'Product': ['Widget', 'Gadget'],
    'Sales': [1234.56, 2345.67],
    'Growth': [0.15, 0.23]
})

with pd.ExcelWriter("styled_output.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Report", index=False)

    # Access workbook
    workbook = writer.book
    worksheet = writer.sheets["Report"]

    # Format currency
    for row in range(2, len(df) + 2):
        worksheet[f'B{row}'].number_format = '$#,##0.00'
        worksheet[f'C{row}'].number_format = '0.0%'

    # Bold headers
    from openpyxl.styles import Font
    for cell in worksheet[1]:
        cell.font = Font(bold=True)
```

---

## Part 6: XLSX Internals

### File Structure

**Key files in unpacked .xlsx:**

`xl/workbook.xml` - Workbook structure
```xml
<workbook>
  <sheets>
    <sheet name="Sheet1" sheetId="1" r:id="rId1"/>
    <sheet name="Sheet2" sheetId="2" r:id="rId2"/>
  </sheets>
</workbook>
```

`xl/worksheets/sheet1.xml` - Sheet data
```xml
<worksheet>
  <sheetData>
    <row r="1">
      <c r="A1" t="s">  <!-- t="s" means shared string -->
        <v>0</v>  <!-- Index into sharedStrings.xml -->
      </c>
      <c r="B1">
        <v>42</v>  <!-- Direct number -->
      </c>
      <c r="C1">
        <f>A1+B1</f>  <!-- Formula -->
        <v>42</v>  <!-- Calculated value (if available) -->
      </c>
    </row>
  </sheetData>
</worksheet>
```

`xl/sharedStrings.xml` - Shared text values
```xml
<sst count="3" uniqueCount="3">
  <si><t>Hello</t></si>
  <si><t>World</t></si>
  <si><t>Example</t></si>
</sst>
```

**Why shared strings?**
- Reduces file size (text "Total" appears once, referenced many times)
- Faster to process
- Cell contains index, not full text

`xl/styles.xml` - Cell formatting
```xml
<cellXfs>
  <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>  <!-- Default -->
  <xf numFmtId="14" fontId="1" fillId="2" borderId="1"/> <!-- Custom -->
</cellXfs>
```

### Cell References

**Absolute vs Relative:**
```python
sheet['C1'] = '=A1+B1'      # Relative: moves when copied
sheet['C1'] = '=$A$1+$B$1'  # Absolute: stays fixed
sheet['C1'] = '=$A1+B$1'    # Mixed: column A fixed, row varies
```

**R1C1 notation (internal):**
- Excel displays: `A1`
- Internal XML: `r="1" c="1"`
- R1C1: `R1C1` (Row 1, Column 1)

### Formulas vs Values

**Important distinction:**

When you write:
```python
sheet['A1'] = '=SUM(B1:B10)'
```

The cell contains:
- **Formula**: `=SUM(B1:B10)` (stored)
- **Value**: `null` or cached value (not automatically calculated!)

**To get calculated values:**
```bash
# Use LibreOffice to recalculate
python recalc.py spreadsheet.xlsx
```

**After recalculation**, the XML contains:
```xml
<c r="A1">
  <f>SUM(B1:B10)</f>
  <v>1234</v>  <!-- Calculated value -->
</c>
```

---

## Part 7: Real-World Use Cases

### Use Case 1: Financial Statement Analysis

```python
import pandas as pd
import openpyxl

# Load historical data
df = pd.read_excel("financials.xlsx", sheet_name="Income Statement")

# Calculate metrics
df['Gross_Margin_%'] = (df['Revenue'] - df['COGS']) / df['Revenue'] * 100
df['Operating_Margin_%'] = df['Operating_Income'] / df['Revenue'] * 100

# Create summary workbook
wb = openpyxl.Workbook()
sheet = wb.active
sheet.title = "Analysis"

# Headers
headers = ["Metric", "2023", "2024", "2025"]
sheet.append(headers)

# Data
metrics = [
    ["Revenue Growth %", "=C3/B3-1", "=D3/C3-1"],
    ["Gross Margin %", "=B5", "=C5", "=D5"],
    ["Operating Margin %", "=B6", "=C6", "=D6"]
]

for metric in metrics:
    sheet.append(metric)

# Format percentages
for row in range(2, sheet.max_row + 1):
    for col in ['B', 'C', 'D']:
        sheet[f'{col}{row}'].number_format = '0.0%'

wb.save("analysis.xlsx")
```

### Use Case 2: Automated Reporting

```python
import pandas as pd
from datetime import datetime

# Load raw data
sales = pd.read_csv("sales.csv")

# Process
summary = sales.groupby('Product').agg({
    'Quantity': 'sum',
    'Revenue': 'sum',
    'Profit': 'sum'
}).reset_index()

summary['Margin%'] = summary['Profit'] / summary['Revenue']

# Create report with timestamp
filename = f"Sales_Report_{datetime.now().strftime('%Y%m%d')}.xlsx"

with pd.ExcelWriter(filename, engine="openpyxl") as writer:
    summary.to_excel(writer, sheet_name="Summary", index=False)

    # Format
    worksheet = writer.sheets["Summary"]

    # Currency columns
    for row in range(2, len(summary) + 2):
        worksheet[f'C{row}'].number_format = '$#,##0'
        worksheet[f'D{row}'].number_format = '$#,##0'
        worksheet[f'E{row}'].number_format = '0.0%'

print(f"Report saved: {filename}")
```

### Use Case 3: Data Validation and Cleaning

```python
import pandas as pd

# Load data
df = pd.read_excel("raw_data.xlsx")

# Initial diagnostics
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"Null counts:\n{df.isnull().sum()}")
print(f"Duplicates: {df.duplicated().sum()}")

# Clean
df = df.drop_duplicates()
df = df.dropna(subset=['ID', 'Date'])  # Drop rows missing critical fields
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Parse dates
df = df[df['Amount'] > 0]  # Filter invalid amounts

# Export cleaned data
df.to_excel("cleaned_data.xlsx", index=False)

# Create data quality report
quality_report = pd.DataFrame({
    'Original_Rows': [len(pd.read_excel("raw_data.xlsx"))],
    'Cleaned_Rows': [len(df)],
    'Duplicates_Removed': [pd.read_excel("raw_data.xlsx").duplicated().sum()],
    'Invalid_Dates': [pd.read_excel("raw_data.xlsx")['Date'].isna().sum()]
})

quality_report.to_excel("quality_report.xlsx", index=False)
```

### Use Case 4: Budget vs Actuals

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

wb = Workbook()
sheet = wb.active
sheet.title = "Budget vs Actuals"

# Headers
headers = ["Category", "Budget", "Actual", "Variance", "Variance %"]
sheet.append(headers)

# Format headers
for cell in sheet[1]:
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    cell.font = Font(bold=True, color="FFFFFF")

# Data
categories = ["Salaries", "Rent", "Utilities", "Marketing", "Supplies"]
budgets = [50000, 10000, 2000, 15000, 3000]
actuals = [52000, 10000, 1800, 12000, 3500]

for i, (cat, budget, actual) in enumerate(zip(categories, budgets, actuals), start=2):
    sheet[f'A{i}'] = cat
    sheet[f'B{i}'] = budget
    sheet[f'C{i}'] = actual
    sheet[f'D{i}'] = f'=C{i}-B{i}'  # Variance
    sheet[f'E{i}'] = f'=D{i}/B{i}'  # Variance %

    # Format
    sheet[f'B{i}'].number_format = '$#,##0'
    sheet[f'C{i}'].number_format = '$#,##0'
    sheet[f'D{i}'].number_format = '$#,##0;[Red]($#,##0)'  # Red if negative
    sheet[f'E{i}'].number_format = '0.0%;[Red](0.0%)'

# Totals
last_row = sheet.max_row + 1
sheet[f'A{last_row}'] = "Total"
sheet[f'A{last_row}'].font = Font(bold=True)

for col in ['B', 'C', 'D']:
    sheet[f'{col}{last_row}'] = f'=SUM({col}2:{col}{last_row-1})'
    sheet[f'{col}{last_row}'].font = Font(bold=True)
    sheet[f'{col}{last_row}'].number_format = '$#,##0;[Red]($#,##0)'

wb.save("budget_actuals.xlsx")
```

---

## Part 8: Performance and Best Practices

### For Large Files (100,000+ rows)

**Problem**: Loading entire file consumes too much memory.

**Solutions:**
```python
# 1. Read-only mode (openpyxl)
from openpyxl import load_workbook

wb = load_workbook("large.xlsx", read_only=True)
sheet = wb.active

for row in sheet.iter_rows(values_only=True):
    # Process row
    pass

wb.close()

# 2. Read specific columns only (pandas)
df = pd.read_excel("large.xlsx", usecols=['A', 'C', 'E'])

# 3. Read in chunks (pandas with CSV intermediate)
# First convert XLSX to CSV, then read in chunks
df.to_csv("temp.csv", index=False)

chunk_size = 10000
for chunk in pd.read_csv("temp.csv", chunksize=chunk_size):
    # Process chunk
    pass

# 4. Write-only mode for export (openpyxl)
from openpyxl import Workbook

wb = Workbook(write_only=True)
sheet = wb.create_sheet()

for data_row in large_dataset:
    sheet.append(data_row)

wb.save("large_output.xlsx")
```

### Memory Optimization

```python
# BAD: Loading entire file multiple times
df1 = pd.read_excel("data.xlsx")
df2 = pd.read_excel("data.xlsx", sheet_name="Sheet2")
df3 = pd.read_excel("data.xlsx", sheet_name="Sheet3")

# GOOD: Load once
all_sheets = pd.read_excel("data.xlsx", sheet_name=None)
df1 = all_sheets['Sheet1']
df2 = all_sheets['Sheet2']
df3 = all_sheets['Sheet3']
```

### Formula Efficiency

**Slow formulas:**
```python
# Slow: Volatile functions recalculate on every change
sheet['A1'] = '=TODAY()'
sheet['A1'] = '=NOW()'
sheet['A1'] = '=OFFSET(A1,1,1)'

# Slow: Array formulas over large ranges
sheet['A1'] = '=SUMPRODUCT((A1:A10000)*(B1:B10000))'
```

**Fast alternatives:**
```python
# Fast: Use specific ranges, not entire columns
sheet['A1'] = '=SUM(B1:B1000)'  # Good
# vs
sheet['A1'] = '=SUM(B:B)'  # Slow (scans entire column)

# Fast: Use INDEX/MATCH instead of VLOOKUP for large tables
sheet['A1'] = '=INDEX(C1:C1000,MATCH(A1,B1:B1000,0))'
```

---

## Part 9: Troubleshooting

### Problem: Formula Errors After Creation

**Symptoms:** #REF!, #DIV/0!, #VALUE!, #NAME? errors

**Diagnosis:**
```bash
python recalc.py spreadsheet.xlsx
```

**Output:**
```json
{
  "status": "errors_found",
  "total_errors": 3,
  "error_summary": {
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    },
    "#DIV/0!": {
      "count": 1,
      "locations": ["Sheet1!D20"]
    }
  }
}
```

**Fixes:**
```python
# #REF! - Invalid cell reference
# Fix: Check cell references in formula
sheet['B5'] = '=A5+B4'  # Was referencing deleted cell

# #DIV/0! - Division by zero
# Fix: Add error handling
sheet['D20'] = '=IFERROR(A20/B20, 0)'

# #VALUE! - Wrong data type
# Fix: Ensure correct types
sheet['E15'] = '=VALUE(A15)'  # Convert text to number

# #NAME? - Unknown function name
# Fix: Check spelling
sheet['F10'] = '=SUM(A1:A10)'  # Was "SUMM"
```

### Problem: Can't Read Formulas (Only See Values)

**Cause:** Opened with `data_only=True`

**Solution:**
```python
# For reading formulas
wb = load_workbook("file.xlsx")  # data_only=False (default)
formula = sheet['A1'].value  # Gets "=SUM(B1:B10)"

# For reading calculated values
wb = load_workbook("file.xlsx", data_only=True)
value = sheet['A1'].value  # Gets 1234
```

### Problem: Excel Says File is Corrupted

**Diagnosis:**
```bash
# Check if it's actually a ZIP file
file spreadsheet.xlsx
# Should output: Microsoft Excel 2007+
```

**Causes:**
- Incomplete write (script crashed mid-save)
- Invalid XML structure
- Missing required files

**Fixes:**
```python
# 1. Try opening with openpyxl (better error messages)
from openpyxl import load_workbook
try:
    wb = load_workbook("corrupted.xlsx")
except Exception as e:
    print(f"Error: {e}")

# 2. Try pandas (more forgiving)
df = pd.read_excel("corrupted.xlsx")

# 3. Repair with Excel via xlwings (requires Excel installed)
import xlwings as xw
app = xw.App(visible=False)
wb = app.books.open("corrupted.xlsx")
wb.save("repaired.xlsx")
wb.close()
app.quit()
```

### Problem: Date Formatting Issues

**Cause:** Excel stores dates as numbers (days since 1900-01-01)

**Solutions:**
```python
# Reading dates with pandas
df = pd.read_excel("data.xlsx", parse_dates=['Date'])

# Writing dates with openpyxl
from datetime import datetime
sheet['A1'] = datetime(2025, 10, 27)
sheet['A1'].number_format = 'mm/dd/yyyy'

# Converting Excel serial date to Python datetime
from datetime import datetime, timedelta
excel_date = 45678
python_date = datetime(1899, 12, 30) + timedelta(days=excel_date)
```

---

## Quick Reference

| **Task** | **Code** |
|----------|----------|
| Read Excel | `pd.read_excel("file.xlsx")` |
| Read sheet | `pd.read_excel("file.xlsx", sheet_name="Sheet1")` |
| Write Excel | `df.to_excel("output.xlsx", index=False)` |
| Load workbook | `wb = load_workbook("file.xlsx")` |
| Create workbook | `wb = Workbook()` |
| Add formula | `sheet['A1'] = '=SUM(B1:B10)'` |
| Format currency | `cell.number_format = '$#,##0.00'` |
| Format percentage | `cell.number_format = '0.0%'` |
| Bold font | `cell.font = Font(bold=True)` |
| Background color | `cell.fill = PatternFill(start_color="FFFF00", fill_type="solid")` |
| Freeze panes | `sheet.freeze_panes = "B2"` |
| Column width | `sheet.column_dimensions['A'].width = 20` |
| Recalculate | `python recalc.py file.xlsx` |

---

## Summary: The Three Mental Models

1. **XLSX = ZIP of XML** → Unzip to see sheets, styles, formulas as XML
2. **Formulas ≠ Values** → Formulas stored as text, need recalculation
3. **Shared Strings** → Text stored once, referenced by index (efficiency)

**Choose your tool:**
- **Data analysis?** → `pandas`
- **Formulas/formatting?** → `openpyxl`
- **Fast export?** → `XlsxWriter` or `openpyxl` write-only mode
- **Recalculate formulas?** → `python recalc.py`

---

**Recommended Reading:**

Read the downloaded book:
- **Python for Excel** (Zumstein) - Covers pandas, openpyxl, xlwings, automation

**Next steps:**
- Explore the `recalc.py` script in xlsx skill directory
- Practice creating financial models with formulas
- Try data analysis workflows with pandas
- Experiment with charts and conditional formatting
