from typing import List, Optional, Tuple, Union
from PIL import Image
import aiohttp
from io import BytesIO
import uvicorn
from datetime import datetime
from config import app


async def resolve_group_id(group_input: str, access_token: str) -> str:
    """
    Resolve various VK group ID formats to a numeric ID.

    Args:
        group_input (str): Group ID, short name, or prefix-based (e.g. 'public123').
        access_token (str): VK user access token.

    Returns:
        str: Numeric group ID.

    Raises:
        ValueError: If VK API returns an error.
    """
    if group_input.isdigit():
        return group_input

    # Remove 'public' or 'club' prefixes
    if group_input.startswith("public") or group_input.startswith("club"):
        possible_id = group_input.lstrip("club").lstrip("public")
        if possible_id.isdigit():
            return possible_id

    # Try resolving via VK API
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
                raise ValueError(f"VK API error: {data['error'].get('error_msg', 'unknown error')}")
            return str(data["response"][0]["id"])


async def get_group_posts(group_id: str, access_token: str, count: int = 100) -> Union[List[dict], dict]:
    """
    Fetch the latest posts from a VK group's wall.

    Args:
        group_id (str): Numeric group ID or short name.
        access_token (str): VK user access token.
        count (int): Number of posts to fetch (default 100).

    Returns:
        Union[List[dict], dict]: List of post dicts, or error dict if failed.
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
                error_msg = data["error"].get("error_msg", "Unknown error")
                return {"error": error_msg}
            return data.get("response", {}).get("items", [])


async def sorting_posts(
    posts: List[dict],
    date_from: Optional[datetime] = None
) -> List[Tuple[Optional[Image.Image], Optional[str]]]:
    """
    Filters and sorts posts by number of likes and extracts top 3.

    Args:
        posts (List[dict]): List of VK post dictionaries.
        date_from (Optional[datetime]): Only include posts after this date.

    Returns:
        List[Tuple[Optional[Image.Image], Optional[str]]]:
            Top 3 posts as (image, text) pairs.
    """
    candidates: List[Tuple[int, Optional[str], Optional[str]]] = []

    for post in posts:
        # Date filter
        post_date = datetime.fromtimestamp(post.get("date", 0))
        if date_from and post_date < date_from:
            continue

        # Clean and extract text
        text: Optional[str] = post.get("text", None)
        if text:
            text = text.strip()
        if text == "":
            text = None

        # Search for first image in attachments
        attachments: List[dict] = post.get("attachments", [])
        like_count: int = post.get("likes", {}).get("count", 0)
        image_url: Optional[str] = None

        for att in attachments:
            if att.get("type") == "photo":
                sizes = att["photo"].get("sizes", [])
                if sizes:
                    # Pick the largest image by area
                    largest = max(sizes, key=lambda s: s["width"] * s["height"])
                    image_url = largest["url"]
                    break

        # Skip posts with neither image nor text
        if image_url is None and text is None:
            continue

        candidates.append((like_count, text, image_url))

    # Sort by like count (descending) and take top 3
    candidates.sort(reverse=True, key=lambda x: x[0])
    top_candidates = candidates[:3]

    result: List[Tuple[Optional[Image.Image], Optional[str]]] = []

    # Download images for top posts
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
                            print(f"⚠️ Failed to download image: {url}")
                except Exception as e:
                    print(f"❌ Image fetch error: {e}")
            result.append((img, text))

    return result


def run_api() -> None:
    """
    Launch FastAPI server using uvicorn.
    This function is used as a thread target in main.py.
    """
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
