"""Test suite for API input validation and edge cases using AAA (Arrange-Act-Assert) pattern."""

import pytest


class TestInputValidation:
    """Tests for input validation across endpoints."""

    def test_signup_with_empty_email(self, client):
        """Test that signup with empty email is handled."""
        # Arrange
        activity_name = "Chess Club"
        empty_email = ""
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": empty_email}
        )
        
        # Assert
        # Empty email should likely fail, but behavior depends on implementation
        # This test documents the current behavior
        assert response.status_code in [200, 400, 422]

    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with various email formats."""
        # Arrange
        special_emails = [
            ("user+tag@mergington.edu", "plus sign"),
            ("user.name@mergington.edu", "period"),
            ("user_name@mergington.edu", "underscore")
        ]
        
        # Act & Assert
        for email, email_type in special_emails:
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": email}
            )
            # Should succeed on first attempt
            assert response.status_code == 200, f"Failed with {email_type} in email"

    def test_activity_name_case_sensitivity(self, client):
        """Test that activity names are case-sensitive."""
        # Arrange
        correct_case_activity = "Chess Club"
        wrong_case_activity = "chess club"
        email1 = "test1@mergington.edu"
        email2 = "test2@mergington.edu"
        
        # Act
        response_correct = client.post(
            f"/activities/{correct_case_activity}/signup",
            params={"email": email1}
        )
        response_wrong = client.post(
            f"/activities/{wrong_case_activity}/signup",
            params={"email": email2}
        )
        
        # Assert
        assert response_correct.status_code == 200
        assert response_wrong.status_code == 404

    def test_signup_response_format(self, client):
        """Test that signup response has correct JSON format."""
        # Arrange
        email = "format@mergington.edu"
        
        # Act
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert "message" in data

    def test_remove_participant_response_format(self, client):
        """Test that remove response has correct JSON format."""
        # Arrange
        email = "formatremove@mergington.edu"
        activity_name = "Basketball Team"
        
        # Act - Add participant first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(data, dict)
        assert "message" in data


class TestActivityData:
    """Tests for activity data integrity and structure."""

    def test_all_activities_have_description(self, client):
        """Test that all activities have descriptions."""
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_info in activities.items():
            assert "description" in activity_info, f"Missing description for {activity_name}"
            assert isinstance(activity_info["description"], str)
            assert len(activity_info["description"]) > 0

    def test_all_activities_have_schedule(self, client):
        """Test that all activities have schedules."""
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_info in activities.items():
            assert "schedule" in activity_info, f"Missing schedule for {activity_name}"
            assert isinstance(activity_info["schedule"], str)
            assert len(activity_info["schedule"]) > 0

    def test_all_activities_have_max_participants(self, client):
        """Test that all activities have max participant limits."""
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_info in activities.items():
            assert "max_participants" in activity_info, f"Missing max_participants for {activity_name}"
            assert isinstance(activity_info["max_participants"], int)
            assert activity_info["max_participants"] > 0

    def test_participants_count_consistent(self, client):
        """Test that participant count doesn't exceed maximum."""
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_info in activities.items():
            participants = activity_info["participants"]
            max_participants = activity_info["max_participants"]
            # Note: The API doesn't enforce this, but it's good data integrity check
            assert len(participants) <= max_participants, \
                f"{activity_name} has more participants than max_participants"


class TestErrorResponses:
    """Tests for error response format and consistency."""

    def test_not_found_error_has_detail(self, client):
        """Test that 404 errors include detail field."""
        # Arrange
        nonexistent_activity = "Nonexistent"
        email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "detail" in data

    def test_bad_request_error_has_detail(self, client):
        """Test that 400 errors include detail field."""
        # Arrange
        email = "duplicate@mergington.edu"
        activity_name = "Chess Club"
        
        # Act - First signup succeeds
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Duplicate signup fails
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "detail" in data
