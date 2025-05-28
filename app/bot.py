# bot.py
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, Text, KeyboardButtonColor
from vk_utils import get_group_posts
from postanalyzer import PostAnalyzer
from config import token


bot = Bot(token=token)

# Основное меню
def main_keyboard():
    return (
        Keyboard(inline=False)
        .add(Text("📊 Анализ сообщества", payload={"cmd": "analyze"}), color=KeyboardButtonColor.PRIMARY)
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

# Обработка текста как group_id
@bot.on.message()
async def analyze_handler(message: Message):
    group_id = message.text.strip()
    if not group_id:
        return

    await message.answer(f"🔍 Получаю посты сообщества `{group_id}`...")

    posts = get_group_posts(group_id)
    if not posts:
        await message.answer("❌ Не удалось получить посты. Проверьте правильность ID или доступ.")
        return

    await message.answer(f"✅ Получено {len(posts)} постов. Анализирую...")
    analyzer = PostAnalyzer()
    recommendations = analyzer.analyze_posts(posts)
    await message.answer("📊 Результаты анализа:\n\n" + recommendations, keyboard=main_keyboard())

bot.run_forever()
