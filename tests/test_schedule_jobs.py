import pytest
from unittest.mock import patch, Mock
import time
from app.utils import schedule_jobs, storage_sqlite

@pytest.fixture
def temp_db(tmp_path):
    original_path = storage_sqlite.DB_PATH
    storage_sqlite.DB_PATH = tmp_path / "test.db"
    storage_sqlite.init_db()
    yield storage_sqlite.DB_PATH
    storage_sqlite.DB_PATH = original_path

@patch('app.agents.fetcher.FetcherAgent')
def test_fetch_rss_job(mock_fetcher):
    # Set up mock
    mock_instance = Mock()
    mock_fetcher.return_value = mock_instance
    
    # Run the job
    schedule_jobs.fetch_rss_job()
    
    # Verify FetcherAgent was called correctly
    mock_instance.run.assert_called_once_with("https://theartnewspaper.com/rss.xml")

@patch('app.agents.publisher.PublisherAgent')
def test_check_and_publish_job(mock_publisher, temp_db):
    # Add a test article
    storage_sqlite.add_article(
        url="https://example.com/test",
        title="Test Article",
        summary="Test summary",
        published="2025-04-28T10:00:00",
        tags=["test"]
    )
    
    # Mock publisher agent
    mock_instance = Mock()
    mock_publisher.return_value = mock_instance
    
    # Run job first time - should publish
    schedule_jobs.check_and_publish_job()
    
    # Should have called publish
    assert mock_instance.run.call_count == 1
    
    # Run job immediately again - should not publish due to interval
    schedule_jobs.check_and_publish_job()
    
    # Should not have published again
    assert mock_instance.run.call_count == 1
    
    # Fast forward time
    storage_sqlite.save_last_publish_ts(0.0)  # Reset last publish time
    
    # Run job again - should publish
    schedule_jobs.check_and_publish_job()
    
    # Should have published again
    assert mock_instance.run.call_count == 2