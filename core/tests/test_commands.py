"""
Test custom Django management commands.
"""

from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase
from psycopg2 import OperationalError as Psycopg2OpError


@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check):
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command("wait_for_db")

        # Check that both databases were checked
        self.assertEqual(patched_check.call_count, 2)
        patched_check.assert_any_call(databases=["default"])
        patched_check.assert_any_call(databases=["mongodb"])

    @patch("time.sleep")
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """Test waiting for database when getting OperationalError."""
        # Simulate errors for both databases
        patched_check.side_effect = (
            [Psycopg2OpError] * 2
            + [OperationalError] * 3
            + [True]  # For default DB
            + [Psycopg2OpError] * 2
            + [OperationalError] * 3
            + [True]  # For mongodb
        )

        call_command("wait_for_db")

        # Check that both databases were checked multiple times
        self.assertEqual(patched_check.call_count, 12)
        # Verify the last calls were for both databases
        patched_check.assert_any_call(databases=["default"])
        patched_check.assert_any_call(databases=["mongodb"])
