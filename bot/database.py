from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import MONGODB_URI

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(MONGODB_URI)
        _db = _client.get_default_database()
    return _db


DEFAULT_GUILD_SETTINGS = {
    "prefix_commands_enabled": True,
    "welcome_enabled": False,
    "welcome_channel_id": None,
    "welcome_message": "Welcome {user} to **{server}**!",
    "mod_log_channel_id": None,
    "auto_mod_spam": False,
}


async def ensure_guild(guild_id: int) -> dict[str, Any]:
    db = get_db()
    doc = await db.guilds.find_one({"guild_id": guild_id})
    if doc:
        return doc
    payload = {
        "guild_id": guild_id,
        **DEFAULT_GUILD_SETTINGS,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
    await db.guilds.insert_one(payload)
    return payload


async def get_guild_settings(guild_id: int) -> dict[str, Any]:
    doc = await ensure_guild(guild_id)
    return {k: doc.get(k, v) for k, v in DEFAULT_GUILD_SETTINGS.items()}


async def record_command(guild_id: int | None, command: str) -> None:
    db = get_db()
    await db.command_stats.insert_one(
        {
            "guild_id": guild_id,
            "command": command,
            "at": datetime.now(timezone.utc),
        }
    )
    await db.bot_metrics.update_one(
        {},
        {
            "$inc": {"commands_total": 1},
            "$set": {"last_seen": datetime.now(timezone.utc)},
        },
        upsert=True,
    )


def _track_payload(track: Any | None) -> dict[str, Any] | None:
    if track is None:
        return None
    return {
        "title": getattr(track, "title", "Unknown"),
        "author": getattr(track, "author", "Unknown"),
        "uri": getattr(track, "uri", None),
        "artwork": getattr(track, "artwork", None),
        "length_ms": getattr(track, "length", 0),
    }


async def sync_music_state(guild_id: int, player: Any | None) -> None:
    db = get_db()
    if player is None:
        payload = {
            "guild_id": guild_id,
            "connected": False,
            "channel_id": None,
            "paused": False,
            "volume": 100,
            "position_ms": 0,
            "current": None,
            "queue": [],
            "updated_at": datetime.now(timezone.utc),
        }
    else:
        queue_items = []
        try:
            for t in list(player.queue)[:25]:
                queue_items.append(_track_payload(t))
        except TypeError:
            pass
        current = player.current
        payload = {
            "guild_id": guild_id,
            "connected": player.connected,
            "channel_id": player.channel.id if player.channel else None,
            "paused": player.paused,
            "volume": player.volume,
            "position_ms": player.position,
            "current": _track_payload(current),
            "queue": [q for q in queue_items if q],
            "updated_at": datetime.now(timezone.utc),
        }
    await db.guild_music.update_one(
        {"guild_id": guild_id},
        {"$set": payload},
        upsert=True,
    )


async def clear_music_state(guild_id: int) -> None:
    await sync_music_state(guild_id, None)


async def log_moderation(
    guild_id: int,
    action: str,
    moderator_id: int,
    target_id: int,
    reason: str | None,
) -> None:
    db = get_db()
    await db.mod_logs.insert_one(
        {
            "guild_id": guild_id,
            "action": action,
            "moderator_id": moderator_id,
            "target_id": target_id,
            "reason": reason,
            "at": datetime.now(timezone.utc),
        }
    )
