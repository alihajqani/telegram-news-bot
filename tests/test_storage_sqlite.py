import pytest
import pathlib
import time
from app.utils import storage_sqlite

@pytest.fixture
def temp_db(tmp_path):
    # Temporarily override the DB_PATH for testing
    original_path = storage_sqlite.DB_PATH
    storage_sqlite.DB_PATH = tmp_path / "test.db"
    yield storage_sqlite.DB_PATH
    storage_sqlite.DB_PATH = original_path

def test_init_db(temp_db):
    storage_sqlite.init_db()
    assert temp_db.exists()

def test_article_operations(temp_db):
    storage_sqlite.init_db()
    test_url = "https://example.com/test"
    test_title = "Test Article"
    
    # Test has_article returns False for non-existent article
    assert not storage_sqlite.has_article(test_url)
    
    # Test adding an article
    storage_sqlite.add_article(
        url=test_url,
        title=test_title,
        summary="Test summary",
        published="2025-04-28",
        tags=["test", "example"]
    )
    
    # Test has_article returns True after insertion
    assert storage_sqlite.has_article(test_url)
    
    # Test list_processed_urls includes the added URL
    urls = storage_sqlite.list_processed_urls()
    assert test_url in urls
    
def test_duplicate_article(temp_db):
    storage_sqlite.init_db()
    test_url = "https://example.com/test"
    
    # Add same article twice
    storage_sqlite.add_article(
        url=test_url,
        title="First",
        summary="Test",
        published="2025-04-28",
        tags=["test"]
    )
    storage_sqlite.add_article(
        url=test_url,
        title="Second",
        summary="Test",
        published="2025-04-28",
        tags=["test"]
    )
    
    # Should only be one instance of the URL
    urls = storage_sqlite.list_processed_urls()
    assert urls.count(test_url) == 1

def test_count_pending_articles(temp_db):
    storage_sqlite.init_db()
    
    # Add articles with different statuses
    storage_sqlite.add_article(
        url="https://example.com/1",
        title="Pending 1",
        summary="Test",
        published="2025-04-28T10:00:00",
        tags=["test"]
    )
    storage_sqlite.add_article(
        url="https://example.com/2",
        title="Pending 2",
        summary="Test",
        published="2025-04-28T11:00:00",
        tags=["test"]
    )
    
    # Initially both should be pending
    assert storage_sqlite.count_pending_articles() == 2
    
    # Mark one as sent
    article = storage_sqlite.get_next_pending_article()
    storage_sqlite.mark_article_sent(article['id'])
    
    # Should now have one pending
    assert storage_sqlite.count_pending_articles() == 1

def test_get_next_pending_article(temp_db):
    storage_sqlite.init_db()
    
    # Add two articles with different timestamps
    storage_sqlite.add_article(
        url="https://example.com/newer",
        title="Newer Article",
        summary="Test",
        published="2025-04-28T12:00:00",
        tags=["test"]
    )
    storage_sqlite.add_article(
        url="https://example.com/older",
        title="Older Article",
        summary="Test",
        published="2025-04-28T10:00:00",
        tags=["test"]
    )
    
    # Should get the older article first
    article = storage_sqlite.get_next_pending_article()
    assert article['title'] == "Older Article"
    
    # Mark it as sent
    storage_sqlite.mark_article_sent(article['id'])
    
    # Should get the newer article next
    article = storage_sqlite.get_next_pending_article()
    assert article['title'] == "Newer Article"

def test_metadata_timestamp(temp_db):
    storage_sqlite.init_db()
    
    # Should return 0.0 when no timestamp exists
    assert storage_sqlite.load_last_publish_ts() == 0.0
    
    # Save and load a timestamp
    now = time.time()
    storage_sqlite.save_last_publish_ts(now)
    loaded = storage_sqlite.load_last_publish_ts()
    assert loaded == now