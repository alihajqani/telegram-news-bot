import feedparser

def fetch_feed(feed_url: str):
    feed = feedparser.parse(feed_url)
    if feed.bozo:
        raise ValueError(f"Error in feed: {feed.bozo_exception}")
    return feed.entries
