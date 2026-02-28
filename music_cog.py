import discord
from discord.ext import commands, tasks
import asyncio
import random
import time
import traceback
from utils import (
    YTDLSource, create_embed, create_now_playing_embed,
    create_added_to_queue_embed, create_queue_embed,
    format_duration, get_lyrics, build_bar
)
from config import (
    ACCENT_COLOR, ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR,
    NOW_PLAYING_COLOR, EQ_PRESETS, EQ_DESCRIPTIONS,
    AUTOPLAY_GENRES, GENIUS_TOKEN
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Playful responses
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKIP_MSGS    = ["🚀 yeeted!", "⏭️ not the vibe.", "💨 gone. next!", "🫡 skipped."]
SHUFFLE_MSGS = ["🔀 shaken, not stirred.", "🎲 chaos mode: on.", "✨ shuffled!"]
PAUSE_MSGS   = ["⏸️ paused.", "🧊 frozen.", "😴 nap time."]
RESUME_MSGS  = ["▶️ back at it!", "🔥 let's go!", "🎶 vibes restored."]
LEAVE_MSGS   = ["👋 peace out!", "🚪 bouncing.", "🎤 mic dropped. bye!"]
LOOP_OFF     = ["🔁 loop off.", "✂️ no more looping!"]
LOOP_SINGLE  = ["🔂 looping forever.", "♾️ this song owns you now."]
LOOP_QUEUE   = ["🔁 queue looping.", "🌀 vibing eternally."]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Buttons
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class MusicView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=None)
        self.bot      = bot
        self.guild_id = guild_id

    def _cog(self): return self.bot.get_cog("Music")

    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.primary, row=0)
    async def pause_resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if not vc: return await interaction.response.send_message("not in vc!", ephemeral=True)
        if vc.is_paused():
            vc.resume()
            await interaction.response.send_message(random.choice(RESUME_MSGS), ephemeral=True)
        elif vc.is_playing():
            vc.pause()
            await interaction.response.send_message(random.choice(PAUSE_MSGS), ephemeral=True)
        else:
            await interaction.response.send_message("nothing playing!", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, row=0)
    async def skip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message(random.choice(SKIP_MSGS), ephemeral=True)
        else:
            await interaction.response.send_message("nothing to skip!", ephemeral=True)

    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary, row=0)
    async def shuffle_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self._cog()
        q   = cog.queues.get(self.guild_id, [])
        if not q: return await interaction.response.send_message("queue empty!", ephemeral=True)
        random.shuffle(q)
        await interaction.response.send_message(random.choice(SHUFFLE_MSGS), ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=0)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = self._cog()
        if cog.mode_247.get(self.guild_id):
            return await interaction.response.send_message("24/7 mode on — use `!247` first!", ephemeral=True)
        vc = interaction.guild.voice_client
        if vc:
            cog.queues[self.guild_id]         = []
            cog.current_tracks[self.guild_id] = None
            cog.autoplay[self.guild_id]       = None
            await vc.disconnect()
            await interaction.response.send_message(random.choice(LEAVE_MSGS), ephemeral=True)
        else:
            await interaction.response.send_message("not even here!", ephemeral=True)

    @discord.ui.button(label="📜 Queue", style=discord.ButtonStyle.secondary, row=1)
    async def queue_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog   = self._cog()
        embed = create_queue_embed(
            cog.queues.get(self.guild_id, []),
            cog.current_tracks.get(self.guild_id),
            autoplay=cog.autoplay.get(self.guild_id)
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🔁 Loop", style=discord.ButtonStyle.secondary, row=1)
    async def loop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog     = self._cog()
        modes   = ["off", "single", "queue"]
        cur     = cog.loops.get(self.guild_id, "off")
        nxt     = modes[(modes.index(cur) + 1) % len(modes)]
        cog.loops[self.guild_id] = nxt
        msgs = {"off": LOOP_OFF, "single": LOOP_SINGLE, "queue": LOOP_QUEUE}
        await interaction.response.send_message(random.choice(msgs[nxt]), ephemeral=True)

    @discord.ui.button(label="🔉 -10%", style=discord.ButtonStyle.secondary, row=1)
    async def vol_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.source:
            v   = max(0.0, vc.source.volume - 0.1)
            vc.source.volume = v
            bar = "█" * int(v * 10) + "░" * (10 - int(v * 10))
            await interaction.response.send_message(f"🔉 `{int(v*100)}%` `{bar}`", ephemeral=True)
        else:
            await interaction.response.send_message("nothing playing!", ephemeral=True)

    @discord.ui.button(label="🔊 +10%", style=discord.ButtonStyle.secondary, row=1)
    async def vol_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.source:
            v   = min(1.0, vc.source.volume + 0.1)
            vc.source.volume = v
            bar = "█" * int(v * 10) + "░" * (10 - int(v * 10))
            await interaction.response.send_message(f"🔊 `{int(v*100)}%` `{bar}`", ephemeral=True)
        else:
            await interaction.response.send_message("nothing playing!", ephemeral=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Music Cog
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot            = bot
        self.queues         = {}   # guild_id: list
        self.current_tracks = {}   # guild_id: YTDLSource
        self.loops          = {}   # guild_id: "off"|"single"|"queue"
        self.text_channels  = {}   # guild_id: TextChannel
        self.eq_mode        = {}   # guild_id: str
        self.autoplay       = {}   # guild_id: str|None
        self.mode_247       = {}   # guild_id: bool
        self.track_start    = {}   # guild_id: float
        self.np_messages    = {}   # guild_id: Message
        self._play_locks    = {}   # guild_id: Lock  ← prevents race conditions
        self.progress_task.start()
        self.watchdog_task.start()

    def cog_unload(self):
        self.progress_task.cancel()
        self.watchdog_task.cancel()

    def get_queue(self, gid):   return self.queues.setdefault(gid, [])
    def get_eq(self, gid):      return self.eq_mode.get(gid, "off")
    def get_lock(self, gid):
        if gid not in self._play_locks:
            self._play_locks[gid] = asyncio.Lock()
        return self._play_locks[gid]

    # ── Background: live progress bar ────────────────────────────────────────
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
                embed   = create_now_playing_embed(track, elapsed=elapsed,
                            eq=self.get_eq(gid), autoplay=self.autoplay.get(gid))
                await msg.edit(embed=embed, view=MusicView(self.bot, gid))
            except discord.NotFound:
                self.np_messages.pop(gid, None)
            except discord.HTTPException:
                pass  # rate limit — skip this update
            except Exception:
                pass

    # ── Background: 24/7 watchdog ────────────────────────────────────────────
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
                            await channel.send(embed=create_embed(
                                description="🔄 reconnected! 24/7 mode alive ♾️",
                                color=SUCCESS_COLOR
                            ))
                            break
            except Exception:
                pass

    @progress_task.before_loop
    async def _before_progress(self): await self.bot.wait_until_ready()

    @watchdog_task.before_loop
    async def _before_watchdog(self): await self.bot.wait_until_ready()

    # ── Core: play_next ───────────────────────────────────────────────────────
    async def play_next(self, guild_id: int):
        """Called after each track ends. Handles loop, queue, autoplay."""
        async with self.get_lock(guild_id):
            channel   = self.text_channels.get(guild_id)
            if not channel: return

            queue     = self.get_queue(guild_id)
            loop_mode = self.loops.get(guild_id, "off")
            cur       = self.current_tracks.get(guild_id)
            eq        = self.get_eq(guild_id)
            eq_filter = EQ_PRESETS.get(eq, "")
            ap        = self.autoplay.get(guild_id)

            # ── Determine next track ─────────────────────────────────────
            track = None

            if loop_mode == "single" and cur:
                # Re-fetch stream URL (old one expires)
                try:
                    track = await YTDLSource.from_url(
                        cur.webpage_url, loop=self.bot.loop,
                        stream=True, requester=cur.requester, eq_filter=eq_filter
                    )
                except Exception as e:
                    await channel.send(embed=create_embed(
                        description=f"⚠️ loop failed, skipping: `{e}`", color=WARNING_COLOR))
                    loop_mode = "off"

            if track is None and queue:
                next_item = queue.pop(0)
                try:
                    if isinstance(next_item, YTDLSource):
                        track = next_item
                    else:
                        track = await YTDLSource.from_entry(
                            next_item, loop=self.bot.loop, eq_filter=eq_filter)
                except Exception as e:
                    await channel.send(embed=create_embed(
                        description=f"⚠️ skipping broken track: `{e}`", color=WARNING_COLOR))
                    # Recurse to try next in queue
                    asyncio.create_task(self.play_next(guild_id))
                    return

                # Queue loop: put current track back at end
                if loop_mode == "queue" and cur:
                    try:
                        recycled = await YTDLSource.from_url(
                            cur.webpage_url, loop=self.bot.loop,
                            stream=True, requester=cur.requester, eq_filter=eq_filter)
                        queue.append(recycled)
                    except Exception:
                        pass

            if track is None and ap and ap in AUTOPLAY_GENRES:
                # Autoplay
                query = random.choice(AUTOPLAY_GENRES[ap])
                try:
                    track = await YTDLSource.from_url(
                        query, loop=self.bot.loop, stream=True,
                        requester=cur.requester if cur else None, eq_filter=eq_filter)
                    await channel.send(embed=create_embed(
                        description=f"✨ queue empty! autoplaying **{ap}** 🎲", color=ACCENT_COLOR))
                except Exception:
                    pass

            if track is None:
                # Nothing left
                self.current_tracks[guild_id] = None
                await channel.send(embed=create_embed(
                    title="✦ Queue Finished",
                    description="nothing left! use `!play` or `!autoplay phonk` 🎲",
                    color=ACCENT_COLOR,
                    footer="thanks for vibing with Demon ♪"
                ))
                return

            # ── Reconnect VC if dropped ──────────────────────────────────
            guild = channel.guild
            vc    = guild.voice_client
            if not vc or not vc.is_connected():
                requester = track.requester
                member    = guild.get_member(requester.id) if requester else None
                if member and member.voice and member.voice.channel:
                    try:
                        vc = await member.voice.channel.connect()
                    except Exception as e:
                        await channel.send(embed=create_embed(
                            description=f"❌ couldn't reconnect: `{e}`", color=ERROR_COLOR))
                        return
                else:
                    await channel.send(embed=create_embed(
                        description="❌ lost VC! join a channel and `!play` again.", color=ERROR_COLOR))
                    return

            # ── Play ─────────────────────────────────────────────────────
            self.current_tracks[guild_id] = track
            self.track_start[guild_id]    = time.time()

            def after_play(err):
                if err:
                    print(f"[play_next] Player error: {err}")
                asyncio.run_coroutine_threadsafe(
                    self.play_next(guild_id), self.bot.loop)

            vc.play(track, after=after_play)

            embed = create_now_playing_embed(track, eq=eq, autoplay=ap)
            view  = MusicView(self.bot, guild_id)
            try:
                msg = await channel.send(embed=embed, view=view)
                self.np_messages[guild_id] = msg
            except Exception:
                pass

    # ── Commands ─────────────────────────────────────────────────────────────

    @commands.hybrid_command(name="play", aliases=["p"], description="🎵 Play a song or YouTube playlist")
    async def play(self, ctx, *, query: str):
        await ctx.defer()

        if not ctx.author.voice:
            return await ctx.send(embed=create_embed(
                title="❌ Not in a Voice Channel",
                description="join a vc first!", color=ERROR_COLOR))

        self.text_channels[ctx.guild.id] = ctx.channel
        eq_filter = EQ_PRESETS.get(self.get_eq(ctx.guild.id), "")

        # Connect / move
        vc = ctx.guild.voice_client
        if not vc:
            try:
                vc = await ctx.author.voice.channel.connect()
            except Exception as e:
                return await ctx.send(embed=create_embed(
                    description=f"❌ couldn't connect: `{e}`", color=ERROR_COLOR))
        elif ctx.author.voice.channel != vc.channel:
            await vc.move_to(ctx.author.voice.channel)

        is_playlist = "list=" in query or "playlist" in query.lower()

        # ── Playlist ─────────────────────────────────────────────────────
        if is_playlist:
            try:
                entries = await YTDLSource.from_playlist(
                    query, loop=self.bot.loop, requester=ctx.author)
            except Exception as e:
                return await ctx.send(embed=create_embed(
                    description=f"❌ playlist load failed: `{e}`", color=ERROR_COLOR))

            if not entries:
                return await ctx.send(embed=create_embed(
                    description="❌ couldn't load that playlist!", color=ERROR_COLOR))

            queue = self.get_queue(ctx.guild.id)
            first = entries[0]
            rest  = entries[1:]

            try:
                track = await YTDLSource.from_entry(
                    first, loop=self.bot.loop, eq_filter=eq_filter)
            except Exception as e:
                return await ctx.send(embed=create_embed(
                    description=f"❌ first track failed: `{e}`", color=ERROR_COLOR))

            queue.extend(rest)

            await ctx.send(embed=create_embed(
                title="📋 Playlist Loaded!",
                description=f"**{len(entries)} songs** added ✨\nfirst track playing now!",
                color=SUCCESS_COLOR,
                footer=f"{len(rest)} more in queue"
            ))

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
                embed = create_now_playing_embed(track, eq=self.get_eq(ctx.guild.id))
                view  = MusicView(self.bot, ctx.guild.id)
                msg   = await ctx.send(embed=embed, view=view)
                self.np_messages[ctx.guild.id] = msg
            return

        # ── Single track ─────────────────────────────────────────────────
        try:
            track = await YTDLSource.from_url(
                query, loop=self.bot.loop, stream=True,
                requester=ctx.author, eq_filter=eq_filter)
        except Exception as e:
            err = "FFmpeg not found! Run: `winget install ffmpeg`" if "ffmpeg" in str(e).lower() else str(e)
            return await ctx.send(embed=create_embed(
                title="❌ Error", description=f"`{err}`", color=ERROR_COLOR))

        # Re-check vc after async fetch
        vc = ctx.guild.voice_client
        if not vc or not vc.is_connected():
            try:
                vc = await ctx.author.voice.channel.connect()
            except Exception as e:
                return await ctx.send(embed=create_embed(
                    description=f"❌ lost vc: `{e}`", color=ERROR_COLOR))

        queue = self.get_queue(ctx.guild.id)
        if vc.is_playing() or vc.is_paused():
            queue.append(track)
            await ctx.send(embed=create_added_to_queue_embed(track, len(queue)))
        else:
            self.current_tracks[ctx.guild.id] = track
            self.track_start[ctx.guild.id]    = time.time()
            vc.play(track, after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(ctx.guild.id), self.bot.loop))
            embed = create_now_playing_embed(track, eq=self.get_eq(ctx.guild.id))
            view  = MusicView(self.bot, ctx.guild.id)
            msg   = await ctx.send(embed=embed, view=view)
            self.np_messages[ctx.guild.id] = msg

    @commands.hybrid_command(name="skip", aliases=["s"], description="⏭️ Skip current song")
    async def skip(self, ctx):
        await ctx.defer()
        vc = ctx.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await ctx.send(embed=create_embed(description=random.choice(SKIP_MSGS), color=ACCENT_COLOR))
        else:
            await ctx.send(embed=create_embed(description="nothing to skip!", color=WARNING_COLOR))

    @commands.hybrid_command(name="pause", description="⏸️ Pause")
    async def pause(self, ctx):
        await ctx.defer()
        vc = ctx.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send(embed=create_embed(description=random.choice(PAUSE_MSGS), color=ACCENT_COLOR))
        else:
            await ctx.send(embed=create_embed(description="nothing to pause!", color=WARNING_COLOR))

    @commands.hybrid_command(name="resume", aliases=["r"], description="▶️ Resume")
    async def resume(self, ctx):
        await ctx.defer()
        vc = ctx.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send(embed=create_embed(description=random.choice(RESUME_MSGS), color=SUCCESS_COLOR))
        else:
            await ctx.send(embed=create_embed(description="nothing paused!", color=WARNING_COLOR))

    @commands.hybrid_command(name="queue", aliases=["q"], description="📜 View queue")
    async def queue_cmd(self, ctx, page: int = 1):
        await ctx.defer()
        embed = create_queue_embed(
            self.get_queue(ctx.guild.id),
            self.current_tracks.get(ctx.guild.id),
            page,
            autoplay=self.autoplay.get(ctx.guild.id)
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="nowplaying", aliases=["np"], description="🎵 Now playing")
    async def nowplaying(self, ctx):
        await ctx.defer()
        track = self.current_tracks.get(ctx.guild.id)
        if not track:
            return await ctx.send(embed=create_embed(
                description="nothing playing! use `!play` 🎶", color=WARNING_COLOR))
        elapsed = int(time.time() - self.track_start.get(ctx.guild.id, time.time()))
        embed   = create_now_playing_embed(track, elapsed=elapsed,
                    eq=self.get_eq(ctx.guild.id), autoplay=self.autoplay.get(ctx.guild.id))
        view    = MusicView(self.bot, ctx.guild.id)
        msg     = await ctx.send(embed=embed, view=view)
        self.np_messages[ctx.guild.id] = msg

    @commands.hybrid_command(name="loop", description="🔁 Toggle loop: off / single / queue")
    async def loop(self, ctx, mode: str = None):
        await ctx.defer()
        current = self.loops.get(ctx.guild.id, "off")
        if mode is None:
            modes = ["off", "single", "queue"]
            mode  = modes[(modes.index(current) + 1) % len(modes)]
        elif mode not in ["off", "single", "queue"]:
            return await ctx.send(embed=create_embed(
                description="choose: `off` · `single` · `queue`", color=ERROR_COLOR))
        self.loops[ctx.guild.id] = mode
        msgs = {"off": LOOP_OFF, "single": LOOP_SINGLE, "queue": LOOP_QUEUE}
        await ctx.send(embed=create_embed(description=random.choice(msgs[mode]), color=ACCENT_COLOR))

    @commands.hybrid_command(name="shuffle", description="🔀 Shuffle queue")
    async def shuffle(self, ctx):
        await ctx.defer()
        q = self.get_queue(ctx.guild.id)
        if not q:
            return await ctx.send(embed=create_embed(description="queue is empty!", color=WARNING_COLOR))
        random.shuffle(q)
        await ctx.send(embed=create_embed(description=random.choice(SHUFFLE_MSGS), color=ACCENT_COLOR))

    @commands.hybrid_command(name="volume", aliases=["vol", "v"], description="🔊 Set volume 0-100")
    async def volume(self, ctx, volume: int):
        await ctx.defer()
        vc = ctx.guild.voice_client
        if not vc or not vc.source:
            return await ctx.send(embed=create_embed(description="nothing playing!", color=WARNING_COLOR))
        if not 0 <= volume <= 100:
            return await ctx.send(embed=create_embed(description="volume must be 0–100!", color=ERROR_COLOR))
        vc.source.volume = volume / 100
        bar = "█" * (volume // 10) + "░" * (10 - volume // 10)
        await ctx.send(embed=create_embed(
            description=f"🔊 **{volume}%** `{bar}`", color=ACCENT_COLOR))

    @commands.hybrid_command(name="eq", aliases=["equalizer"], description="🎛️ Set EQ preset")
    async def eq_cmd(self, ctx, preset: str = None):
        await ctx.defer()
        presets = "\n".join(f"`{k}` — {v}" for k, v in EQ_DESCRIPTIONS.items())
        if preset is None:
            return await ctx.send(embed=create_embed(
                title="🎛️ Equalizer",
                description=f"**current:** `{self.get_eq(ctx.guild.id)}`\n\n{presets}\n\nusage: `!eq bassboost`",
                color=ACCENT_COLOR))
        if preset not in EQ_PRESETS:
            return await ctx.send(embed=create_embed(
                description=f"unknown preset!\n{presets}", color=ERROR_COLOR))
        self.eq_mode[ctx.guild.id] = preset
        await ctx.send(embed=create_embed(
            title="🎛️ EQ Set",
            description=f"**{EQ_DESCRIPTIONS[preset]}** — applies to next song!\nskip now to hear it.",
            color=SUCCESS_COLOR))

    @commands.hybrid_command(name="autoplay", aliases=["ap"], description="✨ Auto-play a genre when queue ends")
    async def autoplay_cmd(self, ctx, genre: str = None):
        await ctx.defer()
        genres = "  ".join(f"`{g}`" for g in AUTOPLAY_GENRES)
        if genre is None:
            cur = self.autoplay.get(ctx.guild.id)
            if cur:
                self.autoplay[ctx.guild.id] = None
                return await ctx.send(embed=create_embed(
                    description=f"✨ autoplay off! was: **{cur}**", color=ACCENT_COLOR))
            return await ctx.send(embed=create_embed(
                title="✨ Autoplay", description=f"{genres}\nusage: `!autoplay phonk`", color=ACCENT_COLOR))
        if genre not in AUTOPLAY_GENRES:
            return await ctx.send(embed=create_embed(
                description=f"unknown genre!\n{genres}", color=ERROR_COLOR))
        self.autoplay[ctx.guild.id] = genre
        colors = {"phonk": 0xff4444, "romantic": 0xff69b4, "lofi": 0x7ec8e3, "sad": 0x6c7a89}
        await ctx.send(embed=create_embed(
            title=f"✨ Autoplay: {genre}",
            description=f"auto-playing **{genre}** when queue ends 🎲\nturn off: `!autoplay`",
            color=colors.get(genre, ACCENT_COLOR)))

    @commands.hybrid_command(name="247", description="♾️ Toggle 24/7 mode")
    async def mode_247_cmd(self, ctx):
        await ctx.defer()
        cur = self.mode_247.get(ctx.guild.id, False)
        self.mode_247[ctx.guild.id]      = not cur
        self.text_channels[ctx.guild.id] = ctx.channel
        if not cur:
            await ctx.send(embed=create_embed(
                title="♾️ 24/7 ON",
                description="not leaving. ever. 😤\nauto-reconnects if kicked!",
                color=SUCCESS_COLOR))
        else:
            await ctx.send(embed=create_embed(
                description="♾️ 24/7 off — i can rest now 😌", color=ACCENT_COLOR))

    @commands.hybrid_command(name="remove", description="🗑️ Remove track from queue")
    async def remove(self, ctx, position: int):
        await ctx.defer()
        q = self.get_queue(ctx.guild.id)
        if not q or not 1 <= position <= len(q):
            return await ctx.send(embed=create_embed(description="invalid position!", color=ERROR_COLOR))
        removed = q.pop(position - 1)
        title   = removed.title if isinstance(removed, YTDLSource) else removed.get('title', 'Unknown')
        await ctx.send(embed=create_embed(description=f"🗑️ removed **{title}**", color=ACCENT_COLOR))

    @commands.hybrid_command(name="clear", description="🧹 Clear the queue")
    async def clear(self, ctx):
        await ctx.defer()
        self.queues[ctx.guild.id] = []
        await ctx.send(embed=create_embed(description="🧹 queue cleared! fresh start 🌱", color=SUCCESS_COLOR))

    @commands.hybrid_command(name="lyrics", description="📜 Get lyrics")
    async def lyrics(self, ctx, *, query: str = None):
        await ctx.defer()
        if not query:
            t = self.current_tracks.get(ctx.guild.id)
            if not t:
                return await ctx.send(embed=create_embed(
                    description="nothing playing and no query!", color=WARNING_COLOR))
            query = t.title
        text  = await get_lyrics(query, GENIUS_TOKEN)
        await ctx.send(embed=create_embed(
            title=f"📜 {query}", description=text[:4000], color=NOW_PLAYING_COLOR))

    @commands.hybrid_command(name="leave", aliases=["dc"], description="👋 Disconnect")
    async def leave(self, ctx):
        await ctx.defer()
        if self.mode_247.get(ctx.guild.id):
            return await ctx.send(embed=create_embed(
                description="24/7 mode on — use `!247` to disable first 😤", color=WARNING_COLOR))
        vc = ctx.guild.voice_client
        if vc:
            self.queues[ctx.guild.id]         = []
            self.current_tracks[ctx.guild.id] = None
            self.autoplay[ctx.guild.id]       = None
            await vc.disconnect()
            await ctx.send(embed=create_embed(description=random.choice(LEAVE_MSGS), color=ACCENT_COLOR))
        else:
            await ctx.send(embed=create_embed(description="not in a vc!", color=WARNING_COLOR))

    @commands.hybrid_command(name="help", description="📖 All commands")
    async def help_cmd(self, ctx):
        await ctx.defer()
        embed = discord.Embed(
            title="✦ Demon — Commands",
            description="use `!` prefix or `/` slash — both work ✨",
            color=NOW_PLAYING_COLOR
        )
        embed.add_field(name="▶ Playback",  value="`play` `skip` `pause` `resume` `volume` `nowplaying` `leave`", inline=False)
        embed.add_field(name="📋 Playlist", value="`!play <YouTube playlist URL>` — loads up to 50 songs!", inline=False)
        embed.add_field(name="📜 Queue",    value="`queue` `shuffle` `remove` `clear`", inline=False)
        embed.add_field(name="🔁 Loop",     value="`loop` — cycles: `off` → `single` → `queue`", inline=False)
        embed.add_field(name="✨ Autoplay", value="`autoplay <genre>` — " + "  ".join(f"`{g}`" for g in AUTOPLAY_GENRES), inline=False)
        embed.add_field(name="🎛️ EQ",       value="`eq <preset>` — " + "  ".join(f"`{k}`" for k in EQ_PRESETS), inline=False)
        embed.add_field(name="♾️ 24/7",     value="`247` — stays in vc forever, auto-reconnects!", inline=False)
        embed.add_field(name="🎤 Extras",   value="`lyrics` `ping`", inline=False)
        embed.set_footer(text="♪ Demon  ·  use buttons on now-playing card for quick controls")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Music(bot))
