import threading
import handlers
from config import bot
from utils import run_api


if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_api, daemon=True)
    bot_thread.start()

    bot.run_forever()
