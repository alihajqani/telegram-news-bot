from telegram import Bot
from telegram.request import HTTPXRequest
import os

request = HTTPXRequest(
    connect_timeout=15.0,
    read_timeout=25.0,
    write_timeout=25.0,
    pool_timeout=5.0
)

bot = Bot(os.getenv("TELEGRAM_TOKEN"), request=request)