import vk_api
from config import token
from PIL import Image
import requests
from io import BytesIO

def get_group_posts(group_id: str, count: int = 30):
    vk_session = vk_api.VkApi(token=token)
    api = vk_session.get_api()

    try:
        posts = api.wall.get(owner_id=-int(group_id), count=count)['items']
        return posts
    except Exception as e:
        print("Ошибка VK API:", e)
        return []


def sorting_posts(posts):
    candidates = []

    for post in posts:
        text = post.get("text", "")
        attachments = post.get("attachments", [])
        like_count = post.get("likes", {}).get("count", 0)

        # Ищем первую фотографию
        image_url = None
        for att in attachments:
            if att["type"] == "photo":
                sizes = att["photo"].get("sizes", [])
                if sizes:
                    # Берем самое крупное изображение
                    largest = max(sizes, key=lambda s: s["width"] * s["height"])
                    image_url = largest["url"]
                    break

        if image_url:
            candidates.append((like_count, text, image_url))

    # Сортировка по убыванию количества лайков
    candidates.sort(reverse=True, key=lambda x: x[0])

    # Оставляем только top_n постов
    top_candidates = candidates[:top_n]

    # Загружаем изображения и формируем список кортежей (Image, text)
    result = []
    for _, text, url in top_candidates:
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            result.append((img, text))
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {e}")

    return result