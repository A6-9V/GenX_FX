import pytest
import socket
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.session_orchestration import get_android_build_id

def test_get_android_build_id_fallback():
    """
    Test that get_android_build_id falls back to the hostname
    when not on an Android device.
    """
    # On a non-Android system, 'getprop' will fail, and the function
    # should return the hostname.
    expected_hostname = socket.gethostname()
    assert get_android_build_id() == expected_hostname
