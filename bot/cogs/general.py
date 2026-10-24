import discord
from discord import app_commands
from discord.ext import commands

from database import record_command


class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "ping")
        ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! **{ms}ms**", ephemeral=True)

    @app_commands.command(name="help", description="List available commands")
    async def help_cmd(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "help")
        embed = discord.Embed(
            title="AIO Bot — Commands",
            description="Use slash commands. Manage settings at your dashboard.",
            color=discord.Color.blurple(),
        )
        embed.add_field(
            name="General",
            value="`/ping` `/help` `/userinfo` `/serverinfo` `/avatar`",
            inline=False,
        )
        embed.add_field(
            name="Utility",
            value="`/poll` `/say` `/embed`",
            inline=False,
        )
        embed.add_field(
            name="Moderation",
            value="`/kick` `/ban` `/timeout` `/untimeout` `/clear`",
            inline=False,
        )
        embed.add_field(
            name="Music (Lavalink)",
            value="`/play` `/pause` `/resume` `/skip` `/stop` `/queue` `/nowplaying` `/volume`",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Info about a user")
    @app_commands.describe(member="Member to inspect")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        member: discord.Member | None = None,
    ) -> None:
        await record_command(interaction.guild_id, "userinfo")
        member = member or interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(member.id) if interaction.guild else None
        if not member:
            await interaction.response.send_message("User not found.", ephemeral=True)
            return
        embed = discord.Embed(title=str(member), color=member.color or discord.Color.blurple())
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(
            name="Joined",
            value=discord.utils.format_dt(member.joined_at, "R") if member.joined_at else "—",
            inline=True,
        )
        embed.add_field(
            name="Account created",
            value=discord.utils.format_dt(member.created_at, "R"),
            inline=True,
        )
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        embed.add_field(
            name=f"Roles ({len(roles)})",
            value=", ".join(roles[:15]) or "None",
            inline=False,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Info about this server")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "serverinfo")
        if not interaction.guild:
            await interaction.response.send_message("Guild only.", ephemeral=True)
            return
        g = interaction.guild
        embed = discord.Embed(title=g.name, color=discord.Color.green())
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        embed.add_field(name="Owner", value=g.owner.mention if g.owner else "—", inline=True)
        embed.add_field(name="Members", value=g.member_count or len(g.members), inline=True)
        embed.add_field(name="Channels", value=len(g.channels), inline=True)
        embed.add_field(name="Roles", value=len(g.roles), inline=True)
        embed.add_field(name="Created", value=discord.utils.format_dt(g.created_at, "D"), inline=True)
        embed.add_field(name="ID", value=g.id, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Show a user's avatar")
    @app_commands.describe(member="Whose avatar")
    async def avatar(
        self,
        interaction: discord.Interaction,
        member: discord.User | None = None,
    ) -> None:
        await record_command(interaction.guild_id, "avatar")
        user = member or interaction.user
        embed = discord.Embed(title=f"{user.name}'s avatar")
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot))
