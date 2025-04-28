# app/utils/rss.py
import feedparser, logging, requests

log = logging.getLogger("rss")

def fetch_feed(feed_url: str):
    feed = feedparser.parse(feed_url)

    if feed.bozo and not feed.entries:
        raw = requests.get(feed_url, timeout=10).content
        feed = feedparser.parse(raw.decode("utf-8", "ignore"))

    if feed.bozo:
        log.warning("RSS warning %s", feed.bozo_exception)

    return feed.entries
