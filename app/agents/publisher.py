from crewai import Agent
from typing import ClassVar
import asyncio, os, telegram, time, logging
from app.telegram_client import bot as _bot

logger = logging.getLogger('telegram_news_bot.publisher')
MAX_TRIES = 3
BACKOFF = 4

class PublisherAgent(Agent):
    role: ClassVar[str] = "Telegram Publisher"
    goal: ClassVar[str] = "Sending news summary to the channel"
    backstory: ClassVar[str] = "A bot that publishes news."
    bot: ClassVar[telegram.Bot] = _bot

    async def _safe_send(self, **kwargs):
        start_time = time.monotonic()
        for attempt in range(1, MAX_TRIES + 1):
            try:
                logger.info(f"Attempt {attempt} to send message")
                result = await self.__class__.bot.send_message(**kwargs)
                end_time = time.monotonic()
                logger.info(f"Message sent successfully in {end_time - start_time:.2f}s after {attempt} attempt(s)")
                return result
            except telegram.error.TimedOut:
                if attempt == MAX_TRIES:
                    logger.error("Max retries reached, giving up")
                    raise
                retry_delay = BACKOFF * attempt
                logger.warning(f"Attempt {attempt} timed out, retrying in {retry_delay}s")
                await asyncio.sleep(retry_delay)  # 4s, 8s …

    async def run(self, article: dict):
        start_time = time.monotonic()
        logger.info(f"Starting to publish article: {article.get('title', 'Unknown Title')}")
        
        try:
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
            
            end_time = time.monotonic()
            logger.info(f"Article published successfully. Total time: {end_time - start_time:.2f}s")
            return {"status": "sent"}
            
        except Exception as e:
            logger.error(f"Error publishing article: {str(e)}", exc_info=True)
            raise
