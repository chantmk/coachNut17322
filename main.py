import os
import sys

from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path

from scripts.EventListener import EventListener
from scripts.CommandHandler import CommandHandler
from scripts.Utils import setupHandler, setupLogger, fromJsonFile
from scripts.Keys import *

load_dotenv(verbose=True)

LOGGER_TAG = "MAIN"

# Setup logging system
Path("./logs").mkdir(exist_ok=True)
handler = setupHandler()
logger = setupLogger(handler, LOGGER_TAG)

# find token if not raise error then exit
try: 
    token = os.getenv("DISCORD_TOKEN")
except Exception as e:
    logger.error(str(e))
    sys.exit(str(e))

# config data
config_data = dict()
config_data[CONFIG_KEY] = fromJsonFile("jsons/config.json", logger)
config_data[EMOJI_KEY] = fromJsonFile(config_data[CONFIG_KEY]["emoji_data"], logger)
config_data[SENTENCE_KEY] = fromJsonFile(config_data[CONFIG_KEY]["sentence_data"], logger)

# Setup bot
bot = commands.Bot(command_prefix=['/coach', 'cn!', '!', '/'])
bot.add_cog(EventListener(bot, handler, config_data))
bot.add_cog(CommandHandler(bot, handler, config_data))

# Run bot
bot.run(token)