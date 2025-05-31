# bot.py
from vkbottle.bot import Message, Bot
from vkbottle import Keyboard, Text, KeyboardButtonColor
from vk_utils import get_group_posts, sorting_posts, normalize_group_id
from postanalyzer import PostAnalyzer
import asyncio
from datetime import datetime, timedelta
from config import VK_CLIENT_ID, TOKEN
import re


bot = Bot(token=TOKEN)

# user_id: { "token": str, "period": str }
user_states = {}


# Основное меню
def main_keyboard():
    return (
        Keyboard(inline=False)
        .add(Text("Авторизация", payload={"cmd": "auth"}), color=KeyboardButtonColor.POSITIVE)
        .row()
        .add(Text("Анализ сообщества", payload={"cmd": "analyze"}), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("За неделю", payload={"cmd": "analyze_week"}), color=KeyboardButtonColor.PRIMARY)
        .add(Text("За месяц", payload={"cmd": "analyze_month"}), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("Помощь", payload={"cmd": "help"}), color=KeyboardButtonColor.SECONDARY)
    )


@bot.on.message(text="/start")
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я ИИ-бот для анализа сообществ ВКонтакте. 📈\n\n"
        "Выберите действие:",
        keyboard=main_keyboard()
    )


@bot.on.message(payload={"cmd": "help"})
async def help_handler(message: Message):
    await message.answer(
        "💡 Я могу анализировать активность и контент вашего сообщества.\n"
        "Нажмите 'Авторизация' и перейдите по ссылке, чтобы получить access_token.\n"
        "Затем отправьте мне этот токен.\n\n"
        "После этого нажмите 'Анализ сообщества' и введите ID или короткое имя сообщества.\n\n"
        "Пример ID: `vk`, `public123456`, `my_group_name`"
    )


@bot.on.message(payload={"cmd": "auth"})
async def auth_handler(message: Message):
    auth_url = (
        f"https://oauth.vk.com/authorize?"
        f"client_id={VK_CLIENT_ID}"
        f"&display=page"
        f"&redirect_uri=https://oauth.vk.com/blank.html"
        f"&scope=groups,wall,offline"
        f"&response_type=token"
        f"&v=5.131"
    )

    await message.answer(
        "🔐 Для работы мне нужно получить доступ к вашему сообществу.\n\n"
        "Перейдите по ссылке, нажмите 'Разрешить', а затем отправьте мне `access_token` из адресной строки:\n\n"
        f"{auth_url}"
    )


@bot.on.message(payload={"cmd": "analyze"})
async def ask_for_group_all(message: Message):
    user_id = message.from_id
    user_states[user_id] = user_states.get(user_id, {})
    user_states[user_id]["period"] = "all"
    await message.answer("✍️ Введите ID или короткое имя вашего сообщества:")


@bot.on.message(payload={"cmd": "analyze_week"})
async def ask_for_group_week(message: Message):
    user_id = message.from_id
    user_states[user_id] = user_states.get(user_id, {})
    user_states[user_id]["period"] = "week"
    await message.answer("📅 Введите ID или короткое имя сообщества для анализа за *неделю*:")


@bot.on.message(payload={"cmd": "analyze_month"})
async def ask_for_group_month(message: Message):
    user_id = message.from_id
    user_states[user_id] = user_states.get(user_id, {})
    user_states[user_id]["period"] = "month"
    await message.answer("🗓️ Введите ID или короткое имя сообщества для анализа за *месяц*:")


@bot.on.message()
async def message_handler(message: Message):
    user_id = message.from_id
    text = message.text.strip()

    # Попытка распознать access_token
    match = re.search(r'access_token=([\w\d\._\-]+)', text)
    token = match.group(1) if match else text

    # Если пользователь прислал токен, сохраняем его
    if (token.startswith("vk1.") or token.startswith("e") or token.startswith("2")) and len(token) > 50:
        user_states[user_id] = user_states.get(user_id, {})
        user_states[user_id]["token"] = token
        await message.answer("✅ Токен сохранён! Теперь выберите 'Анализ сообщества' и введите ID или короткое имя сообщества.")
        return

    # Если токена нет — просим авторизацию
    state = user_states.get(user_id)
    if not state or "token" not in state:
        await message.answer("🔒 Сначала авторизуйтесь, отправив access_token.")
        return

    # Пытаемся получить посты по ID сообщества
    group_id = normalize_group_id(text)
    period = state.get("period", "all")

    await message.answer(f"🔍 Получаю посты сообщества `{group_id}`...")

    posts = await get_group_posts(group_id, access_token=state["token"])

    if isinstance(posts, dict) and "error" in posts:
        await message.answer(f"❌ VK API вернул ошибку: {posts['error']}")
        return
    if not posts:
        await message.answer("❌ Не удалось получить посты. Проверьте правильность ID или доступ.")
        return

    # Определяем дату фильтрации по периоду
    date_from = None
    if period == "week":
        date_from = datetime.now() - timedelta(days=7)
    elif period == "month":
        date_from = datetime.now() - timedelta(days=30)

    await message.answer(f"✅ Получено {len(posts)} постов. Анализирую за {'последнюю неделю' if period == 'week' else 'последний месяц' if period == 'month' else 'всё время'}...")

    top_posts = await sorting_posts(posts, date_from=date_from)
    analyzer = PostAnalyzer()
    recommendations = await asyncio.to_thread(analyzer.analyze_posts, top_posts)

    await message.answer("📊 Результаты анализа:\n\n" + recommendations, keyboard=main_keyboard())


# --- Запуск бота ---
if __name__ == "__main__":
    print('Бот запущен')
    bot.run_forever()
