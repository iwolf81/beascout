"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(scope="session")
def test_data_dir():
    """Return path to test data directory."""
    return Path(__file__).parent / "fixtures"