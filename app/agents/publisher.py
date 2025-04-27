from crewai import Agent
from typing import ClassVar
import asyncio, os, telegram
from app.telegram_client import bot as _bot

MAX_TRIES = 3
BACKOFF = 4

class PublisherAgent(Agent):
    role: ClassVar[str] = "ناشر تلگرام"
    goal: ClassVar[str] = "ارسال خلاصهٔ خبر به کانال"
    backstory: ClassVar[str] = "رباتی که خبرها را منتشر می‌کند."
    bot: ClassVar[telegram.Bot] = _bot

    async def _safe_send(self, **kwargs):
        for attempt in range(1, MAX_TRIES + 1):
            try:
                return await self.__class__.bot.send_message(**kwargs)
            except telegram.error.TimedOut:
                if attempt == MAX_TRIES:
                    raise
                await asyncio.sleep(BACKOFF * attempt)  # 4s, 8s …

    async def run(self, article: dict):
        msg = (
            f"*{article['title']}*\n\n"
            f"{article['summary']}\n\n"
            f"🏷️ {' • '.join(article['tags'])}\n"
            f"[مطالعهٔ کامل]({article['link']})"
        )
        await self._safe_send(
            chat_id=os.getenv("CHANNEL_ID"),
            text=msg,
            parse_mode="Markdown",
            disable_web_page_preview=False,
        )
        return {"status": "sent"}
