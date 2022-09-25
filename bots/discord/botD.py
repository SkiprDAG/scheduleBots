import discord
from discord.ext import commands

from config import TOKEN_DISCORD

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents)
bot.run(TOKEN_DISCORD)
