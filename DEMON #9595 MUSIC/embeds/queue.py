import discord
from config import ACCENT_COLOR

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  𝒇𝒂𝒏𝒄𝒚 font
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_N = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
_F = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
_T = str.maketrans(_N, _F)

def f(text: str) -> str:
    return str(text).translate(_T)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _fmt(seconds):
    if not seconds: return "Live"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def _short(title: str, max_len: int = 38) -> str:
    import re
    title = re.sub(r'\[.*?\]', '', title).strip()
    title = re.sub(r'\(?(official\s*(music\s*)?video|lyrics?|audio|hd|4k|slowed|reverb|ft\..*)\)?',
                   '', title, flags=re.IGNORECASE).strip()
    if " - " in title:
        title = title.split(" - ", 1)[-1].strip()
    if len(title) > max_len:
        title = title[:max_len - 1] + "…"
    return title

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Added to Queue Embed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def added_to_queue_embed(track, position: int) -> discord.Embed:
    from utils import YTDLSource
    short = _short(track.title)
    embed = discord.Embed(
        title="📋  𝒂𝒅𝒅𝒆𝒅 𝒕𝒐 𝒒𝒖𝒆𝒖𝒆",
        color=ACCENT_COLOR
    )
    embed.description = (
        f"> • [{f(short)}]({track.webpage_url})  —  **{f(track.uploader)}**!\n"
        f"> • 𝒅𝒖𝒓𝒂𝒕𝒊𝒐𝒏 : `{_fmt(track.duration)}`\n"
        f"> • 𝒑𝒐𝒔𝒊𝒕𝒊𝒐𝒏 : `#{position}`\n"
        f"> • 𝒓𝒆𝒒𝒖𝒆𝒔𝒕𝒆𝒅 𝒃𝒚 : {track.requester.mention if track.requester else '✨ 𝒂𝒖𝒕𝒐𝒑𝒍𝒂𝒚'}"
    )
    if track.thumbnail:
        embed.set_thumbnail(url=track.thumbnail)
    embed.set_footer(text="𝒔𝒊𝒕 𝒕𝒊𝒈𝒉𝒕, 𝒚𝒐𝒖𝒓 𝒔𝒐𝒏𝒈 𝒊𝒔 𝒄𝒐𝒎𝒊𝒏𝒈 𝒖𝒑!")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Queue Embed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def queue_embed(queue, current=None, page: int = 1, autoplay: str = None) -> discord.Embed:
    from utils import YTDLSource

    per_page = 8
    start    = (page - 1) * per_page
    end      = start + per_page
    pages    = max(1, -(-len(queue) // per_page))

    lines = []

    # Now playing section
    if current:
        short = _short(current.title)
        lines.append(f"▶  **[{f(short)}]({current.webpage_url})**  —  {f(current.uploader)}")
        lines.append(f"╰ `{_fmt(current.duration)}`  •  𝒏𝒐𝒘 𝒑𝒍𝒂𝒚𝒊𝒏𝒈\n")

    # Queue list
    if not queue:
        ap_hint = f"\n✨ 𝒂𝒖𝒕𝒐𝒑𝒍𝒂𝒚 **{autoplay}** 𝒊𝒔 𝒐𝒏!" if autoplay else ""
        lines.append(f"*𝒒𝒖𝒆𝒖𝒆 𝒊𝒔 𝒆𝒎𝒑𝒕𝒚 — 𝒖𝒔𝒆* `!play` *𝒕𝒐 𝒂𝒅𝒅 𝒔𝒐𝒏𝒈𝒔*{ap_hint}")
    else:
        for i, t in enumerate(queue[start:end], start + 1):
            if isinstance(t, YTDLSource):
                title, url, dur = t.title, t.webpage_url, t.duration
            else:
                title = t.get('title', 'Unknown')
                url   = t.get('webpage_url') or '#'
                dur   = t.get('duration')
            short = _short(title)
            lines.append(f"`{f(str(i)):>2}.`  [{f(short)}]({url})  `{_fmt(dur)}`")

    # Total duration
    total_dur = sum(
        (t.duration if isinstance(t, YTDLSource) else t.get('duration') or 0)
        for t in queue
    )

    embed = discord.Embed(
        title="📋  𝒒𝒖𝒆𝒖𝒆",
        description="\n".join(lines),
        color=ACCENT_COLOR
    )

    # Stats row
    stats = f"𝒑𝒂𝒈𝒆 {page}/{pages}  •  {len(queue)} 𝒔𝒐𝒏𝒈𝒔  •  {_fmt(total_dur)} 𝒕𝒐𝒕𝒂𝒍"
    if autoplay:
        stats += f"  •  ✨ 𝒂𝒖𝒕𝒐𝒑𝒍𝒂𝒚: {autoplay}"
    embed.set_footer(text=stats)

    return embed
