import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert "Programming Class" in response.json()


def test_signup_for_activity_adds_student():
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_for_activity_rejects_duplicate_student():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_missing_activity_returns_404():
    response = client.post("/activities/Does Not Exist/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "student@mergington.edu"

    activities[activity_name]["participants"].append(email)

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_participant_missing_activity_returns_404():
    response = client.delete("/activities/Does Not Exist/participants/student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_missing_email_returns_404():
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
