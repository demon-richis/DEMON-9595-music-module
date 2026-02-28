import discord
from discord.ext import commands, tasks
import asyncio
import random
import time
from utils import YTDLSource, format_duration, get_lyrics
from config import (
    ACCENT_COLOR, ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR,
    NOW_PLAYING_COLOR, EQ_PRESETS, EQ_DESCRIPTIONS,
    AUTOPLAY_GENRES, GENIUS_TOKEN
)
# ✦ Import all embeds from the embeds folder
from embeds.now_playing import now_playing_embed
from embeds.queue       import queue_embed, added_to_queue_embed
from embeds.controls    import skip_embed, pause_embed, resume_embed, leave_embed, shuffle_embed, queue_finished_embed
from embeds.info        import (help_embed, eq_embed, eq_set_embed, autoplay_embed, autoplay_set_embed,
                                autoplay_off_embed, mode_247_embed, loop_embed, playlist_loaded_embed, HelpView)
from embeds.errors      import error_embed, warning_embed, success_embed, not_in_vc_embed, nothing_playing_embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Buttons
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── Custom emoji IDs ─────────────────────────────────────────────────────────
E_REWIND   = "<:rewind:1477351764830195813>"
E_PAUSE    = "<:pause:1477351853833322732>"
E_FORWARD  = "<:forward:1477352094456479968>"
E_STOP     = "<:stop:1477352287709040744>"
E_SHUFFLE  = "<:shuffle:1477353412206268508>"
E_LOOP     = "<:loop:1477353603982430248>"
E_QUEUE    = "<:queue:1477354162508529697>"
E_VOLDOWN  = "<:volumedown:1477357267547586600>"
E_VOLUP    = "<:volumeup:1477357858290143232>"
E_MUTE     = "<:mute:1477363235039477841>"

LOOP_LABELS = {"off": "loop: off", "single": "loop: one", "queue": "loop: all"}

