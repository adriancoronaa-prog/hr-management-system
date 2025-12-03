#!/usr/bin/env python
"""Script para ejecutar seed_data con SQLite"""
import os
import sys

# Configurar entorno
os.environ.setdefault('USE_SQLITE', 'True')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Agregar el directorio al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.core.management import call_command

if __name__ == '__main__':
    args = sys.argv[1:] if len(sys.argv) > 1 else ['--minimal']
    call_command('seed_data', *args)
