from crewai import Agent
from app.utils.rss import fetch_feed
from app.utils.storage import load_seen, add_seen

class FetcherAgent(Agent):
    def __init__(self):
        super().__init__(
            role="خبرخوان",
            goal="یافتن مقالات جدید در فید RSS و تحویل به سایر ایجنت‌ها",
            backstory="یک دستیار سخت‌کوش که همواره فیدها را زیر نظر دارد."
        )

    def run(self, feed_url: str):
        unseen = []
        for entry in fetch_feed(feed_url):
            entry_id = getattr(entry, "id", entry.link)
            if entry.id not in load_seen():
                unseen.append({"id": entry.id,
                               "title": entry.title,
                               "link": entry.link,
                               "content": (entry.get("summary") or "")})
                add_seen(entry.id)
        print(f"[Fetcher] fetched={len(unseen)} unseen")
        return unseen
