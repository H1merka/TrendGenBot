import os
from dotenv import load_dotenv


load_dotenv()

# ImageNet Normalization
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# AI-agent
MODEL_NAME = "OpenGVLab/InternVL2_5-4B"

# Client ID of app, neccessary for authorization
VK_CLIENT_ID = os.getenv("CLIENT_ID")

# Bot token for working in bot group
TOKEN = os.getenv("BOT_TOKEN")

# Authentification URL for getting access to group
AUTH_URL = (
        "https://oauth.vk.com/authorize?"
        f"client_id={VK_CLIENT_ID}"
        "&display=page"
        "&redirect_uri=https://oauth.vk.com/blank.html"
        "&scope=groups,wall"
        "&response_type=token"
        "&v=5.131"
    )
