import discord
from discord.ext import commands

from database import ensure_guild, get_guild_settings, record_command


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        await ensure_guild(member.guild.id)
        settings = await get_guild_settings(member.guild.id)
        if not settings.get("welcome_enabled"):
            return
        ch_id = settings.get("welcome_channel_id")
        if not ch_id:
            return
        channel = member.guild.get_channel(int(ch_id))
        if not isinstance(channel, discord.TextChannel):
            return
        msg = settings.get("welcome_message") or "Welcome {user}!"
        text = msg.replace("{user}", member.mention).replace("{server}", member.guild.name)
        await channel.send(text)

    @commands.hybrid_command(name="sync", description="Sync slash commands (owner)")
    @commands.is_owner()
    async def sync(self, ctx: commands.Context) -> None:
        await record_command(ctx.guild.id if ctx.guild else None, "sync")
        synced = await self.bot.tree.sync()
        await ctx.send(f"Synced **{len(synced)}** command(s).")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Events(bot))
