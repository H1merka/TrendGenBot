from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
from config import REDIRECT_URI, VK_CLIENT_ID, USER_STATES, STATE, CODE_VERIFIER
from config import app, templates, lock
from typing import Optional, Dict


@app.get("/")
def home() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict: A simple message to confirm that the server is running.
    """
    return {"message": "Server is alive"}


@app.get("/callback", response_class=HTMLResponse)
async def callback(
    request: Request, 
    code: Optional[str] = None, 
    state: Optional[str] = None
) -> HTMLResponse | Dict[str, str]:
    """
    OAuth2 callback endpoint for VK ID using PKCE flow.

    This endpoint is triggered after the user authorizes access via VK.
    It exchanges the provided authorization code for access tokens.

    Args:
        request (Request): The incoming FastAPI request object.
        code (str, optional): The authorization code provided by VK.
        state (str, optional): The CSRF protection state returned from VK.

    Returns:
        HTMLResponse or dict: Renders a success template or returns an error response.
    """
    # Validate the 'state' parameter to protect against CSRF attacks
    if state != STATE:
        raise HTTPException(status_code=400, detail="Invalid state")

    # Exchange authorization code for access and refresh tokens
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

    # If VK returns an error, forward it to the user
    if "error" in data:
        return {"error": data.get("error_description", data["error"])}

    # Store the token data in a global dictionary, using client IP as the key
    with lock:
        USER_STATES[request.client.host] = {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token"),
            "id_token": data.get("id_token")
        }

    # Render success page
    return templates.TemplateResponse("success.html", {"request": request, "user_id": request.client.host})
