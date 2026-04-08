import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects?
    # Actually, RedirectResponse returns 307, but TestClient follows by default?
    # Let me check: FastAPI RedirectResponse returns 307, but TestClient follows redirects unless follow_redirects=False
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    """Test signup when already signed up"""
    # First signup
    client.post("/activities/Programming Class/signup?email=duplicate@example.com")
    # Try again
    response = client.post("/activities/Programming Class/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" in data["detail"]


def test_unregister_success():
    """Test successful unregister from an activity"""
    # First sign up
    client.post("/activities/Gym Class/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Gym Class/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Gym Class" in data["message"]


def test_unregister_activity_not_found():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    """Test unregister when not signed up"""
    response = client.delete("/activities/Basketball Team/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is not signed up for this activity" in data["detail"]