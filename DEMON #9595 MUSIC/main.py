import discord
from discord.ext import commands
import asyncio
from config import TOKEN, PREFIX, ACCENT_COLOR, SUCCESS_COLOR, ERROR_COLOR

class MusicBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states    = True
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.listening, name="✦ db play"),
            help_command=None,
        )

    async def setup_hook(self):
        try:
            await self.load_extension("music_cog")
            print("✅ Music cog loaded.")
        except Exception as e:
            print(f"❌ Music cog failed: {e}")
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
        print("✅ Commands synced.")

    async def on_ready(self):
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  ✦ {self.user} is online!")
        print(f"  ✦ Guilds: {len(self.guilds)}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound): return
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(embed=discord.Embed(
                description=f"❌ missing: `{error.param.name}` — use `{PREFIX}help`", color=ERROR_COLOR))
        print(f"Error: {error}")

bot = MusicBot()

@bot.hybrid_command(name="ping", description="🏓 Check latency")
async def ping(ctx):
    await ctx.defer()
    ms    = round(bot.latency * 1000)
    color = SUCCESS_COLOR if ms < 100 else ACCENT_COLOR if ms < 200 else ERROR_COLOR
    bar   = "█" * min(10, ms // 20) + "░" * max(0, 10 - ms // 20)
    await ctx.send(embed=discord.Embed(
        title="🏓 Pong!",
        description=f"`{ms}ms` `{bar}`",
        color=color
    ).set_footer(text="✦ all systems go!" if ms < 150 else "⚠️ slight delay"))

if __name__ == "__main__":
    bot.run(TOKEN)
