from crewai import Agent
from app.utils.rss import fetch_feed
from app.utils.storage_sqlite import has_article, add_article
from datetime import datetime
import time
import logging

logger = logging.getLogger('telegram_news_bot.fetcher')

class FetcherAgent(Agent):
    def __init__(self):
        super().__init__(
            role="News Reader",
            goal="Finding new articles in the RSS feed and delivering them to other agents",
            backstory="A hard-working assistant who is always monitoring the feeds."
        )

    def run(self, feed_url: str):
        start_time = time.monotonic()
        logger.info(f"Starting RSS fetch from {feed_url}")
        
        try:
            entries = fetch_feed(feed_url)
            fetch_time = time.monotonic()
            logger.info(f"RSS fetch completed in {fetch_time - start_time:.2f}s, processing entries...")
            
            unseen = []
            for entry in entries:
                entry_id = getattr(entry, "id", entry.link)
                if not has_article(entry_id):
                    article = {
                        "id": entry_id,
                        "title": entry.title,
                        "link": entry.link,
                        "content": (entry.get("summary") or "")
                    }
                    unseen.append(article)
                    
                    # Store in SQLite with minimal info until processed by other agents
                    add_article(
                        url=entry_id,
                        title=entry.title,
                        summary=entry.get("summary", ""),
                        published=getattr(entry, "published", datetime.now().isoformat()),
                        tags=[]
                    )
            
            end_time = time.monotonic()
            total_time = end_time - start_time
            logger.info(f"Fetch completed. Total time: {total_time:.2f}s, Processing time: {end_time - fetch_time:.2f}s, Found {len(unseen)} new articles")
            
            return unseen
            
        except Exception as e:
            logger.error(f"Error in FetcherAgent: {str(e)}", exc_info=True)
            raise
