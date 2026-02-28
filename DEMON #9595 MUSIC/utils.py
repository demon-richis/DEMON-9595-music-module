import discord
import yt_dlp
import asyncio
from config import (
    YDL_OPTIONS, YDL_OPTIONS_SINGLE, EMBED_COLOR, ACCENT_COLOR,
    NOW_PLAYING_COLOR, FFMPEG_EXECUTABLE, EQ_PRESETS
)

ytdl        = yt_dlp.YoutubeDL(YDL_OPTIONS)
ytdl_single = yt_dlp.YoutubeDL(YDL_OPTIONS_SINGLE)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Audio Source
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data        = data
        self.title       = data.get('title', 'Unknown')
        self.webpage_url = data.get('webpage_url') or data.get('original_url') or data.get('url')
        self.url         = data.get('url')
        self.thumbnail   = data.get('thumbnail')
        self.duration    = data.get('duration')
        self.uploader    = data.get('uploader', 'Unknown Artist')
        self.requester   = data.get('requester')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True, requester=None, eq_filter=""):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl_single.extract_info(url, download=False))
        if not data:
            raise Exception("No results found.")
        if 'entries' in data:
            data = data['entries'][0]
        if not data:
            raise Exception("No results found.")
        data['requester'] = requester

        options = "-vn -bufsize 65536"
        if eq_filter:
            options += f" -af \"{eq_filter}\""

        source = discord.FFmpegPCMAudio(
            data['url'],
            executable=FFMPEG_EXECUTABLE,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 200M -analyzeduration 0",
            options=options
        )
        return cls(source, data=data)

    @classmethod
    async def from_playlist(cls, url, *, loop=None, requester=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if not data:
            return []
        entries = data.get('entries', [data])
        tracks = []
        for entry in entries:
            if entry:
                entry['requester'] = requester
                tracks.append(entry)
        return tracks

    @classmethod
    async def from_entry(cls, entry, *, loop=None, eq_filter=""):
        loop  = loop or asyncio.get_event_loop()
        url   = entry.get('webpage_url') or entry.get('url')
        return await cls.from_url(url, loop=loop, stream=True,
                                  requester=entry.get('requester'), eq_filter=eq_filter)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def format_duration(seconds):
    if not seconds:
        return "Live"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def build_bar(current, total, length=15):
    if not total:
        return "─" * length
    filled = int((current / total) * length)
    return "[" + "▓" * filled + "░" * (length - filled) + "]"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Embeds
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_embed(title=None, description=None, color=EMBED_COLOR,
                 thumbnail=None, footer=None, fields=None, image=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if thumbnail: embed.set_thumbnail(url=thumbnail)
    if image:     embed.set_image(url=image)
    if footer:    embed.set_footer(text=footer)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed

def create_aesthetic_embed(*args, **kwargs):
    return create_embed(*args, **kwargs)

def create_now_playing_embed(track, elapsed=0, eq="off", autoplay=None):
    duration = track.duration or 0
    bar      = build_bar(elapsed, duration)
    color    = NOW_PLAYING_COLOR
    if eq == "phonk" or autoplay == "phonk":   color = 0xff4444
    elif eq == "lofi" or autoplay == "lofi":   color = 0x7ec8e3
    elif autoplay == "romantic":                color = 0xff69b4

    footer_parts = ["♪ high quality audio"]
    if eq and eq != "off": footer_parts.append(f"EQ: {eq}")
    if autoplay:           footer_parts.append(f"autoplay: {autoplay}")

    embed = discord.Embed(
        title="✦ Now Playing",
        description=(
            f"### [{track.title}]({track.webpage_url})\n"
            f"by **{track.uploader}**\n\n"
            f"`{format_duration(elapsed)}` {bar} `{format_duration(duration)}`"
        ),
        color=color,
    )
    if track.thumbnail: embed.set_thumbnail(url=track.thumbnail)
    embed.add_field(name="⌚ Duration",     value=f"`{format_duration(duration)}`", inline=True)
    embed.add_field(name="👤 Requested by", value=track.requester.mention if track.requester else "autoplay", inline=True)
    embed.set_footer(text="  ·  ".join(footer_parts))
    return embed

def create_added_to_queue_embed(track, position):
    embed = discord.Embed(
        title="✦ Added to Queue",
        description=f"### [{track.title}]({track.webpage_url})\nby **{track.uploader}**",
        color=ACCENT_COLOR,
    )
    if track.thumbnail: embed.set_thumbnail(url=track.thumbnail)
    embed.add_field(name="⌚ Duration",     value=f"`{format_duration(track.duration)}`", inline=True)
    embed.add_field(name="📍 Position",     value=f"`#{position}`",                       inline=True)
    embed.add_field(name="👤 Requested by", value=track.requester.mention if track.requester else "?", inline=True)
    embed.set_footer(text="♪ sit tight, your song is coming up!")
    return embed

def create_queue_embed(queue, current=None, page=1, autoplay=None):
    per_page = 10
    start    = (page - 1) * per_page
    end      = start + per_page
    pages    = max(1, -(-len(queue) // per_page))
    lines    = []

    if current:
        lines.append(f"**▶  [{current.title}]({current.webpage_url})**\n`{format_duration(current.duration)}` — *now playing*\n")

    if not queue:
        ap_hint = f"\n✨ autoplay **{autoplay}** is on!" if autoplay else ""
        lines.append(f"*queue is empty — add songs with* `!play`{ap_hint}")
    else:
        for i, t in enumerate(queue[start:end], start + 1):
            if isinstance(t, YTDLSource):
                title, url, dur = t.title, t.webpage_url, t.duration
            else:
                title = t.get('title', 'Unknown')
                url   = t.get('webpage_url') or '#'
                dur   = t.get('duration')
            lines.append(f"`{i:02d}.` [{title}]({url}) · `{format_duration(dur)}`")

    total_dur = sum((t.duration if isinstance(t, YTDLSource) else t.get('duration') or 0) for t in queue)
    embed = discord.Embed(title="✦ Queue", description="\n".join(lines), color=ACCENT_COLOR)
    footer = f"page {page}/{pages}  ·  {len(queue)} songs  ·  {format_duration(total_dur)} total"
    if autoplay: footer += f"  ·  autoplay: {autoplay} ✨"
    embed.set_footer(text=footer)
    return embed

async def get_lyrics(song_name, genius_token=""):
    if genius_token:
        try:
            import lyricsgenius
            loop   = asyncio.get_event_loop()
            genius = lyricsgenius.Genius(genius_token, verbose=False, remove_section_headers=True)
            song   = await loop.run_in_executor(None, lambda: genius.search_song(song_name))
            if song and song.lyrics:
                return f"**{song.title}** by *{song.artist}*\n\n{song.lyrics[:3800]}"
        except Exception:
            pass
    return (
        f"Searched for: **{song_name}**\n\n"
        "To enable real lyrics, add `GENIUS_TOKEN` to `.env` and run:\n"
        "`pip install lyricsgenius`"
    )
