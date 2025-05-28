from PIL import Image
import aiohttp
from io import BytesIO
from bot_instance import bot
from datetime import datetime


async def get_group_posts(group_id: str, count: int = 30):
    try:
        # owner_id для групп должен быть отрицательным числом
        response = await bot.api.wall.get(owner_id=-int(group_id), count=count)
        return response.items
    except Exception as e:
        print("Ошибка VK API:", e)
        return []


async def sorting_posts(posts, date_from=None):
    """
    Сортирует посты по количеству лайков и возвращает top_n с изображениями и текстом.
    
    :param posts: список постов (dict)
    :param date_from: минимальная дата публикации (если None — берутся все посты)
    :param top_n: сколько постов вернуть
    :return: список (image, text)
    """
    candidates = []

    for post in posts:
        # Фильтрация по дате, если указана
        post_date = datetime.fromtimestamp(post.get("date", 0))
        if date_from and post_date < date_from:
            continue

        text = post.get("text", "")
        attachments = post.get("attachments", [])
        like_count = post.get("likes", {}).get("count", 0)

        # Ищем первую фотографию
        image_url = None
        for att in attachments:
            if att.get("type") == "photo":
                sizes = att["photo"].get("sizes", [])
                if sizes:
                    largest = max(sizes, key=lambda s: s["width"] * s["height"])
                    image_url = largest["url"]
                    break

        if image_url:
            candidates.append((like_count, text, image_url))

    # Сортировка по убыванию лайков
    candidates.sort(reverse=True, key=lambda x: x[0])
    top_candidates = candidates[:3]

    result = []
    async with aiohttp.ClientSession() as session:
        for _, text, url in top_candidates:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        img_bytes = await response.read()
                        img = Image.open(BytesIO(img_bytes))
                        result.append((img, text))
                    else:
                        print(f"⚠️ Не удалось загрузить изображение: {url}")
            except Exception as e:
                print(f"❌ Ошибка при загрузке изображения: {e}")

    return result
