"""
You call the setup_tests() function from this module at the beginning of each test file.
It is required for unittest to work properly
"""
import os
import django

def setup_tests():
    """This is required for unittest to work properly"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram.settings')
    django.setup()
