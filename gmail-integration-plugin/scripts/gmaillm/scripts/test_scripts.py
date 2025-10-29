#!/usr/bin/env python3
"""
Test script to verify all gmaillm automation scripts work correctly.

This script runs basic tests on each automation script to ensure
they are functioning properly.

Usage:
    python scripts/test_scripts.py
"""

import sys
import subprocess
from typing import List, Tuple


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """
    Run a command and return exit code, stdout, stderr.

    Args:
        cmd: Command and arguments as list

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_help_output(script_name: str) -> bool:
    """
    Test that script's --help works.

    Args:
        script_name: Name of script to test

    Returns:
        True if test passed
    """
    print(f"Testing {script_name} --help...")

    cmd = ['python3', f'scripts/{script_name}', '--help']
    exit_code, stdout, stderr = run_command(cmd)

    if exit_code == 0 and 'usage:' in stdout.lower():
        print(f"  ✓ {script_name} --help works")
        return True
    else:
        print(f"  ✗ {script_name} --help failed")
        print(f"    Exit code: {exit_code}")
        print(f"    Stderr: {stderr}")
        return False


def test_email_notifier() -> bool:
    """
    Test email_notifier.py with quiet mode.

    Returns:
        True if test passed
    """
    print("Testing email_notifier.py...")

    cmd = [
        'python3', 'scripts/email_notifier.py',
        '--query', 'in:inbox',
        '--max-results', '1',
        '--quiet'
    ]
    exit_code, stdout, stderr = run_command(cmd)

    if exit_code == 0:
        print(f"  ✓ email_notifier.py works (found {stdout.strip()} emails)")
        return True
    else:
        print(f"  ✗ email_notifier.py failed")
        print(f"    Exit code: {exit_code}")
        print(f"    Stderr: {stderr}")
        return False


def test_inbox_cleanup() -> bool:
    """
    Test inbox_cleanup.py with dry-run.

    Returns:
        True if test passed
    """
    print("Testing inbox_cleanup.py...")

    # Test that it requires at least one action
    cmd = ['python3', 'scripts/inbox_cleanup.py', '--dry-run']
    exit_code, stdout, stderr = run_command(cmd)

    if exit_code != 0 and 'Must specify at least one action' in stderr:
        print("  ✓ inbox_cleanup.py correctly requires action argument")
        return True
    else:
        print("  ✗ inbox_cleanup.py validation failed")
        print(f"    Exit code: {exit_code}")
        print(f"    Stderr: {stderr}")
        return False


def test_process_workflow() -> bool:
    """
    Test process_workflow.py error handling.

    Returns:
        True if test passed
    """
    print("Testing process_workflow.py...")

    # Test with non-existent workflow
    cmd = [
        'python3', 'scripts/process_workflow.py',
        'nonexistent-workflow-test',
        '--dry-run'
    ]
    exit_code, stdout, stderr = run_command(cmd)

    # It should fail since workflow doesn't exist
    if exit_code != 0:
        print("  ✓ process_workflow.py correctly handles missing workflow")
        return True
    else:
        print("  ✗ process_workflow.py should fail for nonexistent workflow")
        return False


def main():
    """Main test runner."""
    print("=" * 60)
    print("GMAILLM Automation Scripts Test Suite")
    print("=" * 60)
    print()

    tests = [
        ('email_notifier.py --help', lambda: test_help_output('email_notifier.py')),
        ('inbox_cleanup.py --help', lambda: test_help_output('inbox_cleanup.py')),
        ('process_workflow.py --help', lambda: test_help_output('process_workflow.py')),
        ('email_notifier.py functionality', test_email_notifier),
        ('inbox_cleanup.py validation', test_inbox_cleanup),
        ('process_workflow.py error handling', test_process_workflow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
