"""Background job scheduling for RSS fetching and article publishing."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
from app.agents.fetcher import FetcherAgent
from app.agents.publisher import PublisherAgent
from app.utils import storage_sqlite
from app.utils.scheduling import calculate_interval

scheduler = BackgroundScheduler()

def fetch_rss_job():
    """Fetch new articles from RSS feed and store them with pending status."""
    feed_url = "https://theartnewspaper.com/rss.xml"
    FetcherAgent().run(feed_url)

def check_and_publish_job():
    """
    Check if it's time to publish the next pending article based on dynamic interval.
    """
    # Count pending articles
    pending_count = storage_sqlite.count_pending_articles()
    if pending_count == 0:
        return

    # Calculate ideal interval
    interval = calculate_interval(pending_count)
    
    # Check if enough time has passed since last publish
    last_ts = storage_sqlite.load_last_publish_ts()
    now = time.monotonic()
    
    if now - last_ts >= interval:
        # Get and publish next article
        article = storage_sqlite.get_next_pending_article()
        if article:
            # PublisherAgent.run is async, so we need to handle it properly
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(PublisherAgent().run(article))
                storage_sqlite.mark_article_sent(article['id'])
                storage_sqlite.save_last_publish_ts(now)
            finally:
                loop.close()

def init_scheduler():
    """Initialize and start the job scheduler."""
    # Schedule RSS fetch every 3 minutes for testing
    scheduler.add_job(
        fetch_rss_job,
        'interval',
        minutes=3,
        id='rss_fetch',
        replace_existing=True
    )
    
    # Schedule publish check every 2 minutes for testing
    scheduler.add_job(
        check_and_publish_job,
        'interval',
        minutes=2,
        id='publish_check',
        replace_existing=True
    )
    
    # Start the scheduler if it's not already running
    if not scheduler.running:
        scheduler.start()