from crewai.flow.flow import Flow, start, listen   # Flow API :contentReference[oaicite:10]{index=10}
from app.agents.fetcher import FetcherAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.tagger import TaggerAgent
from app.agents.publisher import PublisherAgent
import asyncio

class NewsFlow(Flow):
    model = "gpt-4o-mini"

    @start()
    def fetch(self):
        feed_url = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
        return FetcherAgent().run(feed_url)

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
        for i, article in enumerate(tagged):
            await PublisherAgent().run(article)
            await asyncio.sleep(0.5)