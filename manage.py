#!/usr/bin/env python
"""Command-line utility for running Django administrative tasks"""
import os
import sys

def main():
    """Execute administrative tasks for the Django project"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Failed to import Django. Ensure it's installed and "
            "that your PYTHONPATH is properly set. Did you activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
