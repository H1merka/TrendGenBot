import os
from dotenv import load_dotenv


load_dotenv()

# ImageNet Normalization
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# AI-agent
MODEL_NAME = "OpenGVLab/InternVL2_5-4B"

VK_CLIENT_ID = os.getenv("CLIENT_ID")

TOKEN = os.getenv("BOT_TOKEN")