class MusicView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=None)
        self.bot      = bot
        self.guild_id = guild_id
        # Set loop button label dynamically
        loop_mode = bot.get_cog("Music").loops.get(guild_id, "off") if bot.get_cog("Music") else "off"
        self._set_loop_label(loop_mode)

    def _set_loop_label(self, mode):
        for item in self.children:
            if hasattr(item, 'custom_id') and item.custom_id == "loop_btn":
                item.label = LOOP_LABELS[mode]

    def _cog(self): return self.bot.get_cog("Music")

    # ── ROW 0: rewind | pause | forward | stop ────────────────────────────
    @discord.ui.button(emoji=E_REWIND, style=discord.ButtonStyle.secondary, row=0)
    async def rewind_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Restart current song"""
        cog   = self._cog()
        track = cog.current_tracks.get(self.guild_id)
        vc    = interaction.guild.voice_client
        if not vc or not track:
            return await interaction.response.send_message("nothing playing!", ephemeral=True)
        await interaction.response.defer()
        vc.stop()  # play_next will handle loop=single if set, else re-queue
        # Force restart by re-playing current
        eq_filter = cog.eq_mode.get(self.guild_id, "")
        from config import EQ_PRESETS
        eq_filter = EQ_PRESETS.get(cog.get_eq(self.guild_id), "")
        try:
            from utils import YTDLSource
            new_track = await YTDLSource.from_url(
                track.webpage_url, loop=cog.bot.loop,
                stream=True, requester=track.requester, eq_filter=eq_filter)
            cog.current_tracks[self.guild_id] = new_track
            import time
            cog.track_start[self.guild_id] = time.time()
            vc.play(new_track, after=lambda e: asyncio.run_coroutine_threadsafe(
                cog.play_next(self.guild_id), cog.bot.loop))
            from embeds.now_playing import now_playing_embed
            msg = cog.np_messages.get(self.guild_id)
            if msg:
                await msg.edit(
                    embed=now_playing_embed(new_track, eq=cog.get_eq(self.guild_id),
                        autoplay=cog.autoplay.get(self.guild_id),
                        volume=cog.volumes.get(self.guild_id, 0.5), bot=cog.bot),
                    view=MusicView(cog.bot, self.guild_id))
        except Exception as e:
            await interaction.followup.send(f"restart failed: {e}", ephemeral=True)

    @discord.ui.button(emoji=E_PAUSE, style=discord.ButtonStyle.primary, row=0)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc    = interaction.guild.voice_client
        track = self._cog().current_tracks.get(self.guild_id)
        title = track.title if track else None
        if not vc: return await interaction.response.send_message("not in vc!", ephemeral=True)
        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message(embed=resume_embed(title), ephemeral=True)
        elif vc.is_playing():
            vc.pause()
            await interaction.response.send_message(embed=pause_embed(title), ephemeral=True)
        else:
            await interaction.response.send_message("nothing playing!", ephemeral=True)

    @discord.ui.button(emoji=E_FORWARD, style=discord.ButtonStyle.secondary, row=0)
    async def skip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc    = interaction.guild.voice_client
        track = self._cog().current_tracks.get(self.guild_id)
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message(
                embed=skip_embed(track.title if track else None), ephemeral=True)
        else:
            await interaction.response.send_message("nothing to skip!", ephemeral=True)

    @discord.ui.button(emoji=E_STOP, style=discord.ButtonStyle.danger, row=0)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self._cog()
        if cog.mode_247.get(self.guild_id):
            return await interaction.response.send_message("24/7 mode on — use `db 247` first!", ephemeral=True)
        vc = interaction.guild.voice_client
        if vc:
            cog.queues[self.guild_id]         = []
            cog.current_tracks[self.guild_id] = None
            cog.autoplay[self.guild_id]       = None
            await vc.disconnect()
            await interaction.response.send_message(embed=leave_embed(), ephemeral=True)
        else:
            await interaction.response.send_message("not even here!", ephemeral=True)

    # ── ROW 1: shuffle | loop | queue | vol- | vol+ ───────────────────────
    @discord.ui.button(emoji=E_SHUFFLE, style=discord.ButtonStyle.secondary, row=1)
    async def shuffle_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self._cog()
        q   = cog.queues.get(self.guild_id, [])
        if not q: return await interaction.response.send_message("queue empty!", ephemeral=True)
        random.shuffle(q)
        await interaction.response.send_message(embed=shuffle_embed(len(q)), ephemeral=True)

    @discord.ui.button(emoji=E_LOOP, label="loop: off", style=discord.ButtonStyle.secondary, row=1, custom_id="loop_btn")
    async def loop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog   = self._cog()
        modes = ["off", "single", "queue"]
        cur   = cog.loops.get(self.guild_id, "off")
        nxt   = modes[(modes.index(cur) + 1) % len(modes)]
        cog.loops[self.guild_id] = nxt
        button.label = LOOP_LABELS[nxt]
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=loop_embed(nxt), ephemeral=True)

    @discord.ui.button(emoji=E_QUEUE, style=discord.ButtonStyle.secondary, row=1)
    async def queue_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog   = self._cog()
        embed = queue_embed(
            cog.queues.get(self.guild_id, []),
            cog.current_tracks.get(self.guild_id),
            autoplay=cog.autoplay.get(self.guild_id)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(emoji=E_VOLDOWN, style=discord.ButtonStyle.secondary, row=1)
    async def vol_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc  = interaction.guild.voice_client
        cog = self._cog()
        if vc and vc.source:
            v = max(0.0, vc.source.volume - 0.1)
            vc.source.volume = v
            cog.volumes[self.guild_id] = v
            await interaction.response.defer()
            await cog._update_np_volume(self.guild_id, v)
        else:
            await interaction.response.send_message("nothing playing!", ephemeral=True)

    @discord.ui.button(emoji=E_VOLUP, style=discord.ButtonStyle.secondary, row=1)
    async def vol_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc  = interaction.guild.voice_client
        cog = self._cog()
        if vc and vc.source:
            v = min(1.0, vc.source.volume + 0.1)
            vc.source.volume = v
            cog.volumes[self.guild_id] = v
            await interaction.response.defer()
            await cog._update_np_volume(self.guild_id, v)
        else:
            await interaction.response.send_message("nothing playing!", ephemeral=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Music Cog
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot            = bot
        self.queues         = {}
        self.current_tracks = {}
        self.loops          = {}
        self.text_channels  = {}
        self.eq_mode        = {}
        self.autoplay       = {}
        self.mode_247       = {}
        self.track_start    = {}
        self.np_messages    = {}
        self._play_locks    = {}
        self.volumes        = {}   # guild_id: float 0.0-1.0
        self.progress_task.start()
        self.watchdog_task.start()

    @commands.command(name="mmh")
    async def mmh(self, ctx):
        """music module help"""
        await ctx.send(embed=help_embed(), view=HelpView())

    def cog_unload(self):
        self.progress_task.cancel()
        self.watchdog_task.cancel()

    def get_queue(self, gid):  return self.queues.setdefault(gid, [])
    def get_eq(self, gid):     return self.eq_mode.get(gid, "off")
    def get_lock(self, gid):
        if gid not in self._play_locks:
            self._play_locks[gid] = asyncio.Lock()
        return self._play_locks[gid]

    @tasks.loop(seconds=20)
    async def progress_task(self):
        for gid, msg in list(self.np_messages.items()):
            try:
                track = self.current_tracks.get(gid)
                start = self.track_start.get(gid)
                guild = self.bot.get_guild(gid)
                if not track or not start or not guild: continue
                vc = guild.voice_client
                if not vc or not vc.is_playing(): continue
                elapsed = int(time.time() - start)
                embed   = now_playing_embed(track, elapsed=elapsed,
                            eq=self.get_eq(gid), autoplay=self.autoplay.get(gid))
                await msg.edit(embed=embed, view=MusicView(self.bot, gid))
            except discord.NotFound:
                self.np_messages.pop(gid, None)
            except discord.HTTPException:
                pass
            except Exception:
                pass

    @tasks.loop(seconds=30)
    async def watchdog_task(self):
        for gid, enabled in list(self.mode_247.items()):
            if not enabled: continue
            try:
                channel = self.text_channels.get(gid)
                if not channel: continue
                vc = channel.guild.voice_client
                if not vc or not vc.is_connected():
                    for vchan in channel.guild.voice_channels:
                        if len([m for m in vchan.members if not m.bot]) > 0:
                            await vchan.connect()
                            await channel.send(embed=success_embed("reconnected! 24/7 mode alive ♾️"))
                            break
            except Exception:
                pass

    @progress_task.before_loop
    async def _before_progress(self): await self.bot.wait_until_ready()

    @watchdog_task.before_loop
    async def _before_watchdog(self): await self.bot.wait_until_ready()

    async def _update_np_volume(self, guild_id: int, volume: float):
        """Refresh np message with updated volume bar."""
        msg   = self.np_messages.get(guild_id)
        track = self.current_tracks.get(guild_id)
        if not msg or not track: return
        try:
            import time
            elapsed = int(time.time() - self.track_start.get(guild_id, time.time()))
            embed   = now_playing_embed(track, elapsed=elapsed,
                        eq=self.get_eq(guild_id), autoplay=self.autoplay.get(guild_id),
                        volume=volume, bot=self.bot)
            await msg.edit(embed=embed, view=MusicView(self.bot, guild_id))
        except Exception:
            pass

    async def play_next(self, guild_id: int):
        async with self.get_lock(guild_id):
            channel   = self.text_channels.get(guild_id)
            if not channel: return
            queue     = self.get_queue(guild_id)
            loop_mode = self.loops.get(guild_id, "off")
            cur       = self.current_tracks.get(guild_id)
            eq        = self.get_eq(guild_id)
            eq_filter = EQ_PRESETS.get(eq, "")
            ap        = self.autoplay.get(guild_id)
            track     = None

            if loop_mode == "single" and cur:
                try:
                    track = await YTDLSource.from_url(
                        cur.webpage_url, loop=self.bot.loop,
                        stream=True, requester=cur.requester, eq_filter=eq_filter)
                except Exception as e:
                    await channel.send(embed=warning_embed(f"loop failed, skipping: `{e}`"))
                    loop_mode = "off"

            if track is None and queue:
                next_item = queue.pop(0)
                try:
                    track = next_item if isinstance(next_item, YTDLSource) else \
                            await YTDLSource.from_entry(next_item, loop=self.bot.loop, eq_filter=eq_filter)
                except Exception as e:
                    await channel.send(embed=warning_embed(f"skipping broken track: `{e}`"))
                    asyncio.create_task(self.play_next(guild_id))
                    return
                if loop_mode == "queue" and cur:
                    try:
                        recycled = await YTDLSource.from_url(
                            cur.webpage_url, loop=self.bot.loop,
                            stream=True, requester=cur.requester, eq_filter=eq_filter)
                        queue.append(recycled)
                    except Exception:
                        pass

            if track is None and ap and ap in AUTOPLAY_GENRES:
                query = random.choice(AUTOPLAY_GENRES[ap])
                try:
                    track = await YTDLSource.from_url(
                        query, loop=self.bot.loop, stream=True,
                        requester=cur.requester if cur else None, eq_filter=eq_filter)
                    await channel.send(embed=discord.Embed(
                        description=f"✨ queue empty! autoplaying **{ap}** 🎲", color=ACCENT_COLOR))
                except Exception:
                    pass

            if track is None:
                self.current_tracks[guild_id] = None
                # Remove buttons from last np message
                msg = self.np_messages.pop(guild_id, None)
                if msg:
                    try:
                        await msg.edit(view=None)
                    except Exception:
                        pass
                await channel.send(embed=queue_finished_embed())
                return

            guild = channel.guild
            vc    = guild.voice_client
            if not vc or not vc.is_connected():
                member = guild.get_member(track.requester.id) if track.requester else None
                if member and member.voice and member.voice.channel:
                    try:
                        vc = await member.voice.channel.connect()
                    except Exception as e:
                        await channel.send(embed=error_embed(f"couldn't reconnect: `{e}`"))
                        return
                else:
                    await channel.send(embed=error_embed("lost VC! join a channel and `db play` again."))
                    return

            self.current_tracks[guild_id] = track
            self.track_start[guild_id]    = time.time()

            vc.play(track, after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(guild_id), self.bot.loop))

            try:
                msg = await channel.send(
                    embed=now_playing_embed(track, eq=eq, autoplay=ap, volume=self.volumes.get(guild_id, 0.5), bot=self.bot),
                    view=MusicView(self.bot, guild_id))
                self.np_messages[guild_id] = msg
            except Exception:
                pass

    # ── Commands ─────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="play", aliases=["p"], description="🎵 Play a song or YouTube playlist")
    async def play(self, ctx, *, query: str):
        await ctx.defer()
        if not ctx.author.voice:
            return await ctx.send(embed=not_in_vc_embed())

        self.text_channels[ctx.guild.id] = ctx.channel
        eq_filter = EQ_PRESETS.get(self.get_eq(ctx.guild.id), "")

        vc = ctx.guild.voice_client
        if not vc:
            try: vc = await ctx.author.voice.channel.connect()
            except Exception as e:
                return await ctx.send(embed=error_embed(f"couldn't connect: `{e}`"))
        elif ctx.author.voice.channel != vc.channel:
            await vc.move_to(ctx.author.voice.channel)

        is_playlist = "list=" in query or "playlist" in query.lower()

        if is_playlist:
            try:
                entries = await YTDLSource.from_playlist(query, loop=self.bot.loop, requester=ctx.author)
            except Exception as e:
                return await ctx.send(embed=error_embed(f"playlist load failed: `{e}`"))
            if not entries:
                return await ctx.send(embed=error_embed("couldn't load that playlist!"))

            queue = self.get_queue(ctx.guild.id)
            try:
                track = await YTDLSource.from_entry(entries[0], loop=self.bot.loop, eq_filter=eq_filter)
            except Exception as e:
                return await ctx.send(embed=error_embed(f"first track failed: `{e}`"))

            queue.extend(entries[1:])
            await ctx.send(embed=playlist_loaded_embed(len(entries)))

            vc = ctx.guild.voice_client
            if not vc or not vc.is_connected():
                vc = await ctx.author.voice.channel.connect()

            if vc.is_playing() or vc.is_paused():
                queue.insert(0, track)
            else:
                self.current_tracks[ctx.guild.id] = track
                self.track_start[ctx.guild.id]    = time.time()
                vc.play(track, after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx.guild.id), self.bot.loop))
                msg = await ctx.send(
                    embed=now_playing_embed(track, eq=self.get_eq(ctx.guild.id), volume=self.volumes.get(ctx.guild.id, 0.5), bot=self.bot),
                    view=MusicView(self.bot, ctx.guild.id))
                self.np_messages[ctx.guild.id] = msg
            return

        try:
            track = await YTDLSource.from_url(query, loop=self.bot.loop,
                        stream=True, requester=ctx.author, eq_filter=eq_filter)
        except Exception as e:
            err = "FFmpeg not found! Run: `winget install ffmpeg`" if "ffmpeg" in str(e).lower() else str(e)
            return await ctx.send(embed=error_embed(err))

        vc = ctx.guild.voice_client
        if not vc or not vc.is_connected():
            try: vc = await ctx.author.voice.channel.connect()
            except Exception as e:
                return await ctx.send(embed=error_embed(f"lost vc: `{e}`"))

        queue = self.get_queue(ctx.guild.id)
        if vc.is_playing() or vc.is_paused():
            queue.append(track)
            await ctx.send(embed=added_to_queue_embed(track, len(queue)))
        else:
            self.current_tracks[ctx.guild.id] = track
            self.track_start[ctx.guild.id]    = time.time()
            vc.play(track, after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(ctx.guild.id), self.bot.loop))
            msg = await ctx.send(
                embed=now_playing_embed(track, eq=self.get_eq(ctx.guild.id), volume=self.volumes.get(ctx.guild.id, 0.5), bot=self.bot),
                view=MusicView(self.bot, ctx.guild.id))
            self.np_messages[ctx.guild.id] = msg

    @commands.hybrid_command(name="skip", aliases=["s"], description="⏭️ Skip current song")
    async def skip(self, ctx):
        await ctx.defer()
        vc    = ctx.guild.voice_client
        track = self.current_tracks.get(ctx.guild.id)
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await ctx.send(embed=skip_embed(track.title if track else None))
        else:
            await ctx.send(embed=nothing_playing_embed())

    @commands.hybrid_command(name="pause", description="⏸️ Pause")
    async def pause(self, ctx):
        await ctx.defer()
        vc    = ctx.guild.voice_client
        track = self.current_tracks.get(ctx.guild.id)
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send(embed=pause_embed(track.title if track else None))
        else:
            await ctx.send(embed=nothing_playing_embed())

    @commands.hybrid_command(name="resume", aliases=["r"], description="▶️ Resume")
    async def resume(self, ctx):
        await ctx.defer()
        vc    = ctx.guild.voice_client
        track = self.current_tracks.get(ctx.guild.id)
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send(embed=resume_embed(track.title if track else None))
        else:
            await ctx.send(embed=warning_embed("nothing is paused!"))

    @commands.hybrid_command(name="queue", aliases=["q"], description="📜 View queue")
    async def queue_cmd(self, ctx, page: int = 1):
        await ctx.defer()
        await ctx.send(embed=queue_embed(
            self.get_queue(ctx.guild.id),
            self.current_tracks.get(ctx.guild.id),
            page, autoplay=self.autoplay.get(ctx.guild.id)))

    @commands.hybrid_command(name="nowplaying", aliases=["np"], description="🎵 Now playing")
    async def nowplaying(self, ctx):
        await ctx.defer()
        track = self.current_tracks.get(ctx.guild.id)
        if not track: return await ctx.send(embed=nothing_playing_embed())
        elapsed = int(time.time() - self.track_start.get(ctx.guild.id, time.time()))
        msg = await ctx.send(
            embed=now_playing_embed(track, elapsed=elapsed,
                eq=self.get_eq(ctx.guild.id), autoplay=self.autoplay.get(ctx.guild.id),
                volume=self.volumes.get(ctx.guild.id, 0.5), bot=self.bot),
            view=MusicView(self.bot, ctx.guild.id))
        self.np_messages[ctx.guild.id] = msg

    @commands.hybrid_command(name="loop", description="🔁 Toggle loop: off / single / queue")
    async def loop(self, ctx, mode: str = None):
        await ctx.defer()
        current = self.loops.get(ctx.guild.id, "off")
        if mode is None:
            modes = ["off", "single", "queue"]
            mode  = modes[(modes.index(current) + 1) % len(modes)]
        elif mode not in ["off", "single", "queue"]:
            return await ctx.send(embed=error_embed("choose: `off` · `single` · `queue`"))
        self.loops[ctx.guild.id] = mode
        await ctx.send(embed=loop_embed(mode))

    @commands.hybrid_command(name="shuffle", description="🔀 Shuffle queue")
    async def shuffle(self, ctx):
        await ctx.defer()
        q = self.get_queue(ctx.guild.id)
        if not q: return await ctx.send(embed=warning_embed("queue is empty!"))
        random.shuffle(q)
        await ctx.send(embed=shuffle_embed(len(q)))

    @commands.hybrid_command(name="volume", aliases=["vol", "v"], description="🔊 Set volume 0-100")
    async def volume(self, ctx, volume: int):
        await ctx.defer()
        vc = ctx.guild.voice_client
        if not vc or not vc.source: return await ctx.send(embed=nothing_playing_embed())
        if not 0 <= volume <= 100:
            return await ctx.send(embed=error_embed("volume must be 0–100!"))
        v = volume / 100
        vc.source.volume = v
        self.volumes[ctx.guild.id] = v
        await self._update_np_volume(ctx.guild.id, v)
        bar = "●" * (volume // 10) + "○" * (10 - volume // 10)
        await ctx.send(embed=discord.Embed(
            description=f"🔊 **{f'{volume}%'}** `{bar}`", color=ACCENT_COLOR))

    @commands.hybrid_command(name="eq", aliases=["equalizer"], description="🎛️ Set EQ preset")
    async def eq_cmd(self, ctx, preset: str = None):
        await ctx.defer()
        if preset is None:
            return await ctx.send(embed=eq_embed(self.get_eq(ctx.guild.id)))
        if preset not in EQ_PRESETS:
            return await ctx.send(embed=error_embed(f"unknown preset! use `db eq` to see all options."))
        self.eq_mode[ctx.guild.id] = preset
        await ctx.send(embed=eq_set_embed(preset))

    @commands.hybrid_command(name="autoplay", aliases=["ap"], description="✨ Auto-play a genre when queue ends")
    async def autoplay_cmd(self, ctx, genre: str = None):
        await ctx.defer()
        genres_str = "  ".join(f"`{g}`" for g in AUTOPLAY_GENRES)
        if genre is None:
            cur = self.autoplay.get(ctx.guild.id)
            if cur:
                self.autoplay[ctx.guild.id] = None
                return await ctx.send(embed=autoplay_off_embed(cur))
            return await ctx.send(embed=autoplay_embed(genres_str))
        if genre not in AUTOPLAY_GENRES:
            return await ctx.send(embed=error_embed(f"unknown genre!\navailable: {genres_str}"))
        self.autoplay[ctx.guild.id] = genre
        colors = {"phonk": 0xff4444, "romantic": 0xff69b4, "lofi": 0x7ec8e3, "sad": 0x6c7a89}
        await ctx.send(embed=autoplay_set_embed(genre, colors.get(genre, ACCENT_COLOR)))

    @commands.hybrid_command(name="247", description="♾️ Toggle 24/7 mode")
    async def mode_247_cmd(self, ctx):
        await ctx.defer()
        cur = self.mode_247.get(ctx.guild.id, False)
        self.mode_247[ctx.guild.id]      = not cur
        self.text_channels[ctx.guild.id] = ctx.channel
        await ctx.send(embed=mode_247_embed(not cur))

    @commands.hybrid_command(name="remove", description="🗑️ Remove track from queue")
    async def remove(self, ctx, position: int):
        await ctx.defer()
        q = self.get_queue(ctx.guild.id)
        if not q or not 1 <= position <= len(q):
            return await ctx.send(embed=error_embed("invalid position!"))
        removed = q.pop(position - 1)
        title   = removed.title if isinstance(removed, YTDLSource) else removed.get('title', 'Unknown')
        await ctx.send(embed=success_embed(f"removed **{title}** from queue!"))

    @commands.hybrid_command(name="clear", description="🧹 Clear the queue")
    async def clear(self, ctx):
        await ctx.defer()
        self.queues[ctx.guild.id] = []
        await ctx.send(embed=success_embed("queue cleared! fresh start 🌱"))

    @commands.hybrid_command(name="lyrics", description="📜 Get lyrics")
    async def lyrics(self, ctx, *, query: str = None):
        await ctx.defer()
        if not query:
            t = self.current_tracks.get(ctx.guild.id)
            if not t: return await ctx.send(embed=nothing_playing_embed())
            query = t.title
        text = await get_lyrics(query, GENIUS_TOKEN)
        await ctx.send(embed=discord.Embed(
            title=f"📜 {query}", description=text[:4000], color=NOW_PLAYING_COLOR))

    @commands.hybrid_command(name="leave", aliases=["dc"], description="👋 Disconnect")
    async def leave(self, ctx):
        await ctx.defer()
        if self.mode_247.get(ctx.guild.id):
            return await ctx.send(embed=warning_embed("24/7 mode on — use `db 247` to disable first 😤"))
        vc = ctx.guild.voice_client
        if vc:
            self.queues[ctx.guild.id]         = []
            self.current_tracks[ctx.guild.id] = None
            self.autoplay[ctx.guild.id]       = None
            await vc.disconnect()
            await ctx.send(embed=leave_embed())
        else:
            await ctx.send(embed=warning_embed("not in a vc!"))




async def setup(bot):
    await bot.add_cog(Music(bot))


