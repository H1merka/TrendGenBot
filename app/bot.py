# bot.py
from vkbottle.bot import Message
from vkbottle import Keyboard, Text, KeyboardButtonColor
from vk_utils import get_group_posts, sorting_posts
from postanalyzer import PostAnalyzer
from bot_instance import bot
import asyncio
from datetime import datetime, timedelta


# Основное меню
def main_keyboard():
    return (
        Keyboard(inline=False)
        .add(Text("📊 Анализ сообщества", payload={"cmd": "analyze"}), color=KeyboardButtonColor.PRIMARY)
        .add_row()
        .add(Text("📅 За неделю", payload={"cmd": "analyze_week"}), color=KeyboardButtonColor.SECONDARY)
        .add(Text("🗓️ За месяц", payload={"cmd": "analyze_month"}), color=KeyboardButtonColor.SECONDARY)
        .add_row()
        .add(Text("ℹ️ Помощь", payload={"cmd": "help"}), color=KeyboardButtonColor.SECONDARY)
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
        "Нажмите '📊 Анализ сообщества' и введите короткое имя или ID сообщества.\n\n"
        "Пример: `vk`, `public123456`, `my_group_name`"
    )


@bot.on.message(payload={"cmd": "analyze"})
async def ask_for_group_id(message: Message):
    await message.answer("✍️ Введите ID или короткое имя вашего сообщества:")


@bot.on.message(payload={"cmd": "analyze_week"})
async def ask_for_group_week(message: Message):
    await message.answer("📅 Введите ID или короткое имя сообщества для анализа за *неделю*:")


@bot.on.message(payload={"cmd": "analyze_month"})
async def ask_for_group_month(message: Message):
    await message.answer("🗓️ Введите ID или короткое имя сообщества для анализа за *месяц*:")


# Обработка текстовых сообщений
@bot.on.message()
async def analyze_handler(message: Message):
    group_id = message.text.strip()
    if not group_id:
        return

    await message.answer(f"🔍 Получаю посты сообщества `{group_id}`...")

    posts = await get_group_posts(group_id)
    if not posts:
        await message.answer("❌ Не удалось получить посты. Проверьте правильность ID или доступ.")
        return

    # Определяем тип анализа на основе предыдущей команды пользователя (через last payload)
    last_payload = message.payload or {}
    date_from = None
    period = "всё время"

    if "analyze_week" in last_payload.values():
        date_from = datetime.now() - timedelta(days=7)
        period = "последнюю неделю"
    elif "analyze_month" in last_payload.values():
        date_from = datetime.now() - timedelta(days=30)
        period = "последний месяц"

    await message.answer(f"✅ Получено {len(posts)} постов. Анализирую за {period}...")

    top_posts = await sorting_posts(posts, date_from=date_from)
    analyzer = PostAnalyzer()
    recommendations = await asyncio.to_thread(analyzer.analyze_posts, top_posts)

    await message.answer("📊 Результаты анализа:\n\n" + recommendations, keyboard=main_keyboard())


bot.run_forever()
