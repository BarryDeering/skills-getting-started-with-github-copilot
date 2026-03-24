"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src import app as app_module
    
    # Save original activities
    original_activities = {
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
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for varsity and intramural play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["marcus@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Learn and play recreational soccer",
            "schedule": "Tuesdays and Thursdays, 3:45 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and digital art techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["clara@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and improv activities",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["ryan@mergington.edu", "avery@mergington.edu"]
        },
        "Debate Team": {
            "description": "Compete in academic debates and develop argumentation skills",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific discoveries",
            "schedule": "Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 20,
            "participants": ["jake@mergington.edu", "maya@mergington.edu"]
        }
    }
    
    # Reset app activities
    app_module.activities.clear()
    app_module.activities.update(original_activities)
    
    yield
    
    # Clean up after test
    app_module.activities.clear()
    app_module.activities.update(original_activities)


# Tests for GET /activities
class TestGetActivities:
    """Test cases for retrieving the list of activities"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities with correct structure"""
        # Arrange
        # (State is already set up by the reset_activities fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == 9
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_contains_chess_club(self, client, reset_activities):
        """Test that Chess Club is in the activities list"""
        # Arrange
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_max = 12
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "Chess Club" in data
        assert data["Chess Club"]["max_participants"] == expected_max
        assert data["Chess Club"]["participants"] == expected_participants


# Tests for GET /
class TestRootRedirect:
    """Test cases for the root endpoint redirect"""
    
    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html"""
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


# Tests for POST /activities/{activity_name}/signup
class TestSignup:
    """Test cases for signing up for an activity"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newuser@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={new_email}"
        )
        data = response.json()
        
        # Assert - Response is successful
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert new_email in data["message"]
        
        # Assert - Participant was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that signing up with an already registered email returns error"""
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={existing_email}"
        )
        error_detail = response.json()["detail"]
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in error_detail.lower()
    
    def test_signup_invalid_activity(self, client, reset_activities):
        """Test that signup for non-existent activity returns 404"""
        # Arrange
        invalid_activity = "Invalid Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity.replace(' ', '%20')}/signup?email={test_email}"
        )
        error_detail = response.json()["detail"]
        
        # Assert
        assert response.status_code == 404
        assert "not found" in error_detail.lower()
    
    def test_signup_multiple_participants(self, client, reset_activities):
        """Test that multiple different participants can sign up"""
        # Arrange
        activity_name = "Programming Class"
        new_emails = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]
        
        # Act
        for email in new_emails:
            response = client.post(
                f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Assert - All participants were added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        
        for email in new_emails:
            assert email in participants


# Tests for DELETE /activities/{activity_name}/signup
class TestUnregister:
    """Test cases for unregistering from an activity"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Verify participant exists
        activities = client.get("/activities").json()
        assert email_to_remove in activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email_to_remove}"
        )
        
        # Assert - Response is successful
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Assert - Participant was actually removed
        activities = client.get("/activities").json()
        assert email_to_remove not in activities[activity_name]["participants"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test that unregistering a non-participant returns error"""
        # Arrange
        activity_name = "Chess Club"
        unregistered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={unregistered_email}"
        )
        error_detail = response.json()["detail"]
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in error_detail.lower()
    
    def test_unregister_invalid_activity(self, client, reset_activities):
        """Test that unregistering from non-existent activity returns 404"""
        # Arrange
        invalid_activity = "Invalid Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity.replace(' ', '%20')}/signup?email={test_email}"
        )
        error_detail = response.json()["detail"]
        
        # Assert
        assert response.status_code == 404
        assert "not found" in error_detail.lower()
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signup followed by unregister"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "testuser@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200
        
        # Assert - Participant was added
        activities = client.get("/activities").json()
        assert test_email in activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={test_email}"
        )
        assert unregister_response.status_code == 200
        
        # Assert - Participant was removed
        activities = client.get("/activities").json()
        assert test_email not in activities[activity_name]["participants"]


# Tests for participant count accuracy
class TestParticipantCounts:
    """Test cases for verifying participant counts"""
    
    def test_participant_count_after_signup(self, client, reset_activities):
        """Test that participant count increases after signup"""
        # Arrange
        activity_name = "Chess Club"
        new_email = "newuser@mergington.edu"
        activities = client.get("/activities").json()
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={new_email}"
        )
        
        # Assert
        updated_activities = client.get("/activities").json()
        new_count = len(updated_activities[activity_name]["participants"])
        assert new_count == initial_count + 1
    
    def test_participant_count_after_unregister(self, client, reset_activities):
        """Test that participant count decreases after unregister"""
        # Arrange
        activity_name = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        activities = client.get("/activities").json()
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email_to_remove}"
        )
        
        # Assert
        updated_activities = client.get("/activities").json()
        new_count = len(updated_activities[activity_name]["participants"])
        assert new_count == initial_count - 1
    
    def test_max_participants_not_enforced(self, client, reset_activities):
        """Test that we can exceed max_participants (current behavior)"""
        # Arrange
        activity_name = "Art Studio"
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities[activity_name]["participants"])
        max_capacity = initial_activities[activity_name]["max_participants"]
        num_new_signups = max_capacity + 2
        
        # Act - Sign up more participants than max_participants allows
        for i in range(num_new_signups):
            response = client.post(
                f"/activities/{activity_name.replace(' ', '%20')}/signup?email=user{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Assert - All signups were accepted despite exceeding max
        final_activities = client.get("/activities").json()
        final_count = len(final_activities[activity_name]["participants"])
        assert final_count == initial_count + num_new_signups
        assert final_count > max_capacity
