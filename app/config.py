import os
from dotenv import load_dotenv
from typing import Dict
from vkbottle.bot import Bot
from vkbottle import Keyboard, Text, KeyboardButtonColor, OpenLink
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
import threading


load_dotenv()

# ImageNet Normalization
IMAGENET_MEAN: tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: tuple[float, float, float] = (0.229, 0.224, 0.225)

# AI-agent
MODEL_NAME: str = "OpenGVLab/InternVL2_5-4B"

# Client ID of app, neccessary for authorization
VK_CLIENT_ID: str | None = os.getenv("CLIENT_ID")

# Bot token for working in bot group
TOKEN: str | None = os.getenv("BOT_TOKEN")

# OAuth2 redirect URI
REDIRECT_URI: str = "https://6a21-169-150-209-163.ngrok-free.app/callback"

# VK application secret key
SECRET: str | None = os.getenv("CLIENT_SECRET")

# Authentification URL for getting access to group
AUTH_URL: str = (
        "https://oauth.vk.com/authorize?"
        f"client_id={VK_CLIENT_ID}"
        "&display=page"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=groups,wall"
        "&response_type=code"
        "&v=5.131"
    )

# Blocking shared data for multithreading
lock = threading.Lock()

# user_id: { "token": str, "period": str }
USER_STATES: Dict[int, Dict[str, str]] = {}

# Initializing bot to split the app structure
bot = Bot(token=TOKEN, loop_wrapper=None)

# Keyboard for chat
main_keyboard = (
        Keyboard(inline=False)
        .add(OpenLink(label="Авторизация", link=AUTH_URL), color=KeyboardButtonColor.POSITIVE)
        .row()
        .add(Text("Анализ всех постов", payload={"cmd": "analyze"}), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("Анализ постов за неделю", payload={"cmd": "analyze_week"}), color=KeyboardButtonColor.PRIMARY)
        .add(Text("Анализ постов за месяц", payload={"cmd": "analyze_month"}), color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("Помощь", payload={"cmd": "help"}), color=KeyboardButtonColor.SECONDARY)
    )

# Initializing FastAPI backend server
app = FastAPI()

# Setting up Jinja2 templating for HTML rendering
templates = Jinja2Templates(directory="templates")
