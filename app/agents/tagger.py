from crewai import Agent
import yake

_kw = yake.KeywordExtractor(lan="fa", n=1, top=5)

class TaggerAgent(Agent):
    def __init__(self):
        super().__init__(
            role="برچسب‌گذار",
            goal="استخراج کلمات کلیدی از خلاصهٔ خبر",
            backstory="یک زبان‌شناس دقیق که کلیدواژه‌ها را فوراً تشخیص می‌دهد."
        )
        
    def run(self, article: dict):
        tags = [kw for kw, _ in _kw.extract_keywords(article['summary'])]
        article["tags"] = tags
        return article
