"""
Django command to wait for the database to be available.
"""

import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args, **options):
        for alias in settings.DATABASES.keys():
            self.stdout.write(f'⏳ Waiting for database "{alias}"...')
            up = False
            while not up:
                try:
                    # checks connectivity for this alias
                    self.check(databases=[alias])
                    up = True
                except (Psycopg2OpError, OperationalError):
                    self.stdout.write(
                        f'🚧 "{alias}" unavailable, retrying in 1s...'
                    )
                    time.sleep(1)
            self.stdout.write(
                self.style.SUCCESS(f'✅ "{alias}" is available!')
            )
