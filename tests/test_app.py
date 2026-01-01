"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

# Create a test client
client = TestClient(app)


class TestActivities:
    """Test activity retrieval"""
    
    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    
    def test_root_redirect(self):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignup:
    """Test signup functionality"""
    
    def test_signup_success(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
    
    def test_signup_duplicate(self):
        """Test signup with email already registered"""
        # michael@mergington.edu is already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_updates_activity(self):
        """Test that signup updates the activities list"""
        # Get initial state
        response = client.get("/activities")
        initial_count = len(response.json()["Tennis Club"]["participants"])
        
        # Sign up new student
        client.post(
            "/activities/Tennis Club/signup?email=signup_test@mergington.edu"
        )
        
        # Check updated state
        response = client.get("/activities")
        updated_count = len(response.json()["Tennis Club"]["participants"])
        assert updated_count == initial_count + 1
        assert "signup_test@mergington.edu" in response.json()["Tennis Club"]["participants"]


class TestUnregister:
    """Test unregister functionality"""
    
    def test_unregister_success(self):
        """Test successful unregister"""
        # First sign up
        client.post(
            "/activities/Drama Club/signup?email=unregister_test@mergington.edu"
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Drama Club/unregister?email=unregister_test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered unregister_test@mergington.edu from Drama Club" in data["message"]
    
    def test_unregister_not_signed_up(self):
        """Test unregister when student is not signed up"""
        response = client.delete(
            "/activities/Art Studio/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_updates_activity(self):
        """Test that unregister updates the activities list"""
        test_email = "unregister_update_test@mergington.edu"
        
        # Sign up
        client.post(
            f"/activities/Robotics Club/signup?email={test_email}"
        )
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Robotics Club"]["participants"])
        assert test_email in response.json()["Robotics Club"]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/Robotics Club/unregister?email={test_email}"
        )
        
        # Check updated state
        response = client.get("/activities")
        updated_count = len(response.json()["Robotics Club"]["participants"])
        assert updated_count == initial_count - 1
        assert test_email not in response.json()["Robotics Club"]["participants"]
