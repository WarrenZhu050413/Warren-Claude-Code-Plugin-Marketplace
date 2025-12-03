#!/usr/bin/env python3
"""
Fetch Wikimedia Commons images programmatically using the Wikimedia API.

Usage:
    python3 fetch_wikimedia_image.py "topic" [--count 5] [--json]
    python3 fetch_wikimedia_image.py --file-page URL [--verify] [--html]

Examples:
    # Search and get URLs directly
    python3 fetch_wikimedia_image.py "mofongo puerto rico" --count 3

    # Search with JSON output
    python3 fetch_wikimedia_image.py "Old San Juan street" --json

    # Get URL from specific File: page
    python3 fetch_wikimedia_image.py --file-page "https://commons.wikimedia.org/wiki/File:Mofongo.jpg" --verify --html
"""

import sys
import json
import re
import urllib.request
import urllib.parse
from typing import List, Dict, Optional

WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
# Wikimedia API requires a descriptive User-Agent per their policy
# See: https://www.mediawiki.org/wiki/API:Etiquette
USER_AGENT = "WikimediaImageFetcher/1.0 (ClaudeCode-Plugin; fuchengwarrenzhu@gmail.com)"

def make_api_request(url: str) -> dict:
    """Make a request to the Wikimedia API with proper headers."""
    req = urllib.request.Request(url)
    req.add_header('User-Agent', USER_AGENT)
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode())


def search_wikimedia(topic: str, count: int = 5) -> List[Dict[str, str]]:
    """
    Search Wikimedia Commons for images using the API.
    Returns list of dicts with title, file_page, and direct_url.
    """
    print(f"🔍 Searching Wikimedia Commons for: {topic}")
    print(f"   Looking for top {count} results...\n")

    # Step 1: Search for files
    search_params = {
        'action': 'query',
        'list': 'search',
        'srsearch': topic,
        'srnamespace': '6',  # File namespace
        'srlimit': str(count),
        'format': 'json'
    }

    search_url = f"{WIKIMEDIA_API}?{urllib.parse.urlencode(search_params)}"

    try:
        search_data = make_api_request(search_url)
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []

    if 'query' not in search_data or 'search' not in search_data['query']:
        print("❌ No results found")
        return []

    results = search_data['query']['search']

    if not results:
        print("❌ No results found")
        return []

    print(f"📋 Found {len(results)} results\n")

    # Step 2: Get image URLs for each result
    titles = '|'.join([r['title'] for r in results])

    info_params = {
        'action': 'query',
        'titles': titles,
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'format': 'json'
    }

    info_url = f"{WIKIMEDIA_API}?{urllib.parse.urlencode(info_params)}"

    try:
        info_data = make_api_request(info_url)
    except Exception as e:
        print(f"❌ Failed to get image info: {e}")
        return []

    images = []
    pages = info_data.get('query', {}).get('pages', {})

    for page_id, page_data in pages.items():
        if 'imageinfo' in page_data:
            info = page_data['imageinfo'][0]
            title = page_data.get('title', 'Unknown')
            filename = title.replace('File:', '')

            image = {
                'title': title,
                'filename': filename,
                'direct_url': info.get('url', ''),
                'file_page': f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
                'width': info.get('width', 0),
                'height': info.get('height', 0),
                'mime': info.get('mime', ''),
                'license': 'CC BY-SA (check file page for exact version)',
                'attribution': f'Photo: Wikimedia Commons'
            }
            images.append(image)

    return images


def extract_image_url_from_file_page(file_page_url: str) -> Optional[Dict[str, str]]:
    """
    Extract direct image URL from a Wikimedia Commons File: page.
    Uses the Wikimedia API for reliable extraction.

    Args:
        file_page_url: URL like https://commons.wikimedia.org/wiki/File:Image.jpg

    Returns:
        Dict with: direct_url, filename, license, attribution
    """
    print(f"📥 Extracting image URL from: {file_page_url}")

    # Extract the File: title from URL
    # URL format: https://commons.wikimedia.org/wiki/File:Name.jpg
    try:
        if '/wiki/' in file_page_url:
            title = urllib.parse.unquote(file_page_url.split('/wiki/')[-1])
        else:
            print("   ❌ Invalid Wikimedia Commons URL")
            return None

        # Use API to get direct URL
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'imageinfo',
            'iiprop': 'url|size|mime|extmetadata',
            'format': 'json'
        }

        api_url = f"{WIKIMEDIA_API}?{urllib.parse.urlencode(params)}"

        data = make_api_request(api_url)

        pages = data.get('query', {}).get('pages', {})

        for page_id, page_data in pages.items():
            if 'imageinfo' in page_data:
                info = page_data['imageinfo'][0]
                metadata = info.get('extmetadata', {})

                # Try to get license from metadata
                license_info = metadata.get('LicenseShortName', {}).get('value', 'Check file page')
                artist = metadata.get('Artist', {}).get('value', 'Unknown')
                # Strip HTML tags from artist
                artist_clean = re.sub(r'<[^>]+>', '', artist).strip()

                filename = title.replace('File:', '')

                return {
                    'title': title,
                    'filename': filename,
                    'direct_url': info.get('url', ''),
                    'file_page': file_page_url,
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'mime': info.get('mime', ''),
                    'license': license_info,
                    'artist': artist_clean,
                    'attribution': f'Photo: {artist_clean} via Wikimedia Commons, {license_info}'
                }

        print("   ❌ Could not find image info")
        return None

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def verify_image_url(url: str) -> bool:
    """Verify that an image URL is accessible."""
    print(f"🔍 Verifying URL...")

    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; ImageFetcher/1.0)')

        with urllib.request.urlopen(req, timeout=10) as response:
            content_type = response.headers.get('Content-Type', '')
            status = response.status

            if status == 200 and content_type.startswith('image/'):
                print(f"   ✅ URL verified (HTTP {status}, {content_type})")
                return True
            else:
                print(f"   ⚠️  HTTP {status}, Content-Type: {content_type}")
                return False

    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def generate_html_snippet(image_info: Dict[str, str], alt_text: str = "") -> str:
    """Generate HTML code snippet for embedding the image."""
    alt = alt_text or image_info.get('filename', 'Image')
    return f'''<figure>
  <img src="{image_info['direct_url']}"
       alt="{alt}"
       loading="lazy">
  <figcaption>
    {alt}
    <br><small>{image_info.get('attribution', 'Photo: Wikimedia Commons')}</small>
  </figcaption>
</figure>'''


