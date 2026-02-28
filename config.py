import os
from dotenv import load_dotenv
load_dotenv()

TOKEN  = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not set! Add it to .env or Railway Variables.")

GENIUS_TOKEN = os.getenv("GENIUS_TOKEN", "")

EMBED_COLOR       = 0x1a1a2e
ACCENT_COLOR      = 0x9b59b6
SUCCESS_COLOR     = 0x1abc9c
ERROR_COLOR       = 0xe74c3c
WARNING_COLOR     = 0xf39c12
NOW_PLAYING_COLOR = 0x7289da

FFMPEG_EXECUTABLE = os.getenv("FFMPEG_PATH", "ffmpeg")

EQ_PRESETS = {
    "off":        "",
    "bassboost":  "bass=g=20,dynaudnorm=f=200",
    "nightcore":  "aresample=48000,asetrate=48000*1.25",
    "vaporwave":  "aresample=48000,asetrate=48000*0.8",
    "lofi":       "lowpass=f=5000,aecho=0.8:0.88:60:0.4",
    "8d":         "apulsator=hz=0.08",
    "soft":       "bass=g=5,treble=g=5,dynaudnorm=f=150",
    "phonk":      "bass=g=15,treble=g=-3,dynaudnorm=f=150",
}
EQ_DESCRIPTIONS = {
    "off":       "Normal",
    "bassboost": "Bass Boost",
    "nightcore": "Nightcore",
    "vaporwave": "Vaporwave",
    "lofi":      "Lo-Fi",
    "8d":        "8D Audio",
    "soft":      "Soft",
    "phonk":     "Phonk",
}

AUTOPLAY_GENRES = {
    "phonk":    ["phonk mix 2024", "dark phonk drift", "aggressive phonk mix", "memphis phonk"],
    "romantic": ["romantic songs hindi", "love songs playlist", "romantic english songs", "lofi love songs"],
    "lofi":     ["lofi hip hop study", "lofi chill beats", "lofi playlist 2024"],
    "hiphop":   ["hip hop mix 2024", "rap playlist", "trap beats mix"],
    "pop":      ["pop hits 2024", "trending pop songs"],
    "edm":      ["edm mix 2024", "house music mix"],
    "sad":      ["sad songs playlist", "emotional songs", "heartbreak songs"],
    "party":    ["party mix 2024", "dance hits", "club music mix"],
}

YDL_OPTIONS = {
    'format':                     'bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best',
    'noplaylist':                 False,
    'nocheckcertificate':         True,
    'ignoreerrors':               True,
    'logtostderr':                False,
    'quiet':                      True,
    'no_warnings':                True,
    'default_search':             'ytsearch',
    'source_address':             '0.0.0.0',
    'extractor_retries':          5,
    'fragment_retries':           5,
    'skip_unavailable_fragments': True,
    'playlistend':                50,
}
YDL_OPTIONS_SINGLE = {**YDL_OPTIONS, 'noplaylist': True}
