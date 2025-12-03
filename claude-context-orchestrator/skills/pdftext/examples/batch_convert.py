#!/usr/bin/env python3
"""
Batch convert PDFs to markdown using Docling.

Usage:
    python batch_convert.py <pdf_directory> <output_directory>

Example:
    python batch_convert.py ./papers ./markdown_output

Copyright 2025 Warren Zhu
Licensed under the Apache License, Version 2.0
"""

import sys
import time
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
except ImportError:
    print("Error: Docling not installed. Run: pip install docling")
    sys.exit(1)


def batch_convert(pdf_dir, output_dir):
    """Convert all PDFs in directory to markdown."""

    pdf_dir = Path(pdf_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Get PDF files
    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return

    print(f"Found {len(pdf_files)} PDFs")
    print()

    # Initialize converter once
    print("Initializing Docling...")
    converter = DocumentConverter()
    print("Ready")
    print()

    # Convert each PDF
    results = []
    total_start = time.time()

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] {pdf_path.name}")

        try:
            start = time.time()
            result = converter.convert(str(pdf_path))
            markdown = result.document.export_to_markdown()
            elapsed = time.time() - start

            # Save
            output_file = output_dir / f"{pdf_path.stem}.md"
            output_file.write_text(markdown)

            # Stats
            pages = len(result.document.pages)
            chars = len(markdown)

            print(f"  ✓ {pages} pages in {elapsed:.1f}s ({elapsed/pages:.2f}s/page)")
            print(f"  ✓ {chars:,} chars → {output_file.name}")

            results.append({
                'file': pdf_path.name,
                'pages': pages,
                'time': elapsed,
                'status': 'Success'
            })

        except Exception as e:
            elapsed = time.time() - start
            print(f"  ✗ Error: {e}")
            results.append({
                'file': pdf_path.name,
                'pages': 0,
                'time': elapsed,
                'status': f'Failed: {e}'
            })

        print()

    # Summary
    total_time = time.time() - total_start
    success_count = sum(1 for r in results if r['status'] == 'Success')

    print("=" * 60)
    print(f"Complete: {success_count}/{len(results)} successful")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} min)")
    print(f"Output: {output_dir}/")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python batch_convert.py <pdf_dir> <output_dir>")
        sys.exit(1)

    batch_convert(sys.argv[1], sys.argv[2])
