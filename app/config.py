import os
from dotenv import load_dotenv


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

# Authentification URL for getting access to group
AUTH_URL: str = (
        "https://oauth.vk.com/authorize?"
        f"client_id={VK_CLIENT_ID}"
        "&display=page"
        "&redirect_uri=https://oauth.vk.com/blank.html"
        "&scope=groups,wall"
        "&response_type=token"
        "&v=5.131"
    )
