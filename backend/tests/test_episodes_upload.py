import io
import os
import pytest
from backend.models import Episode, ProcessingJob, Project, User

def test_upload_valid_audio_episode(client, db):
    # Prepare dummy audio bytes
    audio_content = b"ID3\x03\x00\x00\x00\x00\x00#TSSE\x00\x00\x00\x0f\x00\x00\x01Lavf58.29.100" + b"\x00" * 1024
    audio_file = io.BytesIO(audio_content)

    response = client.post(
        "/api/episodes",
        files={"file": ("test_episode.mp3", audio_file, "audio/mpeg")},
        data={"title": "Custom Test Episode", "description": "A test podcast upload."}
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "queued"
    assert data["title"] == "Custom Test Episode"
    
    # Verify in DB
    ep_id = data["id"]
    ep = db.query(Episode).filter(Episode.id == ep_id).first()
    assert ep is not None
    assert ep.title == "Custom Test Episode"
    assert ep.status == "queued"
    assert ep.file_size == len(audio_content)
    assert ep.original_filename == "test_episode.mp3"
    assert ep.audio_url.startswith("/storage/")

    # Verify ProcessingJob created
    job = db.query(ProcessingJob).filter(ProcessingJob.episode_id == ep_id).first()
    assert job is not None
    assert job.status == "queued"
    assert job.current_stage == "upload"

def test_upload_invalid_file_extension(client):
    invalid_file = io.BytesIO(b"malicious script content")
    response = client.post(
        "/api/episodes",
        files={"file": ("script.exe", invalid_file, "application/octet-stream")},
    )
    assert response.status_code == 400 or response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_upload_empty_file(client):
    empty_file = io.BytesIO(b"")
    response = client.post(
        "/api/episodes",
        files={"file": ("empty.mp3", empty_file, "audio/mpeg")},
    )
    assert response.status_code == 400 or response.status_code == 422
    data = response.json()
    assert "error" in data

def test_get_episodes_list_and_filters(client, db):
    user = User(id="u-filter", email="u-filter@example.com")
    p1 = Project(id="p-1", user_id=user.id, name="Project Alpha")
    p2 = Project(id="p-2", user_id=user.id, name="Project Beta")
    
    e1 = Episode(id="ep-f1", project_id=p1.id, title="Alpha Ep 1", duration=300.0, status="completed")
    e2 = Episode(id="ep-f2", project_id=p1.id, title="Alpha Ep 2", duration=600.0, status="processing")
    e3 = Episode(id="ep-f3", project_id=p2.id, title="Beta Ep 1", duration=900.0, status="completed")
    
    db.add_all([user, p1, p2, e1, e2, e3])
    db.commit()

    # 1. Get all
    res_all = client.get("/api/episodes")
    assert res_all.status_code == 200
    eps = res_all.json()
    assert len(eps) >= 3

    # 2. Filter by project
    res_p1 = client.get(f"/api/episodes?project_id={p1.id}")
    assert res_p1.status_code == 200
    p1_eps = res_p1.json()
    assert len(p1_eps) == 2
    assert all(ep["project_name"] == "Project Alpha" for ep in p1_eps)

    # 3. Filter by status
    res_proc = client.get("/api/episodes?status=processing")
    assert res_proc.status_code == 200
    proc_eps = res_proc.json()
    assert any(ep["id"] == "ep-f2" for ep in proc_eps)

    # 4. Search query
    res_search = client.get("/api/episodes?q=Beta")
    assert res_search.status_code == 200
    beta_eps = res_search.json()
    assert len(beta_eps) == 1
    assert beta_eps[0]["title"] == "Beta Ep 1"

def test_get_episode_detail_and_not_found(client, db):
    e = Episode(id="ep-detail-1", title="Detailed System Analysis", duration=2722.0, status="completed")
    db.add(e)
    db.commit()

    # Success case
    res = client.get("/api/episodes/ep-detail-1")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Detailed System Analysis"
    assert data["duration_formatted"] == "45:22"

    # Not found case
    res_404 = client.get("/api/episodes/nonexistent-id")
    assert res_404.status_code == 404
    err = res_404.json()
    assert err["error"]["code"] == "NOT_FOUND"

def test_delete_episode(client, db):
    audio_content = b"TESTAUDIOBYTES" * 100
    audio_file = io.BytesIO(audio_content)
    upload_res = client.post(
        "/api/episodes",
        files={"file": ("to_delete.mp3", audio_file, "audio/mpeg")},
        data={"title": "To Delete"}
    )
    assert upload_res.status_code == 200
    ep_id = upload_res.json()["id"]

    # Delete
    del_res = client.delete(f"/api/episodes/{ep_id}")
    assert del_res.status_code == 200

    # Verify not in DB
    assert db.query(Episode).filter(Episode.id == ep_id).first() is None
    # Verify 404 on subsequent get
    assert client.get(f"/api/episodes/{ep_id}").status_code == 404
