"""Test suite for activities endpoints using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities."""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Basketball Team"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert len(data) > 0
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_response_structure(self, client):
        """Test that activity response has correct structure."""
        # Arrange
        expected_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity_info = data["Chess Club"]
        
        # Assert
        for field in expected_fields:
            assert field in activity_info
        assert isinstance(activity_info["participants"], list)

    def test_get_activities_participants_list(self, client):
        """Test that each activity has a participants list."""
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_info in data.items():
            assert isinstance(activity_info["participants"], list)
            for participant in activity_info["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Should be an email


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_for_activity(self, client):
        """Test that a new student can sign up for an activity."""
        # Arrange
        activity_name = "Chess Club"
        new_email = "testuser@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]

    def test_signup_verification(self, client):
        """Test that after signup, student appears in activity participants."""
        # Arrange
        activity_name = "Programming Class"
        new_email = "verifyuser@mergington.edu"
        
        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        
        # Assert
        assert signup_response.status_code == 200
        assert new_email in participants

    def test_signup_duplicate_student_fails(self, client):
        """Test that a student cannot sign up twice for the same activity."""
        # Arrange
        activity_name = "Art Club"
        email = "duplicate@mergington.edu"
        
        # Act - First signup succeeds
        first_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Second signup attempt
        second_signup = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        second_data = second_signup.json()
        
        # Assert
        assert first_signup.status_code == 200
        assert second_signup.status_code == 400
        assert "already signed up" in second_data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup fails for a non-existent activity."""
        # Arrange
        nonexistent_activity = "Nonexistent Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"].lower()

    def test_signup_with_existing_participant(self, client):
        """Test signup with an email that already exists in the activity."""
        # Arrange
        activities_response = client.get("/activities")
        activities = activities_response.json()
        existing_email = None
        activity_name = None
        
        for act_name, act_info in activities.items():
            if act_info["participants"]:
                existing_email = act_info["participants"][0]
                activity_name = act_name
                break
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""

    def test_remove_existing_participant(self, client):
        """Test that an existing participant can be removed from an activity."""
        # Arrange
        activity_name = "Music Ensemble"
        email = "toremove@mergington.edu"
        
        # Act - First add a participant
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Then remove them
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "message" in data
        assert email in data["message"]

    def test_remove_participant_verification(self, client):
        """Test that after removal, participant is gone from activity."""
        # Arrange
        activity_name = "Debate Team"
        email = "verifyremove@mergington.edu"
        
        # Act - Add participant
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Remove participant
        client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Act - Verify they're gone
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        
        # Assert
        assert email not in participants

    def test_remove_nonexistent_participant_fails(self, client):
        """Test that removing a non-existent participant fails."""
        # Arrange
        activity_name = "Robotics Workshop"
        nonexistent_email = "notreal@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"].lower()

    def test_remove_from_nonexistent_activity_fails(self, client):
        """Test that removing from a non-existent activity fails."""
        # Arrange
        nonexistent_activity = "Fake Activity"
        email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"].lower()

    def test_remove_participant_twice_fails(self, client):
        """Test that removing the same participant twice fails."""
        # Arrange
        activity_name = "Soccer Club"
        email = "twiceremove@mergington.edu"
        
        # Act - Add and remove once
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        first_removal = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Act - Try to remove again
        second_removal = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Assert
        assert first_removal.status_code == 200
        assert second_removal.status_code == 404


class TestRootRedirect:
    """Tests for the root endpoint redirect."""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to the static files."""
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_with_follow_redirects(self, client):
        """Test that following redirects from root returns static content."""
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert - Should successfully retrieve static content or redirect
        assert response.status_code in [200, 307]
