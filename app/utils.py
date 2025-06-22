from typing import List, Optional, Tuple, Union
from PIL import Image
import aiohttp
from io import BytesIO
import uvicorn
from datetime import datetime
from config import app


async def resolve_group_id(group_input: str, access_token: str) -> str:
    """Universal definition of numeric group_id"""
    if group_input.isdigit():
        return group_input

    # Deleting 'public' or 'club' prefixes
    if group_input.startswith("public") or group_input.startswith("club"):
        possible_id = group_input.lstrip("club").lstrip("public")
        if possible_id.isdigit():
            return possible_id

    # Using groups.getById to get numeric ID
    url = "https://api.vk.com/method/groups.getById"
    params = {
        "group_id": group_input,
        "access_token": access_token,
        "v": "5.131"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            data = await response.json()
            if "error" in data:
                raise ValueError(f"Ошибка VK API: {data['error'].get('error_msg', 'неизвестная ошибка')}")
            return str(data["response"][0]["id"])


async def get_group_posts(group_id: str, access_token: str, count: int = 100) -> Union[List[dict], dict]:
    """
    Fetches posts from a VK group wall.

    This function resolves various forms of VK group identifiers (numeric ID,
    short name, or prefixes like 'club'/'public') into a numeric group ID
    and retrieves the latest posts from the group's wall using the VK API.
    """
    try:
        group_id = await resolve_group_id(group_id, access_token)
    except ValueError as e:
        return {"error": str(e)}
    
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


async def sorting_posts(posts: List[dict], date_from: Optional[datetime] = None) -> List[Tuple[Optional[Image.Image], Optional[str]]]:
    """
    Sorting posts by the number of likes
    and returns top 3 with images and text.
    """
    candidates: List[Tuple[int, Optional[str], Optional[str]]] = []

    for post in posts:
        # Filtering by date
        post_date = datetime.fromtimestamp(post.get("date", 0))
        if date_from and post_date < date_from:
            continue

        text: Optional[str] = post.get("text", None)
        if text is not None:
            text = text.strip()
        if text == "":
            text = None

        attachments: List[dict] = post.get("attachments", [])
        like_count: int = post.get("likes", {}).get("count", 0)

        # Searching for first image
        image_url: Optional[str] = None
        for att in attachments:
            if att.get("type") == "photo":
                sizes = att["photo"].get("sizes", [])
                if sizes:
                    largest = max(sizes, key=lambda s: s["width"] * s["height"])
                    image_url = largest["url"]
                    break

        # Ignoring posts without text and without an image at the same time
        if image_url is None and text is None:
            continue

        candidates.append((like_count, text, image_url))

    # Sorting by likes in descending
    candidates.sort(reverse=True, key=lambda x: x[0])
    top_candidates = candidates[:3]

    result: List[Tuple[Optional[Image.Image], Optional[str]]] = []

    async with aiohttp.ClientSession() as session:
        for _, text, url in top_candidates:
            img: Optional[Image.Image] = None
            if url:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            img_bytes = await response.read()
                            img = Image.open(BytesIO(img_bytes))
                        else:
                            print(f"⚠️ Не удалось загрузить изображение: {url}")
                except Exception as e:
                    print(f"❌ Ошибка при загрузке изображения: {e}")

            result.append((img, text))

    return result


def run_api():
    """Synchronous launch of FastAPI server"""
    uvicorn.run(app, host="localhost", port=8000, log_level="info")
