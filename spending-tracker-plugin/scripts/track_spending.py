#!/usr/bin/env python3
"""
Claude Code Spending Tracker
Tracks API spending per day and per hour with thread-safe file locking.
"""

import os
import sys
import json
import fcntl
import contextlib
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# Default configuration
# data_dir can be overridden via --data-dir argument or SPENDING_TRACKER_DATA_DIR env var
DEFAULT_DATA_DIR = os.path.expanduser("~/.claude/spending_data")
CONFIG = {
    "data_dir": os.getenv("SPENDING_TRACKER_DATA_DIR", DEFAULT_DATA_DIR),
    "retention_days": 30,  # Keep data for 30 days
    "lock_timeout": 5,  # Max 5 seconds to acquire lock
    "decimal_places": 8,  # Precision for cost tracking
    "enable_cleanup": True,  # Auto-cleanup old data
}


@contextlib.contextmanager
def file_lock(file_path):
    """Context manager for file locking using fcntl"""
    lock_file_path = file_path + '.lock'
    lock_file = None
    try:
        lock_file = open(lock_file_path, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        if lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                lock_file.close()
            except:
                pass


def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    data_dir = Path(CONFIG["data_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def read_json(file_path):
    """Read JSON file with error handling"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Error reading {file_path}: {e}", file=sys.stderr)
        return {}
    return {}


def write_json(file_path, data):
    """Write JSON file with error handling"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except IOError as e:
        print(f"Error: Cannot write to {file_path}: {e}", file=sys.stderr)
        return False


def get_daily_key(dt=None):
    """Get daily key in format YYYY-MM-DD"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d")


def get_hourly_key(dt=None):
    """Get hourly key in format YYYY-MM-DDTHH:00"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%dT%H:00")


def cleanup_old_data(data, days=30):
    """Remove entries older than specified days"""
    if not CONFIG["enable_cleanup"]:
        return data

    cutoff_date = datetime.now() - timedelta(days=days)
    cleaned_data = {}

    for key, value in data.items():
        try:
            # Parse the key date (handles both YYYY-MM-DD and YYYY-MM-DDTHH:00)
            key_date = datetime.fromisoformat(key.split('T')[0])
            if key_date >= cutoff_date:
                cleaned_data[key] = value
        except (ValueError, IndexError):
            # Keep entries with invalid dates (better safe than sorry)
            cleaned_data[key] = value

    return cleaned_data


def read_session_state():
    """Read session state with error handling"""
    data_dir = ensure_data_dir()
    session_file = data_dir / 'session_state.json'
    return read_json(session_file)


def write_session_state(data):
    """Write session state with error handling"""
    data_dir = ensure_data_dir()
    session_file = data_dir / 'session_state.json'
    return write_json(session_file, data)


def cleanup_old_sessions(session_data, hours=24):
    """Remove session entries older than specified hours"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    cleaned_data = {}

    for session_id, session_info in session_data.items():
        try:
            last_updated = datetime.fromisoformat(session_info.get("last_updated", ""))
            if last_updated >= cutoff_time:
                cleaned_data[session_id] = session_info
        except (ValueError, TypeError):
            # Keep sessions with invalid timestamps
            cleaned_data[session_id] = session_info

    return cleaned_data


def add_cost_with_session(session_id, new_total_cost, period_type='both'):
    """
    Add cost to tracking with session-based delta calculation

    Args:
        session_id: Unique session identifier
        new_total_cost: Current cumulative cost for this session
        period_type: 'daily', 'hourly', or 'both'

    Returns:
        delta: Amount actually added (0 if no new spending)
    """
    data_dir = ensure_data_dir()
    session_file = data_dir / 'session_state.json'

    # Lock session state file for reading/updating
    with file_lock(str(session_file)):
        session_data = read_session_state()

        # Get last known cost for this session
        last_cost = session_data.get(session_id, {}).get("last_cost", 0.0)

        # Calculate delta (only new spending since last update)
        delta = new_total_cost - last_cost

        if delta > 0:
            # Add only the delta to tracking
            add_cost(delta, period_type)

            # Update session state
            session_data[session_id] = {
                "last_cost": new_total_cost,
                "last_updated": datetime.now().isoformat(),
                "total_increments": session_data.get(session_id, {}).get("total_increments", 0) + 1
            }

            # Cleanup old sessions
            session_data = cleanup_old_sessions(session_data, hours=24)

            write_session_state(session_data)

            return delta
        elif delta < 0:
            # Cost went down (shouldn't happen, but handle gracefully)
            # Reset session to new cost
            session_data[session_id] = {
                "last_cost": new_total_cost,
                "last_updated": datetime.now().isoformat(),
                "total_increments": 0
            }
            write_session_state(session_data)
            return 0.0

        return 0.0  # No change in cost


def add_cost(cost_increment, period_type='both'):
    """
    Add cost to tracking files

    Args:
        cost_increment: Amount to add (in USD)
        period_type: 'daily', 'hourly', or 'both'
    """
    data_dir = ensure_data_dir()

    # Process daily tracking
    if period_type in ['daily', 'both']:
        daily_file = data_dir / 'daily.json'
        with file_lock(str(daily_file)):
            daily_data = read_json(daily_file)
            daily_key = get_daily_key()

            if daily_key not in daily_data:
                daily_data[daily_key] = {
                    "total_cost": 0.0,
                    "sessions": 0,
                    "last_updated": datetime.now().isoformat()
                }

            daily_data[daily_key]["total_cost"] += cost_increment
            daily_data[daily_key]["sessions"] += 1
            daily_data[daily_key]["last_updated"] = datetime.now().isoformat()

            # Cleanup old data
            daily_data = cleanup_old_data(daily_data, CONFIG["retention_days"])

            write_json(daily_file, daily_data)

    # Process hourly tracking
    if period_type in ['hourly', 'both']:
        hourly_file = data_dir / 'hourly.json'
        with file_lock(str(hourly_file)):
            hourly_data = read_json(hourly_file)
            hourly_key = get_hourly_key()

            if hourly_key not in hourly_data:
                hourly_data[hourly_key] = {
                    "total_cost": 0.0,
                    "sessions": 0,
                    "last_updated": datetime.now().isoformat()
                }

            hourly_data[hourly_key]["total_cost"] += cost_increment
            hourly_data[hourly_key]["sessions"] += 1
            hourly_data[hourly_key]["last_updated"] = datetime.now().isoformat()

            # Cleanup old data
            hourly_data = cleanup_old_data(hourly_data, CONFIG["retention_days"])

            write_json(hourly_file, hourly_data)


def get_totals():
    """Get current daily and hourly totals"""
    data_dir = ensure_data_dir()

    # Get daily total
    daily_file = data_dir / 'daily.json'
    daily_total = 0.0
    daily_date = get_daily_key()

    with file_lock(str(daily_file)):
        daily_data = read_json(daily_file)
        if daily_date in daily_data:
            daily_total = daily_data[daily_date].get("total_cost", 0.0)

    # Get hourly total
    hourly_file = data_dir / 'hourly.json'
    hourly_total = 0.0
    hourly_period = get_hourly_key()

    with file_lock(str(hourly_file)):
        hourly_data = read_json(hourly_file)
        if hourly_period in hourly_data:
            hourly_total = hourly_data[hourly_period].get("total_cost", 0.0)

    return {
        "daily_total": daily_total,
        "hourly_total": hourly_total,
        "daily_date": daily_date,
        "hourly_period": hourly_period,
        "success": True
    }


def reset_data(confirm=False):
    """Reset all tracking data"""
    if not confirm:
        print("Error: Must pass --confirm to reset data", file=sys.stderr)
        return False

    data_dir = ensure_data_dir()
    daily_file = data_dir / 'daily.json'
    hourly_file = data_dir / 'hourly.json'

    with file_lock(str(daily_file)):
        write_json(daily_file, {})

    with file_lock(str(hourly_file)):
        write_json(hourly_file, {})

    print("All tracking data reset successfully")
    return True


def show_stats():
    """Display statistics about tracked spending"""
    data_dir = ensure_data_dir()

    # Daily stats
    daily_file = data_dir / 'daily.json'
    with file_lock(str(daily_file)):
        daily_data = read_json(daily_file)

    # Hourly stats
    hourly_file = data_dir / 'hourly.json'
    with file_lock(str(hourly_file)):
        hourly_data = read_json(hourly_file)

    print("=== Spending Statistics ===")
    print(f"\nDaily Tracking:")
    print(f"  Total days tracked: {len(daily_data)}")
    if daily_data:
        total_all_days = sum(d.get("total_cost", 0) for d in daily_data.values())
        print(f"  Total across all days: ${total_all_days:.4f}")
        print(f"  Average per day: ${total_all_days/len(daily_data):.4f}")

    print(f"\nHourly Tracking:")
    print(f"  Total hours tracked: {len(hourly_data)}")
    if hourly_data:
        total_all_hours = sum(h.get("total_cost", 0) for h in hourly_data.values())
        print(f"  Total across all hours: ${total_all_hours:.4f}")
        print(f"  Average per hour: ${total_all_hours/len(hourly_data):.4f}")

    print(f"\nCurrent Period:")
    totals = get_totals()
    print(f"  Today ({totals['daily_date']}): ${totals['daily_total']:.4f}")
    print(f"  This hour ({totals['hourly_period']}): ${totals['hourly_total']:.4f}")


def main():
    parser = argparse.ArgumentParser(description='Track Claude Code API spending')

    # Global argument for all subcommands
    parser.add_argument('--data-dir', type=str,
                       help='Directory to store spending data (default: ~/.claude/spending_data)')

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add command (legacy - adds cost directly without session tracking)
    add_parser = subparsers.add_parser('add', help='Add cost to tracking')
    add_parser.add_argument('--cost', type=float, required=True, help='Cost to add in USD')
    add_parser.add_argument('--period', choices=['daily', 'hourly', 'both'],
                           default='both', help='Period to track')

    # Add-session command (new - adds cost with session-based delta tracking)
    add_session_parser = subparsers.add_parser('add-session', help='Add cost with session tracking')
    add_session_parser.add_argument('--session-id', type=str, required=True, help='Session identifier')
    add_session_parser.add_argument('--cost', type=float, required=True, help='Current cumulative session cost in USD')
    add_session_parser.add_argument('--period', choices=['daily', 'hourly', 'both'],
                                    default='both', help='Period to track')

    # Get command
    get_parser = subparsers.add_parser('get', help='Get current totals')
    get_parser.add_argument('--format', choices=['json', 'text'],
                           default='json', help='Output format')

    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset all data')
    reset_parser.add_argument('--confirm', action='store_true',
                             help='Confirm reset operation')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')

    args = parser.parse_args()

    # Override CONFIG if --data-dir provided
    if args.data_dir:
        CONFIG["data_dir"] = os.path.expanduser(args.data_dir)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'add':
            add_cost(args.cost, args.period)
            print(json.dumps({"success": True, "cost_added": args.cost}))

        elif args.command == 'add-session':
            delta = add_cost_with_session(args.session_id, args.cost, args.period)
            print(json.dumps({
                "success": True,
                "session_id": args.session_id,
                "total_cost": args.cost,
                "delta_added": delta
            }))

        elif args.command == 'get':
            totals = get_totals()
            if args.format == 'json':
                print(json.dumps(totals))
            else:
                print(f"Daily: ${totals['daily_total']:.4f}")
                print(f"Hourly: ${totals['hourly_total']:.4f}")

        elif args.command == 'reset':
            reset_data(args.confirm)

        elif args.command == 'stats':
            show_stats()

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
