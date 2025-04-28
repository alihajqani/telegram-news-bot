from dotenv import load_dotenv; load_dotenv()
import logging
import time
from app.flows.newsflow import NewsFlow
from app.utils import storage_sqlite
from app.utils.schedule_jobs import init_scheduler

logger = logging.getLogger('telegram_news_bot.main')

if __name__ == "__main__":
    try:
        start_time = time.monotonic()
        logger.info("Starting Telegram News Bot")
        
        # Initialize database
        logger.info("Initializing database...")
        storage_sqlite.init_db()
        
        # Initialize and start scheduler
        logger.info("Initializing scheduler...")
        init_scheduler()
        
        end_time = time.monotonic()
        logger.info(f"Initialization completed in {end_time - start_time:.2f}s")
        
        # Keep main thread alive
        logger.info("Bot is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(3600)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal. Stopping bot...")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise
