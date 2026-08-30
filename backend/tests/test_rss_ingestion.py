import pytest
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import SessionLocal, init_db
from backend.services.feed_parser_service import (
    FeedParserService,
    validate_feed_url,
    parse_duration_seconds,
    parse_publication_date,
    is_private_or_loopback_ip,
)
from backend.services.podcast_ingestion_service import PodcastIngestionService
from backend.core.exceptions import ValidationException
from backend.repositories.podcast_repo import PodcastRepository
from backend.repositories.episode_repo import EpisodeRepository

client = TestClient(app)

SAMPLE_ITUNES_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>The Architecture &amp; Scale Show</title>
    <link>https://architecturescale.example.com</link>
    <description>Deep dive into distributed systems engineering.</description>
    <language>en-us</language>
    <itunes:author>Jane Doe &amp; Alex Chen</itunes:author>
    <itunes:image href="https://architecturescale.example.com/cover.jpg"/>
    
    <item>
      <title>Episode 101: Distributed Consensus &amp; Raft</title>
      <description>Understanding Leader Election, Log Replication, and Safety in Raft.</description>
      <pubDate>Mon, 15 Jan 2024 14:30:00 GMT</pubDate>
      <itunes:duration>01:14:22</itunes:duration>
      <itunes:episode>101</itunes:episode>
      <itunes:season>2</itunes:season>
      <guid isPermaLink="false">arch-scale-guid-101</guid>
      <enclosure url="https://cdn.example.com/audio/ep101.mp3" length="71434920" type="audio/mpeg"/>
    </item>

    <item>
      <title>Episode 102: Eventual Consistency and Conflict Resolution</title>
      <description>CRDTs, vector clocks, and multi-region database replication.</description>
      <pubDate>Mon, 22 Jan 2024 14:30:00 GMT</pubDate>
      <itunes:duration>45:10</itunes:duration>
      <itunes:episode>102</itunes:episode>
      <itunes:season>2</itunes:season>
      <guid isPermaLink="false">arch-scale-guid-102</guid>
      <enclosure url="https://cdn.example.com/audio/ep102.mp3" length="43419000" type="audio/mpeg"/>
    </item>
  </channel>
</rss>
"""

SAMPLE_MINIMAL_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Minimalist Podcast</title>
    <item>
      <title>Minimal Episode 1</title>
      <enclosure url="https://minimal.example.com/1.mp3"/>
    </item>
  </channel>
</rss>
"""

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_duration_parsing():
    assert parse_duration_seconds("01:14:22") == 4462.0
    assert parse_duration_seconds("45:10") == 2710.0
    assert parse_duration_seconds("3600") == 3600.0
    assert parse_duration_seconds(1820.5) == 1820.5
    assert parse_duration_seconds(None) is None
    assert parse_duration_seconds("invalid") is None

def test_ssrf_protection_rules():
    # Private / loopback IPs must be blocked
    assert is_private_or_loopback_ip("127.0.0.1") is True
    assert is_private_or_loopback_ip("10.0.0.1") is True
    assert is_private_or_loopback_ip("192.168.1.1") is True
    assert is_private_or_loopback_ip("172.16.0.1") is True
    assert is_private_or_loopback_ip("169.254.169.254") is True
    assert is_private_or_loopback_ip("8.8.8.8") is False

    # Blocked schemes
    with pytest.raises(ValidationException, match="Unsupported URL scheme"):
        validate_feed_url("ftp://example.com/feed.xml")

    with pytest.raises(ValidationException, match="Unsupported URL scheme"):
        validate_feed_url("file:///etc/passwd")

    # Blocked hostnames
    with pytest.raises(ValidationException, match="forbidden"):
        validate_feed_url("http://localhost:8000/feed.xml")

    with pytest.raises(ValidationException, match="forbidden"):
        validate_feed_url("http://127.0.0.1:8000/feed.xml")

    with pytest.raises(ValidationException, match="forbidden"):
        validate_feed_url("http://169.254.169.254/latest/meta-data")

