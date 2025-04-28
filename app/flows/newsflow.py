from crewai.flow.flow import Flow, start, listen   # Flow API :contentReference[oaicite:10]{index=10}
from app.agents.fetcher import FetcherAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.tagger import TaggerAgent
from app.agents.publisher import PublisherAgent
import asyncio

class NewsFlow(Flow):
    model = "grok-3-latest"
    max_posts = 2  # Add constant for max posts

    @start()
    def fetch(self):
        feed_url = "https://theartnewspaper.com/rss.xml"
        entries = FetcherAgent().run(feed_url)
        return entries[:self.max_posts]  # Limit initial fetch

    @listen(fetch)
    def summarize(self, entries):
        summarized = []
        for article in entries:
            summarized.append(SummarizerAgent().run(article))
        return summarized

    @listen(summarize)
    def tag(self, summarized):
        tagged = []
        for article in summarized:
            tagged.append(TaggerAgent().run(article))
        return tagged

    @listen(tag)
    async def publish(self, tagged):
        for i, article in enumerate(tagged[:self.max_posts]):  # Ensure max 3 posts
            await PublisherAgent().run(article)
            await asyncio.sleep(0.5)