import pytest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app
from app.main import app

@pytest.fixture
def test_app():
    """Return the FastAPI app for testing."""
    return app
