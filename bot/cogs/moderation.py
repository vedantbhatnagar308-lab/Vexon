import discord
from discord import app_commands
from discord.ext import commands

from database import get_guild_settings, log_moderation, record_command


def mod_log_channel(guild: discord.Guild, settings: dict) -> discord.TextChannel | None:
    cid = settings.get("mod_log_channel_id")
    if not cid:
        return None
    ch = guild.get_channel(int(cid))
    return ch if isinstance(ch, discord.TextChannel) else None


async def send_mod_log(
    guild: discord.Guild,
    settings: dict,
    embed: discord.Embed,
) -> None:
    ch = mod_log_channel(guild, settings)
    if ch:
        await ch.send(embed=embed)


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_check(self, interaction: discord.Interaction) -> bool:
        return interaction.guild is not None

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @app_commands.default_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None,
    ) -> None:
        await record_command(interaction.guild_id, "kick")
        if member.top_role >= interaction.user.top_role:  # type: ignore[union-attr]
            await interaction.response.send_message(
                "You cannot kick someone with equal or higher role.",
                ephemeral=True,
            )
            return
        await member.kick(reason=reason or f"Kicked by {interaction.user}")
        settings = await get_guild_settings(interaction.guild_id)  # type: ignore[arg-type]
        await log_moderation(
            interaction.guild_id,  # type: ignore[arg-type]
            "kick",
            interaction.user.id,
            member.id,
            reason,
        )
        embed = discord.Embed(title="Member kicked", color=discord.Color.orange())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderator", value=str(interaction.user), inline=True)
        embed.add_field(name="Reason", value=reason or "—", inline=False)
        await send_mod_log(interaction.guild, settings, embed)  # type: ignore[arg-type]
        await interaction.response.send_message(
            f"Kicked **{member.display_name}**.", ephemeral=True
        )

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.describe(member="Member to ban", reason="Reason")
    @app_commands.default_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None,
    ) -> None:
        await record_command(interaction.guild_id, "ban")
        if member.top_role >= interaction.user.top_role:  # type: ignore[union-attr]
            await interaction.response.send_message(
                "You cannot ban someone with equal or higher role.",
                ephemeral=True,
            )
            return
        await member.ban(reason=reason or f"Banned by {interaction.user}")
        settings = await get_guild_settings(interaction.guild_id)  # type: ignore[arg-type]
        await log_moderation(
            interaction.guild_id,  # type: ignore[arg-type]
            "ban",
            interaction.user.id,
            member.id,
            reason,
        )
        embed = discord.Embed(title="Member banned", color=discord.Color.red())
        embed.add_field(name="User", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderator", value=str(interaction.user), inline=True)
        embed.add_field(name="Reason", value=reason or "—", inline=False)
        await send_mod_log(interaction.guild, settings, embed)  # type: ignore[arg-type]
        await interaction.response.send_message(
            f"Banned **{member.display_name}**.", ephemeral=True
        )

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(
        member="Member",
        minutes="Duration in minutes (max 40320)",
        reason="Reason",
    )
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 40320],
        reason: str | None = None,
    ) -> None:
        await record_command(interaction.guild_id, "timeout")
        import datetime as dt

        until = discord.utils.utcnow() + dt.timedelta(minutes=minutes)
        await member.timeout(until, reason=reason or f"By {interaction.user}")
        settings = await get_guild_settings(interaction.guild_id)  # type: ignore[arg-type]
        await log_moderation(
            interaction.guild_id,  # type: ignore[arg-type]
            "timeout",
            interaction.user.id,
            member.id,
            reason,
        )
        await interaction.response.send_message(
            f"Timed out **{member.display_name}** for {minutes}m.",
            ephemeral=True,
        )

    @app_commands.command(name="untimeout", description="Remove a member's timeout")
    @app_commands.describe(member="Member")
    @app_commands.default_permissions(moderate_members=True)
    async def untimeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        await record_command(interaction.guild_id, "untimeout")
        await member.timeout(None, reason=f"Untimeout by {interaction.user}")
        await log_moderation(
            interaction.guild_id,  # type: ignore[arg-type]
            "untimeout",
            interaction.user.id,
            member.id,
            None,
        )
        await interaction.response.send_message(
            f"Removed timeout from **{member.display_name}**.",
            ephemeral=True,
        )

    @app_commands.command(name="clear", description="Delete recent messages")
    @app_commands.describe(amount="How many messages (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
    ) -> None:
        await record_command(interaction.guild_id, "clear")
        if not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Text channel only.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted **{len(deleted)}** messages.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
