from telegram import Bot
from telegram.request import HTTPXRequest
import os

request = HTTPXRequest(
    connect_timeout=30.0,  # Increased from 15.0
    read_timeout=30.0,     # Increased from 25.0
    write_timeout=30.0,    # Increased from 25.0
    pool_timeout=10.0,     # Increased from 5.0
    connection_pool_size=10  # Added explicit pool size
)

bot = Bot(os.getenv("TELEGRAM_TOKEN"), request=request)