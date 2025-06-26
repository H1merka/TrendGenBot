import threading
import api_server  # Ensure FastAPI routes are registered
import handlers    # Register VK bot message handlers
from config import bot
from utils import run_api


def main() -> None:
    # Start FastAPI in background
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    # Start VK bot loop
    bot.run_forever()


if __name__ == "__main__":
    main()