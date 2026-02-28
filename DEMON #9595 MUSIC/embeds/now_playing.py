import discord
from datetime import datetime
from config import NOW_PLAYING_COLOR

_N = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
_F = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
_T = str.maketrans(_N, _F)
def f(text: str) -> str:
    return str(text).translate(_T)

def _source(url: str) -> tuple:
    url = (url or "").lower()
    if "youtube" in url or "youtu.be" in url:
        return ("YouTube", "https://i.imgur.com/xzVHhFY.png")
    if "soundcloud" in url:
        return ("SoundCloud", "https://i.imgur.com/9TiGs1N.png")
    if "spotify" in url:
        return ("Spotify", "https://i.imgur.com/7eFVoGp.png")
    return ("Web", "")

def _short_title(title: str, max_len: int = 35) -> str:
    import re
    title = re.sub(r'\[.*?\]', '', title).strip()
    title = re.sub(r'\(?(official\s*(music\s*)?video|lyrics?|audio|hd|4k|slowed|reverb|ft\..*)\)?',
                   '', title, flags=re.IGNORECASE).strip()
    if " - " in title:
        title = title.split(" - ", 1)[-1].strip()
    if len(title) > max_len:
        title = title[:max_len - 1] + "…"
    return title

def _fmt(seconds):
    if not seconds: return "Live"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def _vol_display(volume: float) -> str:
    vol_pct = int(volume * 100)
    filled  = int(volume * 10)
    bar     = "●" * filled + "○" * (10 - filled)
    return f"`{bar}` `{f(str(vol_pct)+'%')}`"

def now_playing_embed(
    track,
    elapsed:  int            = 0,
    eq:       str            = "off",
    autoplay: str            = None,
    volume:   float          = 0.5,
    bot:      discord.Client = None,
) -> discord.Embed:

    duration    = track.duration or 0
    requester   = track.requester
    src_name, src_icon = _source(track.webpage_url)
    short_name  = _short_title(track.title)
    artist_name = track.uploader
    req_text    = requester.mention if requester else "✨ 𝒂𝒖𝒕𝒐𝒑𝒍𝒂𝒚"

    color = NOW_PLAYING_COLOR
    if   eq == "phonk"    or autoplay == "phonk":    color = 0xff4444
    elif eq == "lofi"     or autoplay == "lofi":     color = 0x7ec8e3
    elif eq == "nightcore":                           color = 0xc084fc
    elif eq == "vaporwave":                           color = 0x818cf8
    elif autoplay == "romantic":                      color = 0xff69b4
    elif autoplay == "sad":                           color = 0x6c7a89

    embed = discord.Embed(color=color)

    embed.set_author(
        name=f"𝒑𝒍𝒂𝒚𝒊𝒏𝒈 𝒇𝒓𝒐𝒎  {f(src_name)}",
        icon_url=src_icon if src_icon else discord.Embed.Empty
    )

    embed.title = "<:music:1477266378443722752>  𝒏𝒐𝒘 𝒑𝒍𝒂𝒚𝒊𝒏𝒈"

    embed.description = (
        f"> • [{f(short_name)}]({track.webpage_url})  —  **{f(artist_name)}**!\n"
        f"> • 𝒅𝒖𝒓𝒂𝒕𝒊𝒐𝒏 : `{_fmt(duration)}`\n"
        f"> • 𝒓𝒆𝒒𝒖𝒆𝒔𝒕𝒆𝒅 𝒃𝒚 : {req_text}\n"
        f"> • 𝒗𝒐𝒍𝒖𝒎𝒆 : {_vol_display(volume)}"
    )

    if track.thumbnail:
        embed.set_thumbnail(url=track.thumbnail)

    now        = datetime.now().strftime("%I:%M %p")
    bot_name   = bot.user.name if bot and bot.user else "Demon"
    bot_avatar = bot.user.display_avatar.url if bot and bot.user else discord.Embed.Empty
    embed.set_footer(
        text=f"{bot_name}  •  {f(now)}",
        icon_url=bot_avatar
    )

    return embed
