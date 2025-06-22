from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
from config import REDIRECT_URI, VK_CLIENT_ID, USER_STATES, STATE, CODE_VERIFIER
from config import app, templates, lock


@app.get("/callback", response_class=HTMLResponse)
async def callback(request: Request, code: str = None, state: str = None):
    if state != STATE:
        raise HTTPException(status_code=400, detail="Invalid state")
    # Token exchange via VK ID PKCE Flow
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vkid.vk.com/token",
            data={
                "grant_type": "authorization_code",
                "client_id": VK_CLIENT_ID,
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": CODE_VERIFIER
            },  
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    data = response.json()
    if "error" in data:
        return {"error": data.get("error_description", data["error"])}

    with lock:
        USER_STATES[request.client.host] = {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "id_token": data.get("id_token")
        }
    return templates.TemplateResponse("success.html", {"request": request, "user_id": request.client.host})
