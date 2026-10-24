from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from auth import create_access_token, get_current_user, user_can_manage_guild
from config import settings
from database import DEFAULT_GUILD_SETTINGS, get_db

DISCORD_API = "https://discord.com/api/v10"
MANAGE_GUILD = 0x20


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_db()
    yield


app = FastAPI(title="AIO Bot Dashboard API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GuildSettingsUpdate(BaseModel):
    welcome_enabled: bool | None = None
    welcome_channel_id: str | None = None
    welcome_message: str | None = Field(None, max_length=2000)
    mod_log_channel_id: str | None = None
    auto_mod_spam: bool | None = None


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/auth/discord/url")
async def discord_auth_url() -> dict[str, str]:
    params = {
        "client_id": settings.DISCORD_CLIENT_ID,
        "redirect_uri": settings.DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds",
    }
    return {"url": f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"}


@app.post("/auth/discord/callback")
async def discord_callback(body: dict[str, str]) -> dict[str, Any]:
    code = body.get("code")
    if not code:
        raise HTTPException(400, "Missing code")
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": settings.DISCORD_CLIENT_ID,
                "client_secret": settings.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.DISCORD_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_res.status_code != 200:
            raise HTTPException(401, "Discord token exchange failed")
        tokens = token_res.json()
        access = tokens["access_token"]
        user_res = await client.get(
            f"{DISCORD_API}/users/@me",
            headers={"Authorization": f"Bearer {access}"},
        )
        guilds_res = await client.get(
            f"{DISCORD_API}/users/@me/guilds",
            headers={"Authorization": f"Bearer {access}"},
        )
    user = user_res.json()
    guilds_raw = guilds_res.json()
    manageable = []
    for g in guilds_raw:
        perm = int(g.get("permissions", 0))
        if g.get("owner") or (perm & MANAGE_GUILD):
            manageable.append(
                {
                    "id": g["id"],
                    "name": g["name"],
                    "icon": g.get("icon"),
                    "owner": g.get("owner", False),
                    "permissions": str(perm),
                }
            )
    token = create_access_token(
        {
            "sub": user["id"],
            "username": user.get("username"),
            "avatar": user.get("avatar"),
            "guilds": manageable,
        }
    )
    return {
        "access_token": token,
        "user": {
            "id": user["id"],
            "username": user.get("username"),
            "global_name": user.get("global_name"),
            "avatar": user.get("avatar"),
        },
        "guilds": manageable,
    }


@app.get("/me")
async def me(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "id": user["sub"],
        "username": user.get("username"),
        "avatar": user.get("avatar"),
        "guilds": user.get("guilds", []),
    }


@app.get("/stats")
async def bot_stats(
    user: dict = Depends(get_current_user),
    _: str | None = Header(None, alias="X-API-Secret"),
) -> dict[str, Any]:
    db = get_db()
    metrics = await db.bot_metrics.find_one({}) or {}
    lavalink_ok = bool(metrics.get("lavalink_connected"))
    guild_count = await db.guilds.count_documents({})
    recent = await db.command_stats.count_documents(
        {"at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)}}
    )
    last = metrics.get("last_seen")
    return {
        "commands_total": metrics.get("commands_total", 0),
        "commands_today": recent,
        "guilds_configured": guild_count,
        "lavalink_connected": lavalink_ok,
        "last_seen": last.isoformat() if last else None,
    }


@app.get("/guilds/{guild_id}/settings")
async def get_settings(guild_id: str, user: dict = Depends(get_current_user)) -> dict[str, Any]:
    if not user_can_manage_guild(user, guild_id):
        raise HTTPException(403, "No permission for this server")
    db = get_db()
    doc = await db.guilds.find_one({"guild_id": int(guild_id)})
    if not doc:
        return {"guild_id": guild_id, **DEFAULT_GUILD_SETTINGS}
    out = {"guild_id": guild_id}
    for k in DEFAULT_GUILD_SETTINGS:
        val = doc.get(k, DEFAULT_GUILD_SETTINGS[k])
        if k.endswith("_channel_id") and val is not None:
            val = str(val)
        out[k] = val
    return out


@app.patch("/guilds/{guild_id}/settings")
async def patch_settings(
    guild_id: str,
    body: GuildSettingsUpdate,
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    if not user_can_manage_guild(user, guild_id):
        raise HTTPException(403, "No permission for this server")
    db = get_db()
    updates: dict[str, Any] = {
        k: v
        for k, v in body.model_dump(exclude_none=True).items()
    }
    for key in ("welcome_channel_id", "mod_log_channel_id"):
        if key in updates and updates[key] is not None:
            updates[key] = int(updates[key])
    updates["updated_at"] = datetime.now(timezone.utc)
    await db.guilds.update_one(
        {"guild_id": int(guild_id)},
        {"$set": updates, "$setOnInsert": {"guild_id": int(guild_id), "created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return await get_settings(guild_id, user)


@app.get("/music/lavalink")
async def lavalink_public(_: dict = Depends(get_current_user)) -> dict[str, Any]:
    return {
        "label": settings.LAVALINK_PUBLIC_LABEL,
        "host": settings.LAVALINK_PUBLIC_HOST,
        "port": settings.LAVALINK_PUBLIC_PORT,
    }


@app.get("/guilds/{guild_id}/music")
async def guild_music(
    guild_id: str,
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    if not user_can_manage_guild(user, guild_id):
        raise HTTPException(403, "No permission for this server")
    db = get_db()
    doc = await db.guild_music.find_one({"guild_id": int(guild_id)})
    if not doc:
        return {
            "guild_id": guild_id,
            "connected": False,
            "paused": False,
            "volume": 100,
            "position_ms": 0,
            "current": None,
            "queue": [],
            "updated_at": None,
        }
    doc.pop("_id", None)
    if doc.get("updated_at"):
        doc["updated_at"] = doc["updated_at"].isoformat()
    doc["guild_id"] = str(doc.get("guild_id", guild_id))
    if doc.get("channel_id") is not None:
        doc["channel_id"] = str(doc["channel_id"])
    return doc


@app.get("/guilds/{guild_id}/mod-logs")
async def mod_logs(
    guild_id: str,
    user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
) -> list[dict[str, Any]]:
    if not user_can_manage_guild(user, guild_id):
        raise HTTPException(403, "No permission for this server")
    db = get_db()
    cursor = db.mod_logs.find({"guild_id": int(guild_id)}).sort("at", -1).limit(limit)
    logs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        if doc.get("at"):
            doc["at"] = doc["at"].isoformat()
        logs.append(doc)
    return logs


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
