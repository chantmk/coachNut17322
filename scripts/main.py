import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import date, datetime
from pathlib import Path

import logging
import os

import EventListener

load_dotenv(verbose=True)

Path("./logs").mkdir(exist_ok=True)

filename = datetime.now().strftime("%Y%m%d%H%M%S")
handler = logging.FileHandler(filename=f'logs\{filename}.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

token = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix=['/coach', 'cn!', '!', '/'])

bot.add_cog(EventListener.EventListener(bot, handler))
bot.run(token)