def generate_react_snippet(image_info: Dict[str, str], alt_text: str = "") -> str:
    """Generate React/JSX code snippet for embedding the image."""
    alt = alt_text or image_info.get('filename', 'Image')
    return f'''<figure>
  <img
    src="{image_info['direct_url']}"
    alt="{alt}"
    loading="lazy"
    style={{{{ maxWidth: '100%', height: 'auto' }}}}
  />
  <figcaption style={{{{ fontSize: '0.85rem', color: '#666', fontStyle: 'italic' }}}}>
    {alt}
    <br />
    <small>{image_info.get('attribution', 'Photo: Wikimedia Commons')}</small>
  </figcaption>
</figure>'''


def print_image_info(info: Dict[str, str]) -> None:
    """Pretty print image information."""
    print()
    print("=" * 60)
    print("📸 Image Information")
    print("=" * 60)
    print(f"Filename:     {info.get('filename', 'N/A')}")
    print(f"Direct URL:   {info.get('direct_url', 'N/A')}")
    print(f"File Page:    {info.get('file_page', 'N/A')}")
    print(f"Dimensions:   {info.get('width', '?')}x{info.get('height', '?')}")
    print(f"MIME Type:    {info.get('mime', 'N/A')}")
    print(f"License:      {info.get('license', 'N/A')}")
    print(f"Attribution:  {info.get('attribution', 'N/A')}")
    print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Fetch Wikimedia Commons images using the API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search for images
  %(prog)s "mofongo puerto rico" --count 5

  # Search and output as JSON
  %(prog)s "Old San Juan colorful" --json

  # Get info from specific file page
  %(prog)s --file-page "https://commons.wikimedia.org/wiki/File:Mofongo.jpg"

  # Get file page info with verification and HTML snippet
  %(prog)s --file-page URL --verify --html --alt "Delicious mofongo"
        """
    )
    parser.add_argument('topic', nargs='?', help='Topic to search for (e.g., "paella valenciana")')
    parser.add_argument('--count', '-n', type=int, default=5, help='Number of results (default: 5)')
    parser.add_argument('--file-page', '-f', help='Direct File: page URL to extract from')
    parser.add_argument('--verify', '-v', action='store_true', help='Verify URL accessibility')
    parser.add_argument('--html', action='store_true', help='Generate HTML snippet')
    parser.add_argument('--react', action='store_true', help='Generate React/JSX snippet')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--alt', default='', help='Alt text for HTML/React snippet')
    parser.add_argument('--urls-only', '-u', action='store_true', help='Only output direct URLs (one per line)')

    args = parser.parse_args()

    # Validate that either topic or --file-page is provided
    if not args.topic and not args.file_page:
        parser.error("Either provide a topic or use --file-page with a File: page URL")

    if args.file_page:
        # Extract from a specific File: page
        info = extract_image_url_from_file_page(args.file_page)

        if info:
            if args.json:
                print(json.dumps(info, indent=2))
            elif args.urls_only:
                print(info['direct_url'])
            else:
                print_image_info(info)

                if args.verify:
                    verify_image_url(info['direct_url'])
                    print()

                if args.html:
                    print("=" * 60)
                    print("📝 HTML Snippet")
                    print("=" * 60)
                    print(generate_html_snippet(info, args.alt))
                    print()

                if args.react:
                    print("=" * 60)
                    print("⚛️  React/JSX Snippet")
                    print("=" * 60)
                    print(generate_react_snippet(info, args.alt))
                    print()
        else:
            print("❌ Could not extract image URL")
            sys.exit(1)
    else:
        # Search mode - now actually searches!
        images = search_wikimedia(args.topic, args.count)

        if not images:
            print("❌ No images found")
            sys.exit(1)

        if args.json:
            print(json.dumps(images, indent=2))
        elif args.urls_only:
            for img in images:
                print(img['direct_url'])
        else:
            for i, img in enumerate(images, 1):
                print(f"[{i}] {img['filename']}")
                print(f"    URL: {img['direct_url']}")
                print(f"    Size: {img.get('width', '?')}x{img.get('height', '?')}")
                print(f"    Page: {img['file_page']}")

                if args.verify:
                    verify_image_url(img['direct_url'])

                print()

            if args.html:
                print("=" * 60)
                print("📝 HTML Snippets")
                print("=" * 60)
                for img in images:
                    print(generate_html_snippet(img, args.alt))
                    print()

            if args.react:
                print("=" * 60)
                print("⚛️  React/JSX Snippets")
                print("=" * 60)
                for img in images:
                    print(generate_react_snippet(img, args.alt))
                    print()


if __name__ == '__main__':
    main()
