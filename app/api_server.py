from fastapi import Request
import httpx
from config import SECRET, REDIRECT_URI, VK_CLIENT_ID, USER_STATES
from config import app, templates, lock


@app.get("/callback")
async def callback(request: Request, code: str):
    """Handles VK OAuth callback with authorization code"""
    # Exchange the authorization code for an access token
    async with httpx.AsyncClient() as client:
        token_response: httpx.Response = await client.get(
            "https://oauth.vk.com/access_token",
            params={
                "client_id": VK_CLIENT_ID,
                "client_secret": SECRET,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        )

    # If VK did not return a 200 OK, return error
    if token_response.status_code != 200:
        return {"error": "Failed to get token"}

    data: dict = token_response.json()
    access_token: str | None = data.get("access_token")
    user_id: int | None = data.get("user_id")

    # Save token if both access_token and user_id are present
    if access_token and user_id:
        with lock:
            USER_STATES[user_id] = {"token": access_token}
        print(f"[+] Saved token for user {user_id}")
        return templates.TemplateResponse("success.html", {"request": request, "user_id": user_id})

    # Return error if token or user_id are missing
    return {"error": "Missing token or user_id"}
