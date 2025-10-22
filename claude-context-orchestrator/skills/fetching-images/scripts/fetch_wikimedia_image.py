#!/usr/bin/env python3
"""
Fetch Wikimedia Commons images programmatically.

Usage:
    python3 fetch_wikimedia_image.py "topic" [--count 5] [--output results.json]

Examples:
    python3 fetch_wikimedia_image.py "paella valenciana"
    python3 fetch_wikimedia_image.py "flamenco dancers" --count 10
"""

import sys
import json
import subprocess
from typing import List, Dict, Optional

def search_wikimedia(topic: str, count: int = 5) -> List[Dict[str, str]]:
    """Search Wikimedia Commons for images on a topic."""
    print(f"🔍 Searching Wikimedia Commons for: {topic}")
    print(f"   Looking for top {count} results...\n")

    # Construct search query
    query = f'site:commons.wikimedia.org {topic} file jpg'

    # Use WebSearch (this will need to be run through Claude Code)
    # For now, output the query and instructions
    print(f"📋 Search query to use:")
    print(f"   {query}")
    print()
    print("💡 Run this through Claude Code WebSearch to find file pages")
    print("   Then extract URLs with the extract_image_url() function below\n")

    return []

def extract_image_url_from_file_page(file_page_url: str) -> Optional[Dict[str, str]]:
    """
    Extract direct image URL from a Wikimedia Commons File: page.

    Args:
        file_page_url: URL like https://commons.wikimedia.org/wiki/File:Image.jpg

    Returns:
        Dict with: direct_url, filename, license, attribution
    """
    print(f"📥 Extracting image URL from: {file_page_url}")

    try:
        # Fetch the page with curl
        curl_result = subprocess.run(
            ['curl', '-s', file_page_url],
            capture_output=True,
            text=True
        )

        if not curl_result.stdout:
            print(f"   ❌ Failed to fetch page")
            return None

        # Extract image URLs with grep
        grep_result = subprocess.run(
            ['grep', '-oE', r'https://upload\.wikimedia\.org/wikipedia/commons/[^"]+\.(jpg|JPG|png|PNG|jpeg|JPEG)'],
            input=curl_result.stdout,
            capture_output=True,
            text=True
        )

        if grep_result.stdout:
            urls = grep_result.stdout.strip().split('\n')
            # Filter out thumbnail URLs, prefer the non-thumb version
            direct_urls = [u for u in urls if '/thumb/' not in u and '/archive/' not in u]
            direct_url = direct_urls[0] if direct_urls else urls[0] if urls else None

            if direct_url:
                filename = direct_url.split('/')[-1]
                print(f"   ✅ Found: {filename}")
                return {
                    'direct_url': direct_url,
                    'filename': filename,
                    'file_page': file_page_url,
                    'license': 'CC BY-SA (check file page for exact version)',
                    'attribution': f'Photo: Wikimedia Commons, [License]'
                }
    except Exception as e:
        print(f"   ❌ Error: {e}")

    return None

def verify_image_url(url: str) -> bool:
    """Verify that an image URL is accessible."""
    print(f"🔍 Verifying URL...")

    cmd = ['curl', '-I', '-s', url]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if 'HTTP/2 200' in result.stdout or 'HTTP/1.1 200' in result.stdout:
        # Also check content-type
        if 'content-type: image/' in result.stdout.lower():
            print(f"   ✅ URL verified (HTTP 200, valid image)")
            return True
        else:
            print(f"   ⚠️  HTTP 200 but not an image content-type")
            return False
    else:
        print(f"   ❌ URL not accessible (not HTTP 200)")
        return False

def generate_html_snippet(image_info: Dict[str, str], alt_text: str = "") -> str:
    """Generate HTML code snippet for embedding the image."""
    return f'''<div class="image-container">
    <img src="{image_info['direct_url']}"
         alt="{alt_text or image_info['filename']}">
    <div class="image-caption">
        {alt_text} (Photo: Wikimedia Commons, {image_info['license']})
    </div>
</div>'''

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Fetch Wikimedia Commons images')
    parser.add_argument('topic', nargs='?', help='Topic to search for (e.g., "paella valenciana")')
    parser.add_argument('--count', type=int, default=5, help='Number of results (default: 5)')
    parser.add_argument('--file-page', help='Direct File: page URL to extract from')
    parser.add_argument('--verify', action='store_true', help='Verify URL accessibility')
    parser.add_argument('--html', action='store_true', help='Generate HTML snippet')
    parser.add_argument('--alt', default='', help='Alt text for HTML snippet')

    args = parser.parse_args()

    # Validate that either topic or --file-page is provided
    if not args.topic and not args.file_page:
        parser.error("Either provide a topic or use --file-page with a File: page URL")

    if args.file_page:
        # Extract from a specific File: page
        info = extract_image_url_from_file_page(args.file_page)

        if info:
            print()
            print("=" * 60)
            print("📸 Image Information")
            print("=" * 60)
            print(f"Filename:     {info['filename']}")
            print(f"Direct URL:   {info['direct_url']}")
            print(f"File Page:    {info['file_page']}")
            print(f"License:      {info['license']}")
            print(f"Attribution:  {info['attribution']}")
            print()

            if args.verify:
                verify_image_url(info['direct_url'])
                print()

            if args.html:
                print("=" * 60)
                print("📝 HTML Snippet")
                print("=" * 60)
                print(generate_html_snippet(info, args.alt))
                print()
        else:
            print("❌ Could not extract image URL")
            sys.exit(1)
    else:
        # Search mode
        search_wikimedia(args.topic, args.count)
        print()
        print("=" * 60)
        print("📋 Next Steps")
        print("=" * 60)
        print("1. Copy the search query above")
        print("2. Run WebSearch in Claude Code")
        print("3. Find File: page URLs in results")
        print("4. Run this script again with --file-page URL")
        print()
        print("Example:")
        print(f"  python3 {sys.argv[0]} --file-page https://commons.wikimedia.org/wiki/File:Image.jpg --verify --html")
        print()

if __name__ == '__main__':
    main()
