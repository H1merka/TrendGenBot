import os
import threading
import secrets
import base64
import hashlib
from dotenv import load_dotenv
from typing import Dict, Tuple, Optional
from vkbottle.bot import Bot
from vkbottle import Keyboard, Text, KeyboardButtonColor, OpenLink
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

# Load environment variables from .env file
load_dotenv()

# ImageNet normalization constants for preprocessing image input
IMAGENET_MEAN: Tuple[float, float, float] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, float, float] = (0.229, 0.224, 0.225)

# Name of the AI model used for inference
MODEL_NAME: str = "OpenGVLab/InternVL2_5-4B"

# VK App client ID, used for OAuth2 authentication
VK_CLIENT_ID: Optional[str] = os.getenv("CLIENT_ID")

# VK group bot token for authenticating with VK API
TOKEN: Optional[str] = os.getenv("BOT_TOKEN")

# Redirect URI for OAuth2 flow (must match VK app settings)
REDIRECT_URI: str = "https://trendgenbot.ru/callback"


def generate_code_pair() -> Tuple[str, str]:
    """
    Generate a PKCE code verifier and its corresponding challenge
    according to the S256 transformation.

    Returns:
        tuple: A tuple containing (code_verifier, code_challenge)
    """
    verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8").rstrip("=")
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode("utf-8").rstrip("=")
    return verifier, challenge


# Generate PKCE code pair (used for secure OAuth2 authorization)
CODE_VERIFIER, CODE_CHALLENGE = generate_code_pair()

# Unique state string for CSRF protection in the auth flow
STATE: str = secrets.token_urlsafe(16)

# VK OAuth2 Authorization URL (VK ID PKCE Flow)
AUTH_URL: str = (
    f"https://id.vk.com/authorize?"
    f"client_id={VK_CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope=openid"
    f"&code_challenge={CODE_CHALLENGE}"
    f"&code_challenge_method=S256"
    f"&state={STATE}"
)

# Thread lock to ensure thread-safe access to shared data
lock = threading.Lock()

# Stores per-user session data, indexed by VK user_id (int)
# Example: { 123456: {"access_token": "...", "refresh_token": "..."} }
USER_STATES: Dict[int, Dict[str, str]] = {}

# Initialize VK bot without event loop wrapping (handled externally)
bot = Bot(token=TOKEN, loop_wrapper=None)

# Inline keyboard used in chat interactions
main_keyboard: Keyboard = (
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

# Initialize FastAPI app instance
app: FastAPI = FastAPI()

# Setup for rendering HTML templates with Jinja2
templates: Jinja2Templates = Jinja2Templates(directory="templates")
