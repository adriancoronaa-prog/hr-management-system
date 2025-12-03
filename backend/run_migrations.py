"""Script to run migrations with SQLite"""
import os
import sys

# Set SQLite before importing Django
os.environ['USE_SQLITE'] = 'True'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.core.management import call_command

print("Running migrations with SQLite...")
call_command('migrate')
print("Migrations applied successfully!")
