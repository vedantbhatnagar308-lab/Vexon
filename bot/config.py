import os
from dotenv import load_dotenv

load_dotenv()


def require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DISCORD_TOKEN = require("DISCORD_TOKEN")
DISCORD_CLIENT_ID = require("DISCORD_CLIENT_ID")
MONGODB_URI = require("MONGODB_URI")
API_SECRET = os.getenv("API_SECRET", "")

STATUS_MAP = {
    "online": "online",
    "idle": "idle",
    "dnd": "dnd",
    "invisible": "invisible",
}
BOT_STATUS = STATUS_MAP.get(os.getenv("BOT_STATUS", "online").lower(), "online")

LAVALINK_ENABLED = os.getenv("LAVALINK_ENABLED", "false").lower() in ("1", "true", "yes")
LAVALINK_HOST = os.getenv("LAVALINK_HOST", "localhost")
LAVALINK_PORT = int(os.getenv("LAVALINK_PORT", "2333"))
LAVALINK_PASSWORD = os.getenv("LAVALINK_PASSWORD", "youshallnotpass")
LAVALINK_SECURE = os.getenv("LAVALINK_SECURE", "false").lower() in ("1", "true", "yes")
LAVALINK_IDENTIFIER = os.getenv("LAVALINK_IDENTIFIER", "main")


def lavalink_uri() -> str:
    scheme = "https" if LAVALINK_SECURE else "http"
    return f"{scheme}://{LAVALINK_HOST}:{LAVALINK_PORT}"
