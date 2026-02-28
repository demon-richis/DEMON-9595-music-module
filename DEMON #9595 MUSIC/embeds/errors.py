import discord
from config import ERROR_COLOR, WARNING_COLOR, SUCCESS_COLOR

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  𝒇𝒂𝒏𝒄𝒚 font
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_N = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
_F = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
_T = str.maketrans(_N, _F)
def f(text: str) -> str:
    return str(text).translate(_T)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Error
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def error_embed(description: str, title: str = "❌  𝒆𝒓𝒓𝒐𝒓") -> discord.Embed:
    embed = discord.Embed(title=title, color=ERROR_COLOR)
    embed.description = f"> • {description}"
    embed.set_footer(text="𝒔𝒐𝒎𝒆𝒕𝒉𝒊𝒏𝒈 𝒘𝒆𝒏𝒕 𝒘𝒓𝒐𝒏𝒈 — 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏!")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Warning
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def warning_embed(description: str) -> discord.Embed:
    embed = discord.Embed(title="⚠️  𝒉𝒆𝒚!", color=WARNING_COLOR)
    embed.description = f"> • {description}"
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Success
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def success_embed(description: str) -> discord.Embed:
    embed = discord.Embed(title="✅  𝒅𝒐𝒏𝒆!", color=SUCCESS_COLOR)
    embed.description = f"> • {description}"
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Specific errors
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def not_in_vc_embed() -> discord.Embed:
    embed = discord.Embed(title="❌  𝒋𝒐𝒊𝒏 𝒂 𝒗𝒄 𝒇𝒊𝒓𝒔𝒕!", color=ERROR_COLOR)
    embed.description = "> • 𝒚𝒐𝒖'𝒓𝒆 𝒏𝒐𝒕 𝒊𝒏 𝒂 𝒗𝒐𝒊𝒄𝒆 𝒄𝒉𝒂𝒏𝒏𝒆𝒍!"
    embed.set_footer(text="𝒋𝒐𝒊𝒏 𝒐𝒏𝒆 𝒂𝒏𝒅 𝒕𝒓𝒚 𝒂𝒈𝒂𝒊𝒏.")
    return embed

def nothing_playing_embed() -> discord.Embed:
    embed = discord.Embed(title="⚠️  𝒏𝒐𝒕𝒉𝒊𝒏𝒈 𝒑𝒍𝒂𝒚𝒊𝒏𝒈!", color=WARNING_COLOR)
    embed.description = "> • 𝒖𝒔𝒆 `db play` 𝒕𝒐 𝒔𝒕𝒂𝒓𝒕 𝒔𝒐𝒎𝒆𝒕𝒉𝒊𝒏𝒈 🎶"
    return embed
