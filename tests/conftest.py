"""Pytest configuration and shared fixtures for the test suite."""

import pytest
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Fixture providing a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_activity_data():
    """Fixture providing sample activity and student data for tests."""
    return {
        "activities": {
            "Chess Club": {
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            "Programming Class": {
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
            }
        },
        "new_student_email": "newstudent@mergington.edu",
        "existing_student_email": "michael@mergington.edu"
    }
