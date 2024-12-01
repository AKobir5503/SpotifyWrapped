#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
"""
import os
import sys

def main():
    """
    The main entry point for Django's command-line utility.

    This function sets the default settings module for the Django application,
    handles import errors, and executes the command-line arguments using Django's
    management tools.

    Raises:
        ImportError: If Django is not installed or not available in the current
                     environment's PYTHONPATH, an ImportError is raised with
                     an appropriate error message.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SpotifyWrapped.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
