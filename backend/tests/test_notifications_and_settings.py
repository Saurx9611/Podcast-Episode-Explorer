import pytest
from backend.models import User, Notification

@pytest.fixture
def user_with_notifications(db):
    user = User(
        id="user-notif-test",
        email="notif-test@example.com",
        name="Alex Engineer",
        role="Senior Developer",
        preferences={
            "general": {"workspace_name": "My Workspace"},
            "processing": {"transcription_model": "Whisper Large v3"},
            "search": {"min_similarity": "0.75"},
            "account": {"language": "English"},
        }
    )
    n1 = Notification(
        id="n-1",
        user_id=user.id,
        type="processing_complete",
        title="Processing complete",
        description="Episode ready",
        read=False,
    )
    n2 = Notification(
        id="n-2",
        user_id=user.id,
        type="saved_search_result",
        title="New saved search match",
        description="Found 3 results",
        read=False,
    )
    db.add_all([user, n1, n2])
    db.flush()
    return user

def test_notifications_lifecycle(client, user_with_notifications):
    headers = {"X-User-Id": "user-notif-test"}

    # 1. Get notifications
    res = client.get("/api/notifications", headers=headers)
    assert res.status_code == 200
    notifs = res.json()
    assert len(notifs) >= 2
    assert any(n["id"] == "n-1" and not n["read"] for n in notifs)

    # 2. Mark single notification as read
    res_read = client.patch("/api/notifications/n-1/read", headers=headers)
    assert res_read.status_code == 200
    assert res_read.json()["read"] is True

    # 3. Mark all as read
    res_read_all = client.post("/api/notifications/read-all", headers=headers)
    assert res_read_all.status_code == 200
    assert res_read_all.json()["count"] >= 1

    # Verify all unread queries return 0
    res_unread = client.get("/api/notifications?unread_only=true", headers=headers)
    assert res_unread.status_code == 200
    assert len(res_unread.json()) == 0

def test_settings_persistence(client, user_with_notifications):
    headers = {"X-User-Id": "user-notif-test"}

    # 1. Get settings
    res = client.get("/api/settings", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Alex Engineer"
    assert data["preferences"]["search"]["min_similarity"] == "0.75"

    # 2. Update settings
    update_payload = {
        "name": "Alex Morgan Senior",
        "role": "Lead Architect",
        "preferences": {
            "general": {"workspace_name": "Distributed Systems Pods", "default_playback_speed": "1.5x"},
            "processing": {"chunk_duration": "60", "overlap": "15"},
            "search": {"min_similarity": "0.85", "search_mode": "Hybrid"},
            "account": {"theme_mode": "Dark", "accent_color": "Emerald"},
        }
    }
    res_update = client.patch("/api/settings", json=update_payload, headers=headers)
    assert res_update.status_code == 200
    updated_data = res_update.json()
    assert updated_data["name"] == "Alex Morgan Senior"
    assert updated_data["role"] == "Lead Architect"
    assert updated_data["preferences"]["general"]["workspace_name"] == "Distributed Systems Pods"
    assert updated_data["preferences"]["search"]["min_similarity"] == "0.85"

    # Verify no sensitive server secrets / API keys are exposed
    assert "api_key" not in updated_data
    assert "password" not in updated_data
    assert "secret" not in updated_data
