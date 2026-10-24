import asyncio
import logging
import os
import sys
from datetime import datetime, timezone

import discord
from discord.ext import commands

import config
from database import get_db

if config.LAVALINK_ENABLED:
    import wavelink

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("aio-bot")


class AIOBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        get_db()
        if config.LAVALINK_ENABLED:
            node = wavelink.Node(
                uri=config.lavalink_uri(),
                password=config.LAVALINK_PASSWORD,
                identifier=config.LAVALINK_IDENTIFIER,
            )
            await wavelink.Pool.connect(nodes=[node], client=self, cache_capacity=256)
            log.info("Lavalink connected to %s", config.lavalink_uri())
            db = get_db()
            await db.bot_metrics.update_one(
                {},
                {
                    "$set": {
                        "lavalink_connected": True,
                        "lavalink_uri": config.lavalink_uri(),
                        "last_seen": datetime.now(timezone.utc),
                    }
                },
                upsert=True,
            )

        cogs_dir = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(cogs_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                if filename == "music.py" and not config.LAVALINK_ENABLED:
                    continue
                ext = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(ext)
                    log.info("Loaded extension %s", ext)
                except Exception:
                    log.exception("Failed to load %s", ext)

        # Global slash commands sync
        await self.tree.sync()
        log.info("Slash commands synced globally")

    async def on_ready(self) -> None:
        status = getattr(discord.Status, config.BOT_STATUS, discord.Status.online)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servers | /help",
            ),
            status=status,
        )
        log.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "?")

    async def on_guild_join(self, guild: discord.Guild) -> None:
        from database import ensure_guild

        await ensure_guild(guild.id)
        log.info("Joined guild %s (%s)", guild.name, guild.id)


def main() -> None:
    bot = AIOBot()
    try:
        bot.run(config.DISCORD_TOKEN, log_handler=None)
    except KeyboardInterrupt:
        log.info("Shutting down...")


if __name__ == "__main__":
    if sys.platform != "win32":
        try:
            import uvloop

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            pass
    main()
