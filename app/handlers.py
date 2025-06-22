from vkbottle.bot import Message
from utils import get_group_posts, sorting_posts
from postanalyzer import PostAnalyzer
import asyncio
from datetime import datetime, timedelta
from config import USER_STATES
from config import bot, main_keyboard, lock
from typing import Any, Optional


@bot.on.message(text="/start", payload={"command": "start"})
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Я чат-бот для составления рекомендаций по контент-плану сообществ\n\n"
        "Выберите действие:",
        keyboard=main_keyboard
    )


@bot.on.message(payload={"cmd": "help"})
async def help_handler(message: Message) -> None:
    await message.answer(
        "Я могу анализировать активность и контент вашего сообщества, \n"
        "а также составлять рекомендации для контент плана сообщества."
        "Нажмите 'Авторизация' и перейдите по ссылке, чтобы получить access_token.\n"
        "После перехода по ссылке скопируйте URL из адресной строки и отправьте мне.\n\n"
        "После этого нажмите 'Анализ сообщества' и введите ID или короткое имя сообщества.\n\n"
        "Пример ID: `vk`, `public123456`, `my_group_name`",
        keyboard=main_keyboard
    )


@bot.on.message(payload={"cmd": "analyze"})
async def ask_for_group_all(message: Message) -> None:
    user_id = message.from_id
    with lock:
        USER_STATES[user_id] = USER_STATES.get(user_id, {})
        USER_STATES[user_id]["period"] = "all"
    await message.answer("Введите ID или короткое имя вашего сообщества:")


@bot.on.message(payload={"cmd": "analyze_week"})
async def ask_for_group_week(message: Message) -> None:
    user_id = message.from_id
    with lock:
        USER_STATES[user_id] = USER_STATES.get(user_id, {})
        USER_STATES[user_id]["period"] = "week"
    await message.answer("Введите ID или короткое имя сообщества для анализа за неделю:")


@bot.on.message(payload={"cmd": "analyze_month"})
async def ask_for_group_month(message: Message) -> None:
    user_id = message.from_id
    with lock:
        USER_STATES[user_id] = USER_STATES.get(user_id, {})
        USER_STATES[user_id]["period"] = "month"
    await message.answer("Введите ID или короткое имя сообщества для анализа за месяц:")


@bot.on.message()
async def message_handler(message: Message) -> None:
    user_id = message.from_id
    text = message.text.strip()

    with lock:
        state = USER_STATES.get(user_id, {})
        token = state.get("access_token")

    # If there is no token, ask for authorization
    if not token or not (
        (token.startswith("vk1.") or token.startswith("e") or token.startswith("2")) and
        len(token) > 50
    ):
        await message.answer(
            "Токен отсутствует, авторизуйтесь.",
            keyboard=main_keyboard
        )
        return

    period = state.get("period", "all")

    await message.answer("Получаю посты сообщества...")

    posts: Any = await get_group_posts(text, access_token=state["token"])

    if isinstance(posts, dict) and "error" in posts:
        await message.answer(f"VK API вернул ошибку: {posts['error']}", keyboard=main_keyboard)
        return
    if not posts:
        await message.answer(
            "Не удалось получить посты. "
            "Проверьте правильность ID или доступ.", 
            keyboard=main_keyboard
        )
        return

    # Setting the filtering date
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
        "Ваш запрос будет обработан в течение 5 минут, ожидайте."
    )
    top_posts = await sorting_posts(posts, date_from=date_from)
    analyzer = PostAnalyzer()
    recommendations: str = await asyncio.to_thread(analyzer.analyze_posts, top_posts)

    text = (
        "В вашем контент-плане следует уделить больше внимания следующему:\n\n"
        + recommendations
    )

    await message.answer(
        text,
        keyboard=main_keyboard
    )
