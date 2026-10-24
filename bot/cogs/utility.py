import discord
from discord import app_commands
from discord.ext import commands

from database import record_command


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="poll", description="Create a quick yes/no poll")
    @app_commands.describe(question="Poll question")
    async def poll(self, interaction: discord.Interaction, question: str) -> None:
        await record_command(interaction.guild_id, "poll")
        embed = discord.Embed(title="Poll", description=question, color=discord.Color.gold())
        embed.set_footer(text=f"Asked by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @app_commands.command(name="say", description="Make the bot say something")
    @app_commands.describe(
        message="Text to send",
        channel="Channel (defaults to current)",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def say(
        self,
        interaction: discord.Interaction,
        message: str,
        channel: discord.TextChannel | None = None,
    ) -> None:
        await record_command(interaction.guild_id, "say")
        target = channel or interaction.channel
        if not isinstance(target, discord.TextChannel):
            await interaction.response.send_message("Invalid channel.", ephemeral=True)
            return
        await target.send(message)
        await interaction.response.send_message(f"Sent to {target.mention}.", ephemeral=True)

    @app_commands.command(name="embed", description="Send a custom embed")
    @app_commands.describe(
        title="Embed title",
        description="Embed body",
        color="Hex color e.g. #5865F2",
    )
    @app_commands.default_permissions(manage_messages=True)
    async def embed_cmd(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        color: str = "#5865F2",
    ) -> None:
        await record_command(interaction.guild_id, "embed")
        try:
            c = int(color.lstrip("#"), 16)
        except ValueError:
            c = 0x5865F2
        embed = discord.Embed(title=title, description=description, color=c)
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Utility(bot))
