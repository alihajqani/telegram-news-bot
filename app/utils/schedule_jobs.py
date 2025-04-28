"""Background job scheduling for RSS fetching and article publishing."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time
import logging
import asyncio
from app.agents.fetcher import FetcherAgent
from app.agents.publisher import PublisherAgent
from app.utils import storage_sqlite
from app.utils.scheduling import calculate_interval

logger = logging.getLogger('telegram_news_bot.scheduler')
scheduler = BackgroundScheduler()

def fetch_rss_job():
    """Fetch new articles from RSS feed and store them with pending status."""
    start_time = time.monotonic()
    logger.info("Starting RSS fetch job")
    
    try:
        feed_url = "https://theartnewspaper.com/rss.xml"
        FetcherAgent().run(feed_url)
        
        end_time = time.monotonic()
        logger.info(f"RSS fetch job completed in {end_time - start_time:.2f}s")
    except Exception as e:
        logger.error(f"Error in fetch_rss_job: {str(e)}", exc_info=True)
        raise

async def publish_article(article):
    """Async helper function to publish an article"""
    return await PublisherAgent().run(article)

def check_and_publish_job():
    """
    Check if it's time to publish the next pending article based on dynamic interval.
    """
    start_time = time.monotonic()
    logger.info("Starting publish check job")
    
    try:
        # Count pending articles
        pending_count = storage_sqlite.count_pending_articles()
        if pending_count == 0:
            logger.info("No pending articles to publish")
            return

        # Calculate ideal interval
        interval = calculate_interval(pending_count)
        logger.info(f"Found {pending_count} pending articles, calculated interval: {interval:.2f}s")
        
        # Check if enough time has passed since last publish
        last_ts = storage_sqlite.load_last_publish_ts()
        now = time.monotonic()
        time_since_last = now - last_ts
        
        if time_since_last >= interval:
            logger.info(f"Time to publish (elapsed: {time_since_last:.2f}s >= interval: {interval:.2f}s)")
            
            # Get and publish next article
            article = storage_sqlite.get_next_pending_article()
            if article:
                logger.info(f"Publishing article: {article.get('title', 'Unknown Title')}")
                
                # Create new event loop for this job
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    loop.run_until_complete(publish_article(article))
                    storage_sqlite.mark_article_sent(article['id'])
                    storage_sqlite.save_last_publish_ts(now)
                    
                    end_time = time.monotonic()
                    logger.info(f"Article published successfully. Total job time: {end_time - start_time:.2f}s")
                finally:
                    loop.close()
        else:
            logger.info(f"Not time to publish yet. Time since last: {time_since_last:.2f}s < interval: {interval:.2f}s")
            
    except Exception as e:
        logger.error(f"Error in check_and_publish_job: {str(e)}", exc_info=True)
        raise

def init_scheduler():
    """Initialize and start the job scheduler."""
    logger.info("Initializing scheduler")
    
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
        logger.info("Starting scheduler")
        scheduler.start()
        logger.info("Scheduler started successfully")