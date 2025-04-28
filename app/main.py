from dotenv import load_dotenv; load_dotenv()
from app.flows.newsflow import NewsFlow
from app.utils import storage_sqlite
from app.utils.schedule_jobs import init_scheduler
import time

if __name__ == "__main__":
    # Initialize database
    storage_sqlite.init_db()
    
    # Initialize and start scheduler
    init_scheduler()
    
    # Keep main thread alive
    while True:
        time.sleep(3600)
