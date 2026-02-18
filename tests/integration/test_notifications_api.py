"""Integration tests for notifications API endpoints."""
import pytest
from fastapi import status


@pytest.mark.integration
class TestNotificationsSubscribeEndpoint:
    """Tests for POST /notifications/subscribe endpoint."""

    def test_subscribe_success(self, client):
        """Test successful subscription with valid email."""
        response = client.post(
            "/notifications/subscribe",
            json={
                "email": "test-integration@example.com",
                "diseases": ["DENGUE"],
                "min_risk_level": "HIGH",
                "frequency": "immediate",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "test-integration@example.com"
        assert "subscriber_id" in data
        assert "message" in data

    def test_subscribe_update_existing(self, client):
        """Test that subscribing again with the same email updates preferences."""
        # Subscribe first time
        client.post(
            "/notifications/subscribe",
            json={"email": "update-test@example.com", "min_risk_level": "HIGH"},
        )
        # Subscribe again — should update
        response = client.post(
            "/notifications/subscribe",
            json={
                "email": "update-test@example.com",
                "min_risk_level": "CRITICAL",
                "diseases": ["COVID"],
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "updated" in response.json()["message"].lower() or "success" in response.json()["message"].lower()

    def test_subscribe_invalid_email(self, client):
        """Test that invalid email returns 422."""
        response = client.post(
            "/notifications/subscribe",
            json={"email": "not-an-email"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestNotificationsPreferencesEndpoint:
    """Tests for GET /notifications/preferences endpoint."""

    def test_get_preferences_success(self, client):
        """Test getting preferences after subscribing."""
        # Subscribe first
        client.post(
            "/notifications/subscribe",
            json={"email": "pref-test@example.com", "min_risk_level": "MEDIUM"},
        )
        # Get preferences
        response = client.get(
            "/notifications/preferences?email=pref-test@example.com"
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "pref-test@example.com"
        assert data["min_risk_level"] == "MEDIUM"
        assert data["active"] is True

    def test_get_preferences_not_found(self, client):
        """Test that unknown email returns 404."""
        response = client.get(
            "/notifications/preferences?email=unknown@nowhere.com"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestNotificationsUnsubscribeEndpoint:
    """Tests for DELETE /notifications/unsubscribe endpoint."""

    def test_unsubscribe_invalid_token(self, client):
        """Test that invalid unsubscribe token returns 404."""
        response = client.delete(
            "/notifications/unsubscribe?token=fake-token-12345"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
