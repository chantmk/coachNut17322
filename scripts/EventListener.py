import os
import discord
from discord.ext import commands

from scripts.Utils import setupLogger
from scripts.Keys import *
from scripts.DataStructure import MessageState

LOGGER_TAG = "Event Listener"

class EventListener(commands.Cog):
    def __init__(self, bot, handler, config):
        self.bot = bot
        self.logger = setupLogger(handler, LOGGER_TAG)
        self.channel = ""
        self.message = ""
        self.flag = MessageState.DELETED
        self.taggedMessage = dict()
        self.config = config

    @commands.Cog.listener('on_connect')
    async def onConnected(self):
        self.logger.info("On Connect")

    @commands.Cog.listener('on_disconnect')
    async def onDisconnected(self): 
        self.logger.info("On Disconnect")

    @commands.Cog.listener("on_resume")
    async def onResumed(self):
        self.logger.info("On Resume")

    @commands.Cog.listener('on_guild_join')
    async def onGuildJoin(self, guild):
        self.logger.info("On Guild Join")
        channel_name = self.config[CONFIG_KEY][CONFIG_NAME_KEY]
        if(channel_name == ""):
            channel_name = self.config[CONFIG_KEY][DEFAULT_NAME_KEY]
        general_channel = ""
        for channel in guild.channels:
            if channel.name == self.config[CONFIG_KEY][DEFAULT_NAME_KEY]:
                general_channel = channel
            if channel.name == channel_name:
                self.channel = channel
                break
        else:
            self.channel = general_channel

        async for elem in self.channel.history(limit=50).filter(self.botMessageFilter):
            await elem.delete()
        await self.sendMessage()

    @commands.Cog.listener('on_ready')
    async def ready(self):
        self.logger.info("On Ready")
        channel_name = self.config[CONFIG_KEY][CONFIG_NAME_KEY]
        if(channel_name == ""):
            channel_name = self.config[CONFIG_KEY][DEFAULT_NAME_KEY]
        self.channel = discord.utils.get(self.bot.get_all_channels(), name=channel_name)
        await self.clearMessage()
        self.logger.info("Logged in as {0.user}".format(self.bot))

    @commands.Cog.listener('on_message')
    async def onMessage(self, message):
        self.logger.info("On Message Received: {}".format(message))
        if not message.author.bot:
            await self.refreshMessage()

    @commands.Cog.listener('on_message_delete')
    async def onMessageDelete(self, message):
        self.logger.info("On Message Delete: {}".format(message))

    @commands.Cog.listener('on_reaction_add')
    async def onReactionAdd(self, reaction, user):
        self.logger.info("On Reaction Added; Reaction: {}, User: {}".format(reaction, user))

    @commands.Cog.listener('on_raw_reaction_add')
    async def onRawReactionAdd(self, payload):
        self.logger.info("On Raw Reaction Added: {}".format(payload))
        await self.addedEmoji(payload)

    @commands.Cog.listener('on_reaction_remove')
    async def onReactionRemove(self, reaction, user):
        self.logger.info("On Reaction Removed; Reaction: {}, User: {}".format(reaction, user))

    @commands.Cog.listener('on_raw_reaction_remove')
    async def onRawReactionRemove(self, payload):
        self.logger.info("On Raw Reaction Removed: {}".format(payload))
        await self.removedEmoji(payload)

    def botMessageFilter(self, message):
        return message.author == self.bot.user

    async def clearMessage(self):
        async for elem in self.channel.history(limit=50).filter(self.botMessageFilter):
            if self.flag == MessageState.DELETED and elem.content == self.config[SENTENCE_KEY][WELCOME_MESSAGE_KEY]:
                self.message = elem
                self.flag = MessageState.CREATED
            else:
                await elem.delete()
        if self.flag == MessageState.DELETED:
            await self.sendMessage()

    async def sendMessage(self):
        if self.flag == MessageState.DELETED:
            self.flag = MessageState.CREATED
            self.message = await self.channel.send(self.config[SENTENCE_KEY][WELCOME_MESSAGE_KEY])
            for emoji in self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY]:
                await self.message.add_reaction(emoji)

    async def removeMessage(self):
        if self.flag == MessageState.CREATED or self.flag == MessageState.SENT:
            self.flag = MessageState.DELETED
            await self.message.delete()

    async def refreshMessage(self):
        found = await self.channel.history(limit = 10).find(self.botMessageFilter)
        if found == None:
            self.flag = MessageState.DELETED
            await self.sendMessage()
        else :
            await self.removeMessage()
            await self.sendMessage()

    async def addedEmoji(self, payload):
        if payload.user_id != self.bot.user.id:
            if payload.message_id == self.message.id:
                await self.handleMyMessage(payload)
            elif payload.message_id in self.taggedMessage:
                await self.handleTaggedMessage(payload)

    async def removedEmoji(self, payload):
        self.logger.info("remove emoji")

    async def handleMyMessage(self, payload):
        if payload.emoji.name not in self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY]:
            return
        if self.flag == MessageState.CREATED:
            self.flag = MessageState.SENT
            await self.tagSubscriber(payload.emoji.name)

    async def handleTaggedMessage(self, payload):
        if payload.emoji.name == self.config[EMOJI_KEY][TAGS_EMOJI_KEY][1]:
            current_count = self.taggedMessage[payload.message_id][0]
            if current_count >= (len(self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY])-1):
                return
            await self.tagSubscriber(self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY][current_count+1])
            await self.taggedMessage[payload.message_id][1].delete()
            self.taggedMessage.pop(payload.message_id)
        elif payload.emoji.name == self.config[EMOJI_KEY][TAGS_EMOJI_KEY][2]:
            current_count = self.taggedMessage[payload.message_id][0]
            if current_count <= 0:
                return
            await self.tagSubscriber(self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY][current_count-1])
            await self.taggedMessage[payload.message_id][1].delete()
            self.taggedMessage.pop(payload.message_id)
        elif payload.emoji.name == self.config[EMOJI_KEY][TAGS_EMOJI_KEY][3]:
            await self.taggedMessage[payload.message_id][1].delete()
            self.taggedMessage.pop(payload.message_id)


    async def tagSubscriber(self, count_emoji):
        message = await self.channel.send(self.config[SENTENCE_KEY][TAG_MESSAGE_KEY].format(count_emoji))
        for emoji in self.config[EMOJI_KEY][TAGS_EMOJI_KEY]:
            await message.add_reaction(emoji)
        self.taggedMessage[message.id] = (self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY].index(count_emoji), message)
        await self.refreshMessage()