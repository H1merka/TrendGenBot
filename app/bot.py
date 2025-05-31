from vkbottle.bot import Message
from vk_utils import get_group_posts, sorting_posts
from postanalyzer import PostAnalyzer
import asyncio
from datetime import datetime, timedelta
from config import AUTH_URL, USER_STATES
from main_obj_init import bot, main_keyboard
import re
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


@bot.on.message(payload={"cmd": "auth"})
async def auth_handler(message: Message) -> None:
    await message.answer(
        "Для работы мне нужно получить доступ к вашему сообществу.\n\n"
        "Перейдите по ссылке, скопируйте URL из адресной строки и отправьте мне:\n\n"
        f"{AUTH_URL}"
    )


@bot.on.message(payload={"cmd": "analyze"})
async def ask_for_group_all(message: Message) -> None:
    user_id = message.from_id
    USER_STATES[user_id] = USER_STATES.get(user_id, {})
    USER_STATES[user_id]["period"] = "all"
    await message.answer("Введите ID или короткое имя вашего сообщества:")


@bot.on.message(payload={"cmd": "analyze_week"})
async def ask_for_group_week(message: Message) -> None:
    user_id = message.from_id
    USER_STATES[user_id] = USER_STATES.get(user_id, {})
    USER_STATES[user_id]["period"] = "week"
    await message.answer("Введите ID или короткое имя сообщества для анализа за неделю:")


@bot.on.message(payload={"cmd": "analyze_month"})
async def ask_for_group_month(message: Message) -> None:
    user_id = message.from_id
    USER_STATES[user_id] = USER_STATES.get(user_id, {})
    USER_STATES[user_id]["period"] = "month"
    await message.answer("Введите ID или короткое имя сообщества для анализа за месяц:")


@bot.on.message()
async def message_handler(message: Message) -> None:
    user_id = message.from_id
    text = message.text.strip()

    # Attempt to recognize access_token
    match = re.search(r'access_token=([\w\d\._\-]+)', text)
    token = match.group(1) if match else text

    # If user sent a token, save it.
    if (token.startswith("vk1.") or token.startswith("e") or token.startswith("2")) and len(token) > 50:
        USER_STATES[user_id] = USER_STATES.get(user_id, {})
        USER_STATES[user_id]["token"] = token
        await message.answer(
            "Токен сохранён! Теперь выберите 'Анализ сообщества' "
            "и введите ID или короткое имя сообщества.",
            keyboard=main_keyboard
        )
        return

    # If there is no token, ask for authorization
    state = USER_STATES.get(user_id)
    if not state or "token" not in state:
        await message.answer(
            "Сначала авторизуйтесь, отправив access_token.", 
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

# Launching bot
if __name__ == "__main__":
    bot.run_forever()
