#!/usr/bin/env python3
"""
Analyze PDF extraction quality across different tools.

Usage:
    python quality_analysis.py <extraction_directory>

Example:
    python quality_analysis.py ./pdf_extraction_results

Expects files named: PDFname_tool.txt (e.g., paper_docling.txt, paper_pymupdf.txt)

Copyright 2025 Warren Zhu
Licensed under the Apache License, Version 2.0
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


def analyze_quality(text):
    """Analyze text quality metrics."""
    return {
        'chars': len(text),
        'words': len(text.split()),
        'consecutive_spaces': len(re.findall(r'  +', text)),
        'excessive_newlines': len(re.findall(r'\n{4,}', text)),
        'control_chars': len(re.findall(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text)),
        'garbled_chars': len(re.findall(r'[�\ufffd]', text)),
        'hyphen_breaks': len(re.findall(r'\w+-\n\w+', text))
    }


def compare_tools(results_dir):
    """Compare extraction quality across tools."""

    results_dir = Path(results_dir)
    if not results_dir.exists():
        print(f"Error: {results_dir} not found")
        return

    # Group files by PDF
    pdf_files = defaultdict(dict)

    for txt_file in sorted(results_dir.glob('*.txt')):
        # Parse: PDFname_tool.txt
        parts = txt_file.stem.rsplit('_', 1)
        if len(parts) == 2:
            pdf_name, tool = parts
            text = txt_file.read_text(encoding='utf-8', errors='ignore')
            pdf_files[pdf_name][tool] = text

    if not pdf_files:
        print(f"No extraction files found in {results_dir}")
        print("Expected format: PDFname_tool.txt")
        return

    # Analyze each PDF
    for pdf_name, tools in sorted(pdf_files.items()):
        print("=" * 80)
        print(f"PDF: {pdf_name}")
        print("=" * 80)
        print()

        # Quality metrics
        results = {tool: analyze_quality(text) for tool, text in tools.items()}

        print("QUALITY METRICS")
        print("-" * 80)
        print(f"{'Tool':<20} {'Chars':>12} {'Words':>10} {'Issues':>10} {'Garbled':>10}")
        print("-" * 80)

        for tool in ['docling', 'pymupdf', 'pdfplumber', 'pdftotext', 'pdfminer', 'pypdf']:
            if tool in results:
                r = results[tool]
                issues = (r['consecutive_spaces'] + r['excessive_newlines'] +
                         r['control_chars'] + r['garbled_chars'])
                print(f"{tool:<20} {r['chars']:>12,} {r['words']:>10,} "
                      f"{issues:>10} {r['garbled_chars']:>10}")

        print()

        # Find best
        best_quality = min(results.items(),
                          key=lambda x: x[1]['consecutive_spaces'] + x[1]['garbled_chars'])
        most_content = max(results.items(), key=lambda x: x[1]['chars'])

        print(f"Best quality: {best_quality[0]}")
        print(f"Most content: {most_content[0]}")
        print()

    # Overall ranking
    print("=" * 80)
    print("OVERALL RANKING")
    print("=" * 80)
    print()

    tool_scores = defaultdict(lambda: {'total_issues': 0, 'total_garbled': 0, 'files': 0})

    for tools in pdf_files.values():
        for tool, text in tools.items():
            r = analyze_quality(text)
            issues = (r['consecutive_spaces'] + r['excessive_newlines'] +
                     r['control_chars'] + r['garbled_chars'])

            tool_scores[tool]['total_issues'] += issues
            tool_scores[tool]['total_garbled'] += r['garbled_chars']
            tool_scores[tool]['files'] += 1

    # Calculate average quality
    ranked = []
    for tool, scores in tool_scores.items():
        avg_issues = scores['total_issues'] / scores['files']
        avg_garbled = scores['total_garbled'] / scores['files']
        quality_score = avg_garbled * 10 + avg_issues

        ranked.append({
            'tool': tool,
            'score': quality_score,
            'avg_issues': avg_issues,
            'avg_garbled': avg_garbled
        })

    ranked.sort(key=lambda x: x['score'])

    print(f"{'Rank':<6} {'Tool':<20} {'Avg Issues':>12} {'Avg Garbled':>12} {'Score':>10}")
    print("-" * 80)

    for i, r in enumerate(ranked, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"{medal} {i:<3} {r['tool']:<20} {r['avg_issues']:>12.1f} "
              f"{r['avg_garbled']:>12.1f} {r['score']:>10.1f}")

    print()
    print("Quality score: garbled_chars * 10 + total_issues (lower is better)")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quality_analysis.py <extraction_directory>")
        sys.exit(1)

    compare_tools(sys.argv[1])
