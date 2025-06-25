from vkbottle.bot import Message
from utils import get_group_posts, sorting_posts
from postanalyzer import PostAnalyzer
import asyncio
from datetime import datetime, timedelta
from config import USER_STATES, bot, main_keyboard, lock
from typing import Any, Optional


@bot.on.message(text="/start", payload={"command": "start"})
async def start_handler(message: Message) -> None:
    """
    Handles the /start command from the user.
    Sends a welcome message and displays the main keyboard.
    """
    await message.answer(
        "Привет! Я чат-бот для составления рекомендаций по контент-плану сообществ\n\n"
        "Выберите действие:",
        keyboard=main_keyboard
    )


@bot.on.message(payload={"cmd": "help"})
async def help_handler(message: Message) -> None:
    """
    Provides usage instructions and help information to the user.
    """
    await message.answer(
        "Я могу анализировать активность и контент вашего сообщества, \n"
        "а также составлять рекомендации для контент плана сообщества."
        "Нажмите 'Авторизация' и авторизуйтесь.\n"
        "После этого нажмите 'Анализ сообщества' и введите ID или короткое имя сообщества.\n\n"
        "Пример ID: `vk`, `public123456`, `my_group_name`",
        keyboard=main_keyboard
    )


@bot.on.message(payload={"cmd": "analyze"})
async def ask_for_group_all(message: Message) -> None:
    """
    Requests community ID for full-period analysis.
    """
    user_id: int = message.from_id
    with lock:
        USER_STATES[user_id] = USER_STATES.get(user_id, {})
        USER_STATES[user_id]["period"] = "all"
    await message.answer("Введите ID или короткое имя вашего сообщества:")


@bot.on.message(payload={"cmd": "analyze_week"})
async def ask_for_group_week(message: Message) -> None:
    """
    Requests community ID for last week's posts analysis.
    """
    user_id: int = message.from_id
    with lock:
        USER_STATES[user_id] = USER_STATES.get(user_id, {})
        USER_STATES[user_id]["period"] = "week"
    await message.answer("Введите ID или короткое имя сообщества для анализа за неделю:")


@bot.on.message(payload={"cmd": "analyze_month"})
async def ask_for_group_month(message: Message) -> None:
    """
    Requests community ID for last month's posts analysis.
    """
    user_id: int = message.from_id
    with lock:
        USER_STATES[user_id] = USER_STATES.get(user_id, {})
        USER_STATES[user_id]["period"] = "month"
    await message.answer("Введите ID или короткое имя сообщества для анализа за месяц:")


@bot.on.message()
async def message_handler(message: Message) -> None:
    """
    Handles any text message. Assumes it's a community ID and initiates content analysis
    based on the previously selected period and stored access_token.
    """
    user_id: int = message.from_id
    text: str = message.text.strip()

    # Get user state and token from shared state
    with lock:
        state = USER_STATES.get(user_id, {})
        token = state.get("access_token")

    # If token is missing or invalid, prompt user to authenticate
    if not token or not (
        (token.startswith("vk1.") or token.startswith("e") or token.startswith("2")) and
        len(token) > 50
    ):
        await message.answer(
            "Токен отсутствует, авторизуйтесь.",
            keyboard=main_keyboard
        )
        return

    # Determine analysis period
    period: str = state.get("period", "all")

    await message.answer("Получаю посты сообщества...")

    # Fetch group posts using VK API
    posts: Any = await get_group_posts(text, access_token=state["access_token"])

    # Handle VK API errors
    if isinstance(posts, dict) and "error" in posts:
        await message.answer(f"VK API вернул ошибку: {posts['error']}", keyboard=main_keyboard)
        return

    # Handle empty result
    if not posts:
        await message.answer(
            "Не удалось получить посты. "
            "Проверьте правильность ID или доступ.",
            keyboard=main_keyboard
        )
        return

    # Define filtering start date based on selected period
    date_from: Optional[datetime] = None
    if period == "week":
        date_from = datetime.now() - timedelta(days=7)
        period_text = "последнюю неделю"
    elif period == "month":
        date_from = datetime.now() - timedelta(days=30)
        period_text = "последний месяц"
    else:
        period_text = "всё время"

    await message.answer(
        f"Получено {len(posts)} постов. Анализирую за {period_text}. "
        "Ваш запрос будет обработан в течение 5-10 минут, ожидайте."
    )

    # Sort and analyze posts
    top_posts: list = await sorting_posts(posts, date_from=date_from)
    analyzer = PostAnalyzer()
    recommendations: str = await asyncio.to_thread(analyzer.analyze_posts, top_posts)

    # Send recommendations
    result_text: str = (
        "В вашем контент-плане следует уделить больше внимания следующему:\n\n"
        + recommendations
    )

    await message.answer(
        result_text,
        keyboard=main_keyboard
    )
