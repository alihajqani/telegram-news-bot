import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging
logger = logging.getLogger('telegram_news_bot')
logger.setLevel(logging.INFO)

# File handler with rotation every 5MB
file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(logs_dir, f'bot_{datetime.now().strftime("%Y%m%d")}.log'),
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5
)

# Console handler
console_handler = logging.StreamHandler()

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)