import discord
from discord.ext import commands, tasks
import time
import os

TOKEN = os.getenv("DISCORD_TOKEN")

AFK_CHANNEL_NAME = "🎵 AFK-Bereich"
CHECK_SECONDS = 30
AFK_AFTER_SECONDS = 300

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

idle_since = {}

@bot.event
async def on_ready():
    print(f"Bot online als {bot.user}")
    check_afk.start()

@tasks.loop(seconds=CHECK_SECONDS)
async def check_afk():
    now = time.time()

    for guild in bot.guilds:
        afk_channel = discord.utils.get(
            guild.voice_channels,
            name=AFK_CHANNEL_NAME
        )

        if not afk_channel:
            continue

        for vc in guild.voice_channels:
            if vc == afk_channel:
                continue

            for member in vc.members:
                if member.bot:
                    continue

                voice = member.voice

                if voice.self_mute or voice.self_deaf:
                    idle_since.setdefault(member.id, now)

                    if now - idle_since[member.id] >= AFK_AFTER_SECONDS:
                        await member.move_to(afk_channel)
                        idle_since.pop(member.id, None)
                else:
                    idle_since.pop(member.id, None)

bot.run(TOKEN)
