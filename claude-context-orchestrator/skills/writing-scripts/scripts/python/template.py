#!/usr/bin/env python3
"""
Script description here.

Usage:
    python3 template.py input.txt --output results.txt
    python3 template.py --url https://example.com --verify
"""

import sys
import os
import argparse
import logging
import subprocess
from typing import Optional, List, Dict


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with appropriate level."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def process_file(file_path: str) -> Optional[Dict[str, str]]:
    """
    Process a single file.

    Args:
        file_path: Path to file to process

    Returns:
        Dict with results, or None on error
    """
    logging.info(f"Processing file: {file_path}")

    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process content here
        result = {
            'file': file_path,
            'size': len(content),
            'lines': len(content.splitlines())
        }

        logging.debug(f"Processed {result['lines']} lines")
        return result

    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return None


def run_command(cmd: List[str], input_data: Optional[str] = None) -> Optional[str]:
    """
    Run external command safely.

    Args:
        cmd: Command as list of strings
        input_data: Optional input to pipe to command

    Returns:
        Command output or None on error
    """
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed with exit code {e.returncode}")
        logging.error(f"stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        logging.error(f"Command not found: {cmd[0]}")
        return None


def verify_url(url: str) -> bool:
    """
    Verify URL is accessible.

    Args:
        url: URL to check

    Returns:
        True if URL returns HTTP 200
    """
    logging.debug(f"Verifying URL: {url}")

    result = subprocess.run(
        ['curl', '-I', '-s', url],
        capture_output=True,
        text=True
    )

    if 'HTTP/2 200' in result.stdout or 'HTTP/1.1 200' in result.stdout:
        logging.info(f"✅ URL verified: {url}")
        return True

    logging.warning(f"❌ URL not accessible: {url}")
    return False


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description='Script description',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Positional arguments
    parser.add_argument(
        'input',
        nargs='?',
        help='Input file or topic'
    )

    # Optional arguments
    parser.add_argument(
        '--output', '-o',
        help='Output file path'
    )

    parser.add_argument(
        '--url',
        help='Process URL instead of file'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify URLs before processing'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='Number of items to process (default: 5)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force operation without confirmation'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Validate arguments
    if not args.input and not args.url:
        parser.error("Provide either input file or --url")

    # Environment variable example
    api_key = os.getenv('API_KEY')
    if api_key:
        logging.debug("API key found in environment")

    # Main logic
    try:
        if args.url:
            # URL processing mode
            if args.verify and not verify_url(args.url):
                logging.error("URL verification failed")
                return 1

            logging.info(f"Processing URL: {args.url}")
            # Process URL here

        else:
            # File processing mode
            result = process_file(args.input)
            if result is None:
                return 1

            logging.info(f"Processed file: {result}")

            # Save output if specified
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(str(result))
                logging.info(f"Results saved to: {args.output}")

        logging.info("✅ Operation completed successfully")
        return 0

    except KeyboardInterrupt:
        logging.warning("\n⚠️  Operation cancelled by user")
        return 130

    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
