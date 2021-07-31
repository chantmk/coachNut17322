import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

import logging
import os
import sys

from scripts.EventListener import EventListener
from scripts.CommandHandler import CommandHandler
from scripts.Utils import setupHandler, setupLogger, fromJsonFile

load_dotenv(verbose=True)

# Setup logging system
Path("./logs").mkdir(exist_ok=True)
handler = setupHandler()
logger = setupLogger(handler, "Main")

# find token if not raise error then exit
try: 
    token = os.getenv("DISCORD_TOKEN")
except Exception as e:
    logger.error(str(e))
    sys.exit(str(e))

# config data
config = fromJsonFile("jsons/config.json", logger)
emoji = fromJsonFile(config["emoji_data"], logger)

# Setup bot
bot = commands.Bot(command_prefix=['/coach', 'cn!', '!', '/'])
bot.add_cog(EventListener(bot, handler, config, emoji))
bot.add_cog(CommandHandler(bot, handler, config, emoji))

# Run bot
bot.run(token)