import threading
import handlers  # Registers VK bot message handlers
from config import bot
from utils import run_api


def main() -> None:
    """
    Entry point of the application.

    Runs the FastAPI backend server in a separate thread and starts the VK bot's event loop.
    """
    # Start FastAPI app in a background thread (daemonized)
    bot_thread: threading.Thread = threading.Thread(target=run_api, daemon=True)
    bot_thread.start()

    # Start VK bot event loop (blocking call)
    bot.run_forever()


if __name__ == "__main__":
    main()
