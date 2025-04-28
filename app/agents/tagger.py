from crewai import Agent
import yake

_kw = yake.KeywordExtractor(lan="En", n=1, top=5)

class TaggerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="Tagger",
            goal="Extracting keywords from the news summary",
            backstory="A precise linguist who immediately identifies keywords."
        )
        
    def run(self, article: dict):
        tags = [kw for kw, _ in _kw.extract_keywords(article['summary'])]
        article["tags"] = tags
        return article
