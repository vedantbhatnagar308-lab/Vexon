from __future__ import annotations

import discord
import wavelink
from discord import app_commands
from discord.ext import commands, tasks

from database import clear_music_state, record_command, sync_music_state


def format_duration(ms: int) -> str:
    if ms <= 0:
        return "0:00"
    seconds = ms // 1000
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def player_embed(player: wavelink.Player, title: str) -> discord.Embed:
    track = player.current
    embed = discord.Embed(title=title, color=0x1DB954)
    if track:
        embed.description = f"**[{track.title}]({track.uri})**"
        embed.add_field(name="Artist", value=track.author or "Unknown", inline=True)
        embed.add_field(
            name="Duration",
            value=format_duration(track.length),
            inline=True,
        )
        embed.add_field(name="Volume", value=f"{player.volume}%", inline=True)
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
    else:
        embed.description = "Nothing playing."
    q_len = len(player.queue)
    embed.set_footer(text=f"Queue: {q_len} track{'s' if q_len != 1 else ''}")
    return embed


class Music(commands.Cog):
    """Lavalink-powered music commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_load(self) -> None:
        if not self.music_sync_loop.is_running():
            self.music_sync_loop.start()

    async def cog_unload(self) -> None:
        self.music_sync_loop.cancel()

    @tasks.loop(seconds=8)
    async def music_sync_loop(self) -> None:
        for guild in self.bot.guilds:
            player = guild.voice_client
            if isinstance(player, wavelink.Player) and player.connected:
                await sync_music_state(guild.id, player)

    @music_sync_loop.before_loop
    async def before_sync(self) -> None:
        await self.bot.wait_until_ready()

    def _voice_error(self, interaction: discord.Interaction) -> str | None:
        if not interaction.guild or not interaction.user:
            return "Guild only."
        member = interaction.user
        if not isinstance(member, discord.Member) or not member.voice or not member.voice.channel:
            return "Join a voice channel first."
        return None

    async def resolve_player(self, interaction: discord.Interaction) -> wavelink.Player | None:
        if not interaction.guild:
            return None
        member = interaction.user
        if not isinstance(member, discord.Member) or not member.voice or not member.voice.channel:
            return None
        channel = member.voice.channel
        player: wavelink.Player | None = interaction.guild.voice_client  # type: ignore[assignment]
        if player is None:
            player = await channel.connect(cls=wavelink.Player, self_deaf=True)
        elif player.channel != channel:
            await player.move_to(channel)
        return player

    @app_commands.command(name="play", description="Play a song (URL or search)")
    @app_commands.describe(query="YouTube URL or search terms")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        await record_command(interaction.guild_id, "play")
        err = self._voice_error(interaction)
        if err:
            await interaction.response.send_message(err, ephemeral=True)
            return
        await interaction.response.defer()
        player = await self.resolve_player(interaction)
        if not player:
            await interaction.followup.send("Could not join voice.", ephemeral=True)
            return
        try:
            result = await wavelink.Playable.search(query)
        except wavelink.LavalinkException as exc:
            await interaction.followup.send(f"Lavalink error: {exc}", ephemeral=True)
            return
        if result is None:
            await interaction.followup.send("No results found.", ephemeral=True)
            return
        if hasattr(result, "tracks"):
            track_list = result.tracks
        elif isinstance(result, list):
            track_list = result
        else:
            track_list = [result]
        if not track_list:
            await interaction.followup.send("No results found.", ephemeral=True)
            return
        track = track_list[0]
        if player.playing or player.paused:
            player.queue.put(track)
            await sync_music_state(interaction.guild_id, player)  # type: ignore[arg-type]
            await interaction.followup.send(
                embed=player_embed(player, "Added to queue"),
            )
            return
        await player.play(track)
        await sync_music_state(interaction.guild_id, player)  # type: ignore[arg-type]
        await interaction.followup.send(embed=player_embed(player, "Now playing"))

    @app_commands.command(name="pause", description="Pause playback")
    async def pause(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "pause")
        player = interaction.guild.voice_client if interaction.guild else None  # type: ignore[union-attr]
        if not isinstance(player, wavelink.Player) or not player.playing:
            await interaction.response.send_message("Nothing is playing.", ephemeral=True)
            return
        await player.pause(True)
        await sync_music_state(interaction.guild_id, player)  # type: ignore[arg-type]
        await interaction.response.send_message("Paused.", ephemeral=True)

    @app_commands.command(name="resume", description="Resume playback")
    async def resume(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "resume")
        player = interaction.guild.voice_client if interaction.guild else None  # type: ignore[union-attr]
        if not isinstance(player, wavelink.Player) or not player.paused:
            await interaction.response.send_message("Not paused.", ephemeral=True)
            return
        await player.pause(False)
        await sync_music_state(interaction.guild_id, player)  # type: ignore[arg-type]
        await interaction.response.send_message("Resumed.", ephemeral=True)

    @app_commands.command(name="skip", description="Skip the current track")
    async def skip(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "skip")
        player = interaction.guild.voice_client if interaction.guild else None  # type: ignore[union-attr]
        if not isinstance(player, wavelink.Player):
            await interaction.response.send_message("Not connected.", ephemeral=True)
            return
        await player.skip(force=True)
        await sync_music_state(interaction.guild_id, player)  # type: ignore[arg-type]
        await interaction.response.send_message("Skipped.", ephemeral=True)

    @app_commands.command(name="stop", description="Stop and clear the queue")
    async def stop(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "stop")
        player = interaction.guild.voice_client if interaction.guild else None  # type: ignore[union-attr]
        if not isinstance(player, wavelink.Player):
            await interaction.response.send_message("Not connected.", ephemeral=True)
            return
        player.queue.clear()
        await player.disconnect()
        await clear_music_state(interaction.guild_id)  # type: ignore[arg-type]
        await interaction.response.send_message("Stopped and disconnected.", ephemeral=True)

    @app_commands.command(name="queue", description="Show the music queue")
    async def queue_cmd(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "queue")
        player = interaction.guild.voice_client if interaction.guild else None  # type: ignore[union-attr]
        if not isinstance(player, wavelink.Player):
            await interaction.response.send_message("Not connected.", ephemeral=True)
            return
        lines = []
        if player.current:
            lines.append(f"**Now:** {player.current.title}")
        for i, t in enumerate(list(player.queue)[:15], start=1):
            lines.append(f"`{i}.` {t.title} — {format_duration(t.length)}")
        if not lines:
            lines.append("Queue is empty.")
        embed = discord.Embed(
            title="Music queue",
            description="\n".join(lines),
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Currently playing track")
    async def nowplaying(self, interaction: discord.Interaction) -> None:
        await record_command(interaction.guild_id, "nowplaying")
        player = interaction.guild.voice_client if interaction.guild else None  # type: ignore[union-attr]
        if not isinstance(player, wavelink.Player) or not player.current:
            await interaction.response.send_message("Nothing playing.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=player_embed(player, "Now playing"),
        )

    @app_commands.command(name="volume", description="Set playback volume (0-200)")
    @app_commands.describe(level="Volume percentage")
    async def volume(
        self,
        interaction: discord.Interaction,
        level: app_commands.Range[int, 0, 200],
    ) -> None:
        await record_command(interaction.guild_id, "volume")
        player = interaction.guild.voice_client if interaction.guild else None  # type: ignore[union-attr]
        if not isinstance(player, wavelink.Player):
            await interaction.response.send_message("Not connected.", ephemeral=True)
            return
        await player.set_volume(level)
        await sync_music_state(interaction.guild_id, player)  # type: ignore[arg-type]
        await interaction.response.send_message(f"Volume set to **{level}%**.", ephemeral=True)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEvent) -> None:
        player = payload.player
        if not player or not player.guild:
            return
        await sync_music_state(player.guild.id, player)

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEvent) -> None:
        player = payload.player
        if not player or not player.guild:
            return
        await sync_music_state(player.guild.id, player)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Music(bot))