def test_feed_parser_service_xml():
    parser = FeedParserService()
    parsed = parser.parse_feed_content(SAMPLE_ITUNES_RSS, source_url="https://architecturescale.example.com/feed.xml")

    podcast = parsed["podcast"]
    assert podcast["title"] == "The Architecture & Scale Show"
    assert podcast["author"] == "Jane Doe & Alex Chen"
    assert podcast["artwork_url"] == "https://architecturescale.example.com/cover.jpg"

    episodes = parsed["episodes"]
    assert len(episodes) == 2

    ep1 = episodes[0]
    assert ep1["title"] == "Episode 101: Distributed Consensus & Raft"
    assert ep1["duration"] == 4462.0
    assert ep1["guid"] == "arch-scale-guid-101"
    assert ep1["episode_number"] == 101
    assert ep1["season_number"] == 2
    assert ep1["audio_url"] == "https://cdn.example.com/audio/ep101.mp3"
    assert ep1["file_size"] == 71434920

def test_minimal_and_missing_metadata_parsing():
    parser = FeedParserService()
    parsed = parser.parse_feed_content(SAMPLE_MINIMAL_RSS)

    assert parsed["podcast"]["title"] == "Minimalist Podcast"
    assert parsed["podcast"]["author"] is None
    assert len(parsed["episodes"]) == 1
    assert parsed["episodes"][0]["title"] == "Minimal Episode 1"
    assert parsed["episodes"][0]["audio_url"] == "https://minimal.example.com/1.mp3"

def test_malformed_feed_handling():
    parser = FeedParserService()
    with pytest.raises(ValidationException, match="empty"):
        parser.parse_feed_content("")

    with pytest.raises(ValidationException, match="empty"):
        parser.parse_feed_content("   ")

def test_podcast_ingestion_and_deduplication(db_session):
    parser = FeedParserService()
    feed_data = parser.parse_feed_content(SAMPLE_ITUNES_RSS, source_url="https://unique-feed.example.com/rss.xml")

    service = PodcastIngestionService(parser_service=parser)

    # 1. First Ingestion
    res1 = service.ingest_parsed_data(db_session, feed_data, feed_url="https://unique-feed.example.com/rss.xml")
    podcast = res1["podcast"]
    assert res1["total_episodes_in_feed"] == 2
    assert res1["new_episodes_imported"] == 2
    assert res1["updated_episodes"] == 0

    try:
        # 2. Second Ingestion (Idempotent - Deduplication test)
        res2 = service.ingest_parsed_data(db_session, feed_data, feed_url="https://unique-feed.example.com/rss.xml")
        assert res2["podcast"].id == podcast.id
        assert res2["total_episodes_in_feed"] == 2
        assert res2["new_episodes_imported"] == 0
        assert res2["updated_episodes"] == 0

        # Verify no audio files were auto-downloaded (status remains 'uploaded')
        ep_repo = EpisodeRepository(db_session)
        eps = ep_repo.get_episodes(podcast_id=podcast.id)
        assert len(eps) == 2
        for ep in eps:
            assert ep.status == "uploaded"
            assert ep.guid in ("arch-scale-guid-101", "arch-scale-guid-102")
    finally:
        # Cleanup
        pod_repo = PodcastRepository(db_session)
        pod_repo.delete(podcast.id)

def test_api_import_endpoint():
    with patch("backend.services.feed_parser_service.FeedParserService.fetch_feed_xml", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = SAMPLE_ITUNES_RSS

        resp = client.post("/api/podcasts/import", json={
            "feed_url": "https://valid-podcast.example.com/rss"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["podcast"]["title"] == "The Architecture & Scale Show"
        assert data["total_episodes_in_feed"] == 2
        assert data["new_episodes_imported"] == 2

        # Cleanup
        pod_id = data["podcast"]["id"]
        client.delete(f"/api/podcasts/{pod_id}")
