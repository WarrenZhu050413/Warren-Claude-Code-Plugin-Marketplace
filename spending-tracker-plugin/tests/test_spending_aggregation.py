#!/usr/bin/env python3
"""
Test suite for spending aggregation from canonical hourly data.

Tests verify that:
1. Hourly data is the canonical source of truth
2. Daily totals are computed by summing hourly data
3. Weekly totals are computed by summing hourly data
4. No independent counters that can drift
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import track_spending
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import track_spending


class TestSpendingAggregation(unittest.TestCase):
    """Test that daily and weekly are computed from hourly data."""

    def setUp(self):
        """Create temporary data directory for each test."""
        self.test_dir = tempfile.mkdtemp()
        track_spending.CONFIG["data_dir"] = self.test_dir
        track_spending.CONFIG["enable_cleanup"] = False  # Don't cleanup during tests

    def tearDown(self):
        """Remove temporary data directory."""
        shutil.rmtree(self.test_dir)

    def test_daily_is_sum_of_hourly_entries(self):
        """Daily total should equal sum of all hourly entries for that day."""
        # Add spending across multiple hours in the same day
        session_id = "test-session-1"

        # Hour 1: $10
        track_spending.add_cost(10.0, period_type='hourly')

        # Hour 2: $20
        track_spending.add_cost(20.0, period_type='hourly')

        # Hour 3: $30
        track_spending.add_cost(30.0, period_type='hourly')

        # Daily should be computed as sum: $60
        totals = track_spending.get_totals()

        # Read hourly data to compute expected daily
        hourly_file = Path(self.test_dir) / 'hourly.json'
        with open(hourly_file, 'r') as f:
            hourly_data = json.load(f)

        today = track_spending.get_daily_key()
        hourly_for_today = sum(
            entry["total_cost"]
            for key, entry in hourly_data.items()
            if key.startswith(today)
        )

        self.assertAlmostEqual(totals['daily_total'], hourly_for_today, places=2)
        self.assertAlmostEqual(totals['daily_total'], 60.0, places=2)

    def test_weekly_is_sum_of_hourly_entries(self):
        """Weekly total should equal sum of all hourly entries for that week."""
        # Add spending across multiple hours
        track_spending.add_cost(10.0, period_type='hourly')
        track_spending.add_cost(20.0, period_type='hourly')
        track_spending.add_cost(15.0, period_type='hourly')

        totals = track_spending.get_totals()

        # Read hourly data to compute expected weekly
        hourly_file = Path(self.test_dir) / 'hourly.json'
        with open(hourly_file, 'r') as f:
            hourly_data = json.load(f)

        # Get current week
        current_week = track_spending.get_weekly_key()

        # Sum all hourly entries for this week
        hourly_for_week = sum(
            entry["total_cost"]
            for key, entry in hourly_data.items()
            if self._hourly_key_in_week(key, current_week)
        )

        self.assertAlmostEqual(totals['weekly_total'], hourly_for_week, places=2)
        self.assertAlmostEqual(totals['weekly_total'], 45.0, places=2)

    def test_no_drift_between_aggregations(self):
        """
        Even if daily/weekly files exist, they should be ignored.
        Only hourly data should be used for computing totals.
        """
        # Add hourly data
        track_spending.add_cost(100.0, period_type='hourly')

        # Manually corrupt daily and weekly files with wrong values
        daily_file = Path(self.test_dir) / 'daily.json'
        weekly_file = Path(self.test_dir) / 'weekly.json'

        today = track_spending.get_daily_key()
        this_week = track_spending.get_weekly_key()

        # Write incorrect values
        with open(daily_file, 'w') as f:
            json.dump({today: {"total_cost": 999.0, "sessions": 1}}, f)

        with open(weekly_file, 'w') as f:
            json.dump({this_week: {"total_cost": 888.0, "sessions": 1}}, f)

        # Get totals - should use hourly data, not corrupted daily/weekly
        totals = track_spending.get_totals()

        self.assertAlmostEqual(totals['daily_total'], 100.0, places=2)
        self.assertAlmostEqual(totals['weekly_total'], 100.0, places=2)
        self.assertNotEqual(totals['daily_total'], 999.0)
        self.assertNotEqual(totals['weekly_total'], 888.0)

    def test_session_based_tracking_only_updates_hourly(self):
        """Session-based delta tracking should only update hourly data."""
        session_id = "test-session-abc"

        # First call: add $50
        delta1 = track_spending.add_cost_with_session(session_id, 50.0)
        self.assertAlmostEqual(delta1, 50.0, places=2)

        # Second call: total is now $75 (delta = $25)
        delta2 = track_spending.add_cost_with_session(session_id, 75.0)
        self.assertAlmostEqual(delta2, 25.0, places=2)

        # Verify only hourly file exists and has correct total
        hourly_file = Path(self.test_dir) / 'hourly.json'
        self.assertTrue(hourly_file.exists())

        with open(hourly_file, 'r') as f:
            hourly_data = json.load(f)

        total_hourly = sum(entry["total_cost"] for entry in hourly_data.values())
        self.assertAlmostEqual(total_hourly, 75.0, places=2)

        # Daily and weekly should be computed from hourly
        totals = track_spending.get_totals()
        self.assertAlmostEqual(totals['daily_total'], 75.0, places=2)
        self.assertAlmostEqual(totals['weekly_total'], 75.0, places=2)

    def _hourly_key_in_week(self, hourly_key, week_key):
        """Helper to check if an hourly key belongs to a given week."""
        try:
            # Parse hourly key (format: YYYY-MM-DDTHH:00)
            dt = datetime.fromisoformat(hourly_key.replace('T', ' ').replace(':00', ':00:00'))
            year, week, _ = dt.isocalendar()
            entry_week = f"{year}-W{week:02d}"
            return entry_week == week_key
        except:
            return False


class TestBackwardCompatibility(unittest.TestCase):
    """Test that existing data files are migrated correctly."""

    def setUp(self):
        """Create temporary data directory with legacy data."""
        self.test_dir = tempfile.mkdtemp()
        track_spending.CONFIG["data_dir"] = self.test_dir
        track_spending.CONFIG["enable_cleanup"] = False

    def tearDown(self):
        """Remove temporary data directory."""
        shutil.rmtree(self.test_dir)

    def test_migrate_existing_daily_and_weekly_to_hourly(self):
        """
        Existing daily/weekly files should be converted to hourly entries.
        This ensures no data loss during migration.
        """
        # Create legacy daily and weekly files
        daily_file = Path(self.test_dir) / 'daily.json'
        weekly_file = Path(self.test_dir) / 'weekly.json'

        today = track_spending.get_daily_key()
        this_week = track_spending.get_weekly_key()

        # Legacy data: daily has $100, weekly has $100
        with open(daily_file, 'w') as f:
            json.dump({
                today: {"total_cost": 100.0, "sessions": 10, "last_updated": datetime.now().isoformat()}
            }, f)

        with open(weekly_file, 'w') as f:
            json.dump({
                this_week: {"total_cost": 100.0, "sessions": 10, "last_updated": datetime.now().isoformat()}
            }, f)

        # Call migration function (to be implemented)
        track_spending.migrate_legacy_data()

        # Verify hourly data now exists
        hourly_file = Path(self.test_dir) / 'hourly.json'
        self.assertTrue(hourly_file.exists())

        # Verify totals are preserved
        totals = track_spending.get_totals()
        self.assertAlmostEqual(totals['daily_total'], 100.0, places=2)


if __name__ == '__main__':
    unittest.main()
