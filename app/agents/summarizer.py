from crewai import Agent
from pydantic import PrivateAttr
from openai import OpenAI
import os
from typing import ClassVar


client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url=os.getenv("XAI_API_BASE"))

class SummarizerAgent(Agent):
    role: ClassVar[str] = "Persian News Summarizer"
    goal: ClassVar[str] = (
        "Produce 50-70-word Persian summaries with a friendly, energetic tone, "
        "while deliberately varying wording and sentence structure to avoid repetition."
    )
    backstory: ClassVar[str] = (
        "A creative Persian writer obsessed with keeping summaries vivid and non-redundant. "
        "You dislike clichés, so you rephrase recurring ideas each time."
    )
    _tone: str = PrivateAttr(default="Friendly and exciting")

    def __init__(self, tone: str = "Friendly and exciting"):
        super().__init__()
        self._tone = tone

    def run(self, article: dict):
        prompt = (f"Summarize this news article in a {self._tone} tone (50-70 words) in Persian language:\n"
                f"{article['content'] or article['title']}")
        
        resp = client.chat.completions.create(
            model="grok-3-latest",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        print("***************")
        print(resp)
        print(type(resp))
        print("***************")

        article["summary"] = resp.choices[0].message.content.strip()
        return article