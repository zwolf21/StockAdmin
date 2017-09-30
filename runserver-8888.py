#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StockAdmin.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line([__file__,'runserver', '0.0.0.0:8888'])
