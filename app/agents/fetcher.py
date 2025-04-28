from crewai import Agent
from app.utils.rss import fetch_feed
from app.utils.storage_sqlite import has_article, add_article
from datetime import datetime

class FetcherAgent(Agent):
    def __init__(self):
        super().__init__(
            role="News Reader",
            goal="Finding new articles in the RSS feed and delivering them to other agents",
            backstory="A hard-working assistant who is always monitoring the feeds."
        )

    def run(self, feed_url: str):
        unseen = []
        for entry in fetch_feed(feed_url):
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
        
        print(f"[Fetcher] fetched={len(unseen)} unseen")
        return unseen
