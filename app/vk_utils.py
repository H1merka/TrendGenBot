from PIL import Image
import aiohttp
from io import BytesIO
from datetime import datetime


def normalize_group_id(group_id: str) -> str:
    """
    Удаляет префиксы типа public, club и возвращает числовой ID без лишнего
    """
    if group_id.startswith("public"):
        return group_id.replace("public", "", 1)
    if group_id.startswith("club"):
        return group_id.replace("club", "", 1)
    return group_id


async def get_group_posts(group_id: str, access_token: str, count: int = 100):
    group_id = normalize_group_id(group_id)
    url = "https://api.vk.com/method/wall.get"
    params = {
        "owner_id": f"-{group_id}",
        "count": count,
        "access_token": access_token,
        "v": "5.131"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            if "error" in data:
                error_msg = data["error"].get("error_msg", "Неизвестная ошибка")
                return {"error": error_msg}
            return data.get("response", {}).get("items", [])


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
