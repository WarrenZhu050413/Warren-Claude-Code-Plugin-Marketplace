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


def get_weekly_key(dt=None):
    """Get weekly key in format YYYY-Www (ISO week format)"""
    if dt is None:
        dt = datetime.now()
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def cleanup_old_data(data, days=30):
    """Remove entries older than specified days (only for hourly data)"""
    if not CONFIG["enable_cleanup"]:
        return data

    cutoff_date = datetime.now() - timedelta(days=days)
    cleaned_data = {}

    for key, value in data.items():
        try:
            # Parse hourly key format: YYYY-MM-DDTHH:00
            if 'T' in key:
                key_date = datetime.fromisoformat(key.replace(':00', ':00:00'))
            else:
                # Legacy format: YYYY-MM-DD
                key_date = datetime.fromisoformat(key)

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


def add_cost_with_session(session_id, new_total_cost, period_type='all'):
    """
    Add cost to tracking with session-based delta calculation

    Args:
        session_id: Unique session identifier
        new_total_cost: Current cumulative cost for this session
        period_type: 'daily', 'hourly', 'weekly', or 'all'

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


def add_cost(cost_increment, period_type='all'):
    """
    Add cost to tracking (only updates hourly - canonical source).

    Args:
        cost_increment: Amount to add (in USD)
        period_type: Legacy parameter for backward compatibility (ignored, always updates hourly)

    Note: Hourly data is the canonical source. Daily and weekly are computed on-demand.
    """
    data_dir = ensure_data_dir()

    # Only update hourly data (canonical source)
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
    """
    Get current daily, weekly, and hourly totals.

    Hourly data is the canonical source of truth.
    Daily and weekly totals are computed by aggregating hourly data.
    """
    data_dir = ensure_data_dir()
    hourly_file = data_dir / 'hourly.json'

    daily_date = get_daily_key()
    weekly_period = get_weekly_key()
    hourly_period = get_hourly_key()

    # Read hourly data (canonical source)
    with file_lock(str(hourly_file)):
        hourly_data = read_json(hourly_file)

    # Compute current hour total
    hourly_total = hourly_data.get(hourly_period, {}).get("total_cost", 0.0)

    # Compute daily total by summing all hourly entries for today
    daily_total = sum(
        entry.get("total_cost", 0.0)
        for key, entry in hourly_data.items()
        if key.startswith(daily_date)
    )

    # Compute weekly total by summing all hourly entries for this week
    weekly_total = 0.0
    for key, entry in hourly_data.items():
        try:
            # Parse hourly key (format: YYYY-MM-DDTHH:00)
            dt = datetime.fromisoformat(key.replace('T', ' ').replace(':00', ':00:00'))
            year, week, _ = dt.isocalendar()
            entry_week = f"{year}-W{week:02d}"
            if entry_week == weekly_period:
                weekly_total += entry.get("total_cost", 0.0)
        except (ValueError, AttributeError):
            # Skip entries with invalid keys
            continue

    return {
        "daily_total": daily_total,
        "weekly_total": weekly_total,
        "hourly_total": hourly_total,
        "daily_date": daily_date,
        "weekly_period": weekly_period,
        "hourly_period": hourly_period,
        "success": True
    }


def migrate_legacy_data():
    """
    Migrate legacy daily/weekly data to hourly format.

    Reads existing daily.json and creates corresponding hourly entries.
    This ensures no data loss when switching to aggregation-based approach.
    """
    data_dir = ensure_data_dir()
    daily_file = data_dir / 'daily.json'
    hourly_file = data_dir / 'hourly.json'

    # Read legacy daily data
    with file_lock(str(daily_file)):
        daily_data = read_json(daily_file)

    if not daily_data:
        # No legacy data to migrate
        return

    # Read existing hourly data
    with file_lock(str(hourly_file)):
        hourly_data = read_json(hourly_file)

        # For each day in legacy data, create an hourly entry
        # We'll use noon (12:00) as a reasonable default hour
        for day_key, day_entry in daily_data.items():
            hourly_key = f"{day_key}T12:00"

            # Only migrate if this hourly entry doesn't already exist
            if hourly_key not in hourly_data:
                hourly_data[hourly_key] = {
                    "total_cost": day_entry.get("total_cost", 0.0),
                    "sessions": day_entry.get("sessions", 0),
                    "last_updated": day_entry.get("last_updated", datetime.now().isoformat()),
                    "migrated_from_daily": True
                }

        write_json(hourly_file, hourly_data)

    print(f"Migrated {len(daily_data)} daily entries to hourly format")


def reset_data(confirm=False):
    """Reset all tracking data"""
    if not confirm:
        print("Error: Must pass --confirm to reset data", file=sys.stderr)
        return False

    data_dir = ensure_data_dir()
    daily_file = data_dir / 'daily.json'
    weekly_file = data_dir / 'weekly.json'
    hourly_file = data_dir / 'hourly.json'

    with file_lock(str(daily_file)):
        write_json(daily_file, {})

    with file_lock(str(weekly_file)):
        write_json(weekly_file, {})

    with file_lock(str(hourly_file)):
        write_json(hourly_file, {})

    print("All tracking data reset successfully")
    return True


def show_stats():
    """Display statistics about tracked spending (computed from hourly data)"""
    data_dir = ensure_data_dir()
    hourly_file = data_dir / 'hourly.json'

    # Read hourly data (canonical source)
    with file_lock(str(hourly_file)):
        hourly_data = read_json(hourly_file)

    if not hourly_data:
        print("No spending data tracked yet")
        return

    # Aggregate by day and week
    daily_totals = {}
    weekly_totals = {}

    for key, entry in hourly_data.items():
        try:
            # Parse hourly key: YYYY-MM-DDTHH:00
            dt = datetime.fromisoformat(key.replace('T', ' ').replace(':00', ':00:00'))
            day_key = dt.strftime("%Y-%m-%d")
            year, week, _ = dt.isocalendar()
            week_key = f"{year}-W{week:02d}"

            cost = entry.get("total_cost", 0.0)

            # Aggregate by day
            if day_key not in daily_totals:
                daily_totals[day_key] = 0.0
            daily_totals[day_key] += cost

            # Aggregate by week
            if week_key not in weekly_totals:
                weekly_totals[week_key] = 0.0
            weekly_totals[week_key] += cost

        except (ValueError, AttributeError):
            continue

    # Calculate statistics
    total_all_hours = sum(h.get("total_cost", 0) for h in hourly_data.values())

    print("=== Spending Statistics ===")
    print(f"\nHourly Tracking (Canonical):")
    print(f"  Total hours tracked: {len(hourly_data)}")
    print(f"  Total across all hours: ${total_all_hours:.4f}")
    print(f"  Average per hour: ${total_all_hours/len(hourly_data):.4f}")

    print(f"\nDaily Aggregation (from hourly):")
    print(f"  Total days tracked: {len(daily_totals)}")
    if daily_totals:
        total_all_days = sum(daily_totals.values())
        print(f"  Total across all days: ${total_all_days:.4f}")
        print(f"  Average per day: ${total_all_days/len(daily_totals):.4f}")

    print(f"\nWeekly Aggregation (from hourly):")
    print(f"  Total weeks tracked: {len(weekly_totals)}")
    if weekly_totals:
        total_all_weeks = sum(weekly_totals.values())
        print(f"  Total across all weeks: ${total_all_weeks:.4f}")
        print(f"  Average per week: ${total_all_weeks/len(weekly_totals):.4f}")

    print(f"\nCurrent Period:")
    totals = get_totals()
    print(f"  Today ({totals['daily_date']}): ${totals['daily_total']:.4f}")
    print(f"  This week ({totals['weekly_period']}): ${totals['weekly_total']:.4f}")
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
    add_parser.add_argument('--period', choices=['daily', 'hourly', 'weekly', 'both', 'all'],
                           default='all', help='Period to track')

    # Add-session command (new - adds cost with session-based delta tracking)
    add_session_parser = subparsers.add_parser('add-session', help='Add cost with session tracking')
    add_session_parser.add_argument('--session-id', type=str, required=True, help='Session identifier')
    add_session_parser.add_argument('--cost', type=float, required=True, help='Current cumulative session cost in USD')
    add_session_parser.add_argument('--period', choices=['daily', 'hourly', 'weekly', 'both', 'all'],
                                    default='all', help='Period to track')

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
                print(f"Weekly: ${totals['weekly_total']:.4f}")
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
