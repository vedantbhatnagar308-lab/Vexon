from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

DEFAULT_GUILD_SETTINGS = {
    "welcome_enabled": False,
    "welcome_channel_id": None,
    "welcome_message": "Welcome {user} to **{server}**!",
    "mod_log_channel_id": None,
    "auto_mod_spam": False,
}


def get_db() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
        _db = _client.get_default_database()
    return _db
