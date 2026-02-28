import discord
from config import ACCENT_COLOR, SUCCESS_COLOR, WARNING_COLOR, NOW_PLAYING_COLOR, EQ_DESCRIPTIONS, AUTOPLAY_GENRES, EQ_PRESETS

_N = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
_F = "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁𝒂𝒃𝒄𝒅𝒆𝒇𝒈𝒉𝒊𝒋𝒌𝒍𝒎𝒏𝒐𝒑𝒒𝒓𝒔𝒕𝒖𝒗𝒘𝒙𝒚𝒛𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
_T = str.maketrans(_N, _F)
def f(text: str) -> str:
    return str(text).translate(_T)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Category data
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CATEGORIES = {
    "playback": {
        "label":       "Playback",
        "description": "play, skip, pause, resume, volume, leave",
        "embed_title": "𝒑𝒍𝒂𝒚𝒃𝒂𝒄𝒌 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔",
        "fields": [
            ("play",       "`db play <song/url>` — play a song or YouTube playlist"),
            ("skip",       "`db skip` — skip current song"),
            ("pause",      "`db pause` — pause playback"),
            ("resume",     "`db resume` — resume playback"),
            ("volume",     "`db volume <0-100>` — set volume"),
            ("nowplaying", "`db np` — show now playing card"),
            ("leave",      "`db leave` — disconnect from vc"),
        ]
    },
    "queue": {
        "label":       "Queue",
        "description": "queue, shuffle, remove, clear",
        "embed_title": "𝒒𝒖𝒆𝒖𝒆 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔",
        "fields": [
            ("queue",   "`db queue [page]` — view the queue"),
            ("shuffle", "`db shuffle` — shuffle the queue"),
            ("remove",  "`db remove <position>` — remove a track"),
            ("clear",   "`db clear` — clear the entire queue"),
            ("loop",    "`db loop` — toggle: off / single / queue"),
        ]
    },
    "features": {
        "label":       "Features",
        "description": "autoplay, eq, 247, lyrics",
        "embed_title": "𝒇𝒆𝒂𝒕𝒖𝒓𝒆𝒔",
        "fields": [
            ("autoplay", "`db autoplay <genre>` — auto-play when queue ends\ngenres: " + "  ".join(f"`{g}`" for g in AUTOPLAY_GENRES)),
            ("eq",       "`db eq <preset>` — audio equalizer\npresets: " + "  ".join(f"`{k}`" for k in EQ_PRESETS)),
            ("247",      "`db 247` — stay in vc forever, auto-reconnects"),
            ("lyrics",   "`db lyrics [query]` — get song lyrics"),
        ]
    },
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Category embed builder
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def category_embed(category_key: str) -> discord.Embed:
    cat = CATEGORIES[category_key]
    embed = discord.Embed(
        title=f"𝒎𝒖𝒔𝒊𝒄 𝒎𝒐𝒅𝒖𝒍𝒆  —  {cat['embed_title']}",
        color=NOW_PLAYING_COLOR
    )
    lines = []
    for name, desc in cat["fields"]:
        lines.append(f"> • {desc}")
    embed.description = "\n".join(lines)
    embed.set_footer(text="𝒅𝒃 <𝒄𝒐𝒎𝒎𝒂𝒏𝒅>  •  𝒖𝒔𝒆 𝒅𝒓𝒐𝒑𝒅𝒐𝒘𝒏 𝒕𝒐 𝒔𝒘𝒊𝒕𝒄𝒉 𝒄𝒂𝒕𝒆𝒈𝒐𝒓𝒚")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Main help embed (shown first)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="𝒎𝒖𝒔𝒊𝒄 𝒎𝒐𝒅𝒖𝒍𝒆",
        description=(
            "> • 𝒑𝒓𝒆𝒇𝒊𝒙 : `db`\n"
            "> • 𝒔𝒍𝒂𝒔𝒉 𝒄𝒐𝒎𝒎𝒂𝒏𝒅𝒔 𝒂𝒍𝒔𝒐 𝒘𝒐𝒓𝒌 ✨\n"
            ">\n"
            "> 𝒔𝒆𝒍𝒆𝒄𝒕 𝒂 𝒄𝒂𝒕𝒆𝒈𝒐𝒓𝒚 𝒇𝒓𝒐𝒎 𝒕𝒉𝒆 𝒅𝒓𝒐𝒑𝒅𝒐𝒘𝒏 𝒃𝒆𝒍𝒐𝒘"
        ),
        color=NOW_PLAYING_COLOR
    )
    embed.set_footer(text="𝒅𝒃 𝒎𝒎𝒉  •  𝒎𝒖𝒔𝒊𝒄 𝒎𝒐𝒅𝒖𝒍𝒆 𝒉𝒆𝒍𝒑")
    return embed

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Dropdown View
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class HelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=cat["label"],
                value=key,
                description=cat["description"],
            )
            for key, cat in CATEGORIES.items()
        ]
        super().__init__(
            placeholder="select a category...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        embed = category_embed(self.values[0])
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(HelpSelect())

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Other info embeds
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def eq_embed(current: str) -> discord.Embed:
    presets = "\n".join(f"> • `{k}` — {v}" for k, v in EQ_DESCRIPTIONS.items())
    embed = discord.Embed(title="🎛️  𝒆𝒒𝒖𝒂𝒍𝒊𝒛𝒆𝒓", color=ACCENT_COLOR)
    embed.description = f"> • 𝒄𝒖𝒓𝒓𝒆𝒏𝒕 : `{current}`\n>\n{presets}\n>\n> • 𝒖𝒔𝒂𝒈𝒆 : `db eq bassboost`"
    embed.set_footer(text="𝒔𝒌𝒊𝒑 𝒕𝒐 𝒉𝒆𝒂𝒓 𝒏𝒆𝒘 𝑬𝑸 𝒏𝒐𝒘!")
    return embed

def eq_set_embed(preset: str) -> discord.Embed:
    embed = discord.Embed(title="🎛️  𝒆𝒒 𝒖𝒑𝒅𝒂𝒕𝒆𝒅!", color=SUCCESS_COLOR)
    embed.description = f"> • 𝒑𝒓𝒆𝒔𝒆𝒕 : `{preset}` — **{EQ_DESCRIPTIONS[preset]}**\n> • 𝒔𝒌𝒊𝒑 𝒕𝒐 𝒉𝒆𝒂𝒓 𝒊𝒕 𝒏𝒐𝒘! ⚡"
    return embed

def autoplay_embed(genres_str: str) -> discord.Embed:
    embed = discord.Embed(title="✨  𝒂𝒖𝒕𝒐𝒑𝒍𝒂𝒚", color=ACCENT_COLOR)
    embed.description = f"> • 𝒈𝒆𝒏𝒓𝒆𝒔 : {genres_str}\n> • 𝒖𝒔𝒂𝒈𝒆 : `db autoplay phonk`\n> • 𝒕𝒖𝒓𝒏 𝒐𝒇𝒇 : `db autoplay` 𝒂𝒈𝒂𝒊𝒏"
    embed.set_footer(text="𝒂𝒖𝒕𝒐-𝒑𝒍𝒂𝒚𝒔 𝒘𝒉𝒆𝒏 𝒒𝒖𝒆𝒖𝒆 𝒓𝒖𝒏𝒔 𝒐𝒖𝒕!")
    return embed

def autoplay_set_embed(genre: str, color: int) -> discord.Embed:
    embed = discord.Embed(title=f"✨  𝒂𝒖𝒕𝒐𝒑𝒍𝒂𝒚 : {genre}", color=color)
    embed.description = f"> • 𝒊'𝒍𝒍 𝒂𝒖𝒕𝒐-𝒑𝒍𝒂𝒚 **{genre}** 𝒗𝒊𝒃𝒆𝒔 🎲\n> • 𝒕𝒖𝒓𝒏 𝒐𝒇𝒇 : `db autoplay`"
    embed.set_footer(text="𝒊𝒏𝒇𝒊𝒏𝒊𝒕𝒆 𝒗𝒊𝒃𝒆𝒔 𝒖𝒏𝒍𝒐𝒄𝒌𝒆𝒅!")
    return embed

def autoplay_off_embed(was: str) -> discord.Embed:
    embed = discord.Embed(title="✨  𝒂𝒖𝒕𝒐𝒑𝒍𝒂𝒚 𝒐𝒇𝒇", color=ACCENT_COLOR)
    embed.description = f"> • 𝒘𝒂𝒔 : **{was}**\n> • 𝒅𝒊𝒔𝒂𝒃𝒍𝒆𝒅 ✅"
    return embed

def loop_embed(mode: str) -> discord.Embed:
    data = {
        "off":    ("🔁  𝒍𝒐𝒐𝒑 𝒐𝒇𝒇",    ACCENT_COLOR,  "𝒍𝒐𝒐𝒑 𝒅𝒊𝒔𝒂𝒃𝒍𝒆𝒅.",                  "𝒃𝒂𝒄𝒌 𝒕𝒐 𝒏𝒐𝒓𝒎𝒂𝒍."),
        "single": ("🔂  𝒍𝒐𝒐𝒑 𝒔𝒊𝒏𝒈𝒍𝒆", 0xc084fc,      "𝒍𝒐𝒐𝒑𝒊𝒏𝒈 𝒕𝒉𝒊𝒔 𝒔𝒐𝒏𝒈 𝒇𝒐𝒓𝒆𝒗𝒆𝒓. 😤", "𝒃𝒐𝒍𝒅 𝒄𝒉𝒐𝒊𝒄𝒆."),
        "queue":  ("🔁  𝒍𝒐𝒐𝒑 𝒒𝒖𝒆𝒖𝒆",  SUCCESS_COLOR, "𝒆𝒏𝒕𝒊𝒓𝒆 𝒒𝒖𝒆𝒖𝒆 𝒍𝒐𝒐𝒑𝒊𝒏𝒈. 🌀",        "𝒗𝒊𝒃𝒊𝒏𝒈 𝒆𝒕𝒆𝒓𝒏𝒂𝒍𝒍𝒚."),
    }
    title, color, desc, footer = data[mode]
    embed = discord.Embed(title=title, color=color)
    embed.description = f"> • {desc}"
    embed.set_footer(text=footer)
    return embed

def mode_247_embed(enabled: bool) -> discord.Embed:
    if enabled:
        embed = discord.Embed(title="♾️  𝟐𝟒/𝟕 𝒎𝒐𝒅𝒆 𝒐𝒏", color=SUCCESS_COLOR)
        embed.description = "> • 𝒊'𝒎 𝒏𝒐𝒕 𝒍𝒆𝒂𝒗𝒊𝒏𝒈. 𝒆𝒗𝒆𝒓. 😤\n> • 𝒂𝒖𝒕𝒐-𝒓𝒆𝒄𝒐𝒏𝒏𝒆𝒄𝒕𝒔 𝒊𝒇 𝒌𝒊𝒄𝒌𝒆𝒅!"
        embed.set_footer(text="𝒆𝒕𝒆𝒓𝒏𝒂𝒍 𝒗𝒊𝒃𝒆 𝒎𝒐𝒅𝒆 𝒂𝒄𝒕𝒊𝒗𝒂𝒕𝒆𝒅.")
    else:
        embed = discord.Embed(title="♾️  𝟐𝟒/𝟕 𝒎𝒐𝒅𝒆 𝒐𝒇𝒇", color=ACCENT_COLOR)
        embed.description = "> • 𝒊 𝒄𝒂𝒏 𝒓𝒆𝒔𝒕 𝒏𝒐𝒘 😌"
    return embed

def playlist_loaded_embed(count: int) -> discord.Embed:
    embed = discord.Embed(title="📋  𝒑𝒍𝒂𝒚𝒍𝒊𝒔𝒕 𝒍𝒐𝒂𝒅𝒆𝒅!", color=SUCCESS_COLOR)
    embed.description = f"> • **{f(str(count))} 𝒔𝒐𝒏𝒈𝒔** 𝒒𝒖𝒆𝒖𝒆𝒅 ✨\n> • 𝒇𝒊𝒓𝒔𝒕 𝒕𝒓𝒂𝒄𝒌 𝒑𝒍𝒂𝒚𝒊𝒏𝒈 𝒏𝒐𝒘!"
    embed.set_footer(text="𝒔𝒊𝒕 𝒃𝒂𝒄𝒌 𝒂𝒏𝒅 𝒗𝒊𝒃𝒆 🎵")
    return embed
