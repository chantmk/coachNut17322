from discord.ext import commands
from scripts.Utils import *

from scripts.Keys import SENTENCE_KEY
class CommandHandler(commands.Cog):
    def __init__(self, bot, handler, config):
        self.bot = bot
        self.logger = setupLogger(handler, "CommandHandler")
        self.sentence = fromJsonFile(config[SENTENCE_KEY], self.logger)
    
    @commands.command(aliases=["b"])
    async def curse(self, ctx, **args):
        self.logger.info("Cursing")