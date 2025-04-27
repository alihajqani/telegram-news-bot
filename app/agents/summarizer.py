from crewai import Agent
from pydantic import PrivateAttr
from openai import OpenAI
import os
from typing import ClassVar

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class SummarizerAgent(Agent):
    role: ClassVar[str] = "خلاصه‌کننده"
    goal: ClassVar[str] = "تلخیص خبرها به زبانی روان و جذاب"
    backstory: ClassVar[str] = "یک نویسنده خلاق که عاشق خلاصه‌نویسی است."
    _tone: str = PrivateAttr(default="صمیمی و هیجان‌انگیز")

    def __init__(self, tone: str = "صمیمی و هیجان‌انگیز"):
        super().__init__()
        self._tone = tone

    def run(self, article: dict):
        prompt = (f"با لحن {self._tone} این متن خبری را خلاصه کن (۵۰–۷۰ کلمه):\n"
                 f"{article['content'] or article['title']}")
        
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
        )
        article["summary"] = resp.choices[0].message.content.strip()
        return article
