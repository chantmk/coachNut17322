from discord.ext import commands
from scripts.Utils import setupLogger, fromJsonFile

class CommandHandler(commands.Cog):
    def __init__(self, bot, handler, config, emoji):
        self.bot = bot
        self.logger = setupLogger(handler, "CommandHandler")
        self.emoji = emoji
        self.sentence = fromJsonFile(config["sentence_data"], self.logger)
    
    @commands.command(aliases=["b"])
    async def blameSomeone(self, ctx, **args):
        print("yeah")
        print(ctx)
        print(args)