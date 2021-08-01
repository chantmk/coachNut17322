from random import choice
from discord.ext import commands

from scripts.Utils import *
from scripts.Keys import *
from scripts.Aliases import ADD_ALIASES, REMOVE_ALIASES

LOGGER_TAG = "Command Handler"
class CommandHandler(commands.Cog):
    def __init__(self, bot, handler, config):
        self.bot = bot
        self.logger = setupLogger(handler, LOGGER_TAG)
        self.config = config
    
    @commands.command(aliases=["c"])
    async def curse(self, ctx, *args):
        await self.handleCurse(ctx, args, False)

    @commands.command(aliases=["cs", "curse_with_sound"])
    async def curseWithSound(self, ctx, *args):
        if ctx.author.voice is None:
            await ctx.send(self.config[SENTENCE_KEY][NOT_IN_ROOM_KEY], delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_CURSE_KEY])
            await ctx.message.delete(delay=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])
        else:
            await self.handleCurse(ctx, args, True)
        
    async def handleCurse(self, ctx, args, tts=False):
        if len(args) == 0:
            await ctx.send(self.config[SENTENCE_KEY][NO_NAME_KEY], delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_CURSE_KEY])
        elif len(args) == 1:
            curse_sentence = choice(self.config[SENTENCE_KEY][CURSE_KEY]).format(args[0])
            if tts:
                await sendTTS(ctx, curse_sentence, self.config[CONFIG_KEY][CURSE_FILE_NAME])
            else :
                await ctx.send(curse_sentence, delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_CURSE_KEY])
        elif len(args) == 2:
            await self.handleAddRemoveCurse(ctx, args[0], args[1])
        await ctx.message.delete(delay=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])

    async def handleAddRemoveCurse(self, ctx, curse, command):
        if command.lower() in ADD_ALIASES:
            try:
                if curse not in self.config[SENTENCE_KEY][CURSE_KEY]:
                    self.config[SENTENCE_KEY][CURSE_KEY].append(curse)
                    toJsonFile(self.config[CONFIG_KEY][SENTENCE_DATA_KEY], self.config[SENTENCE_KEY], self.logger)
                    await ctx.send(self.config[SENTENCE_KEY][ADD_RESULT_KEY][SUCCESS_KEY].format(curse), delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])
                else:
                    await ctx.send(self.config[SENTENCE_KEY][ADD_RESULT_KEY][CONTAINED_KEY].format(curse), delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])
            except Exception as e:
                self.logger.error(str(e))
                await ctx.send(self.config[SENTENCE_KEY][ADD_RESULT_KEY][FAILED_KEY].format(curse), delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])
        elif command.lower() in REMOVE_ALIASES:
            try:
                if curse in self.config[SENTENCE_KEY][CURSE_KEY]:
                    self.config[SENTENCE_KEY][CURSE_KEY].remove(curse)
                    toJsonFile(self.config[CONFIG_KEY][SENTENCE_DATA_KEY], self.config[SENTENCE_KEY], self.logger)
                    await ctx.send(self.config[SENTENCE_KEY][REMOVE_RESULT_KEY][SUCCESS_KEY].format(curse), delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])
                else:
                    await ctx.send(self.config[SENTENCE_KEY][REMOVE_RESULT_KEY][CONTAINED_KEY].format(curse), delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])
            except Exception as e:
                self.logger.error(str(e))
                await ctx.send(self.config[SENTENCE_KEY][REMOVE_RESULT_KEY][FAILED_KEY].format(curse), delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_COMMAND_KEY])