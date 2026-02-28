import discord
from config import ACCENT_COLOR, SUCCESS_COLOR, WARNING_COLOR, ERROR_COLOR

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  𝒇𝒂𝒏𝒄𝒚 font
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_N = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
_F = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
_T = str.maketrans(_N, _F)

def f(text: str) -> str:
    return str(text).translate(_T)

def _short(title: str, max_len: int = 35) -> str:
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
#  Skip
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def skip_embed(title: str = None) -> discord.Embed:
    short = f(_short(title)) if title else None
    embed = discord.Embed(
        title="⏭️  𝒔𝒌𝒊𝒑𝒑𝒆𝒅!",
        color=ACCENT_COLOR
    )
    embed.description = (
        f"> • 𝒕𝒓𝒂𝒄𝒌 : **{short}**\n" if short else ""
    ) + "> • 𝒍𝒐𝒂𝒅𝒊𝒏𝒈 𝒏𝒆𝒙𝒕 𝒕𝒓𝒂𝒄𝒌..."
    embed.set_footer(text="𝒏𝒐𝒕 𝒕𝒉𝒆 𝒗𝒊𝒃𝒆? 𝒇𝒂𝒊𝒓 𝒆𝒏𝒐𝒖𝒈𝒉.")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Pause
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def pause_embed(title: str = None) -> discord.Embed:
    short = f(_short(title)) if title else None
    embed = discord.Embed(
        title="⏸️  𝒑𝒂𝒖𝒔𝒆𝒅.",
        color=WARNING_COLOR
    )
    embed.description = (
        (f"> • 𝒕𝒓𝒂𝒄𝒌 : **{short}**\n" if short else "") +
        "> • 𝒖𝒔𝒆 `db resume` 𝒐𝒓 ▶️ 𝒕𝒐 𝒄𝒐𝒏𝒕𝒊𝒏𝒖𝒆"
    )
    embed.set_footer(text="𝒕𝒂𝒌𝒆 𝒚𝒐𝒖𝒓 𝒕𝒊𝒎𝒆.")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Resume
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def resume_embed(title: str = None) -> discord.Embed:
    short = f(_short(title)) if title else None
    embed = discord.Embed(
        title="▶️  𝒓𝒆𝒔𝒖𝒎𝒆𝒅!",
        color=SUCCESS_COLOR
    )
    embed.description = (
        (f"> • 𝒕𝒓𝒂𝒄𝒌 : **{short}**\n" if short else "") +
        "> • 𝒗𝒊𝒃𝒆𝒔 𝒓𝒆𝒔𝒕𝒐𝒓𝒆𝒅 🎶"
    )
    embed.set_footer(text="𝒍𝒆𝒕'𝒔 𝒈𝒐𝒐𝒐!")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Leave
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def leave_embed() -> discord.Embed:
    embed = discord.Embed(
        title="👋  𝒅𝒊𝒔𝒄𝒐𝒏𝒏𝒆𝒄𝒕𝒆𝒅.",
        color=ACCENT_COLOR
    )
    embed.description = (
        "> • 𝒍𝒆𝒇𝒕 𝒕𝒉𝒆 𝒗𝒐𝒊𝒄𝒆 𝒄𝒉𝒂𝒏𝒏𝒆𝒍!\n"
        "> • 𝒄𝒂𝒍𝒍 𝒎𝒆 𝒃𝒂𝒄𝒌 𝒘𝒊𝒕𝒉 `db play` 🎵"
    )
    embed.set_footer(text="𝒊𝒕 𝒘𝒂𝒔 𝒂 𝒗𝒊𝒃𝒆. 𝒔𝒆𝒆 𝒚𝒂!")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Shuffle
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def shuffle_embed(queue_size: int) -> discord.Embed:
    embed = discord.Embed(
        title="🔀  𝒔𝒉𝒖𝒇𝒇𝒍𝒆𝒅!",
        color=ACCENT_COLOR
    )
    embed.description = (
        f"> • **{f(str(queue_size))} 𝒔𝒐𝒏𝒈𝒔** 𝒓𝒆𝒂𝒓𝒓𝒂𝒏𝒈𝒆𝒅 🎲\n"
        "> • 𝒄𝒉𝒂𝒐𝒔 𝒎𝒐𝒅𝒆 𝒂𝒄𝒕𝒊𝒗𝒂𝒕𝒆𝒅!"
    )
    embed.set_footer(text="𝒔𝒖𝒓𝒑𝒓𝒊𝒔𝒆 𝒚𝒐𝒖𝒓𝒔𝒆𝒍𝒇.")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Queue Finished
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def queue_finished_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🎵  𝒒𝒖𝒆𝒖𝒆 𝒇𝒊𝒏𝒊𝒔𝒉𝒆𝒅!",
        color=ACCENT_COLOR
    )
    embed.description = (
        "> • 𝒏𝒐𝒕𝒉𝒊𝒏𝒈 𝒍𝒆𝒇𝒕 𝒕𝒐 𝒑𝒍𝒂𝒚!\n"
        "> • 𝒂𝒅𝒅 𝒎𝒐𝒓𝒆 𝒘𝒊𝒕𝒉 `db play` 🎶\n"
        "> • 𝒐𝒓 𝒖𝒔𝒆 `db autoplay phonk` 𝒇𝒐𝒓 𝒊𝒏𝒇𝒊𝒏𝒊𝒕𝒆 𝒗𝒊𝒃𝒆𝒔 ✨"
    )
    embed.set_footer(text="𝒕𝒉𝒂𝒏𝒌𝒔 𝒇𝒐𝒓 𝒗𝒊𝒃𝒊𝒏𝒈 𝒘𝒊𝒕𝒉 𝑫𝒆𝒎𝒐𝒏 𝒕𝒐𝒅𝒂𝒚 ♪")
    return embed
