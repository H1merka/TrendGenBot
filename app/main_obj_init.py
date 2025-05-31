from vkbottle.bot import Bot
from vkbottle import Keyboard, Text, KeyboardButtonColor
from config import TOKEN


# Initializing bot to split the app structure
bot = Bot(token=TOKEN)

# Keyboard for chat
main_keyboard = (
        Keyboard(inline=False)
        .add(Text("Авторизация", payload={"cmd": "auth"}), color=KeyboardButtonColor.POSITIVE)
        .row()
        .add(Text("Анализ всех постов", payload={"cmd": "analyze"}), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("Анализ постов за неделю", payload={"cmd": "analyze_week"}), color=KeyboardButtonColor.PRIMARY)
        .add(Text("Анализ постов за месяц", payload={"cmd": "analyze_month"}), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("Помощь", payload={"cmd": "help"}), color=KeyboardButtonColor.SECONDARY)
    )
