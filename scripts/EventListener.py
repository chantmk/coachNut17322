import os
import discord
import logging
import Utils
from discord import channel
from discord.ext import commands
from DataStructure import MessageState

count_emojis = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 6)]
up_down_emojis = ['\U0001F44A', '\U0001F53C', '\U0001F53D', '\U00002611']

class EventListener(commands.Cog):
    def __init__(self, bot, handler):
        self.bot = bot
        self.logger = Utils.setupLogger(handler, "Main")
        self.channel = ""
        self.message = ""
        self.flag = MessageState.DELETED
        self.taggedMessage = dict()

    @commands.Cog.listener('on_connect')
    async def onConnected(self):
        self.logger.info("On Connect")
        test_channel_name = os.getenv("CHANNEL_NAME")
        if(test_channel_name == None):
            test_channel_name = "general"
        test_myChannel = discord.utils.get(self.bot.get_all_channels(), name=test_channel_name)

    @commands.Cog.listener('on_disconnect')
    async def onDisconnected(self): 
        self.logger.info("On Disconnect")

    @commands.Cog.listener("on_resume")
    async def onResumed(self):
        self.logger.info("On Resume")

    @commands.Cog.listener('on_guild_join')
    async def onGuildJoin(self, guild):
        self.logger.info("On Guild Join")
        channel_name = os.getenv("CHANNEL_NAME")
        if(channel_name == None):
            channel_name = "general"
        general_channel = ""
        for channel in guild.channels:
            if channel.name == "general":
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
        channel_name = os.getenv("CHANNEL_NAME")
        if(channel_name == None):
            channel_name = "general"
        self.channel = discord.utils.get(self.bot.get_all_channels(), name=channel_name)
        async for elem in self.channel.history(limit=50).filter(self.botMessageFilter):
            await elem.delete()
        await self.sendMessage()
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
    async def onReactionRawAdd(self, payload):
        self.logger.info("On Raw Reaction Added: {}".format(payload))
        await self.addedEmoji(payload)

    @commands.Cog.listener('on_reaction_remove')
    async def onReactionRemove(self, reaction, user):
        self.logger.info("On Reaction Removed; Reaction: {}, User: {}".format(reaction, user))

    @commands.Cog.listener('on_raw_reaction_remove')
    async def reactionRawRemove(self, payload):
        self.logger.info("On Raw Reaction Removed: {}".format(payload))
        await self.removedEmoji(payload)

    def botMessageFilter(self, message):
        return message.author == self.bot.user

    async def sendMessage(self):
        if self.flag == MessageState.DELETED:
            self.flag = MessageState.CREATED
            print(self.flag.name)
            self.message = await self.channel.send("เรียกกี่คนดี")
            for emoji in count_emojis:
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
        self.logger("remove emoji")

    async def handleMyMessage(self, payload):
        if payload.emoji.name not in count_emojis:
            return
        if self.flag == MessageState.CREATED:
            self.flag = MessageState.SENT
            await self.tagSubscriber(payload.emoji.name)

    async def handleTaggedMessage(self, payload):
        if payload.emoji.name == up_down_emojis[1]:
            current_count = self.taggedMessage[payload.message_id][0]
            if current_count >= (len(count_emojis)-1):
                return
            await self.tagSubscriber(count_emojis[current_count+1])
            await self.taggedMessage[payload.message_id][1].delete()
            self.taggedMessage.pop(payload.message_id)
        elif payload.emoji.name == up_down_emojis[2]:
            current_count = self.taggedMessage[payload.message_id][0]
            if current_count <= 0:
                return
            await self.tagSubscriber(count_emojis[current_count-1])
            await self.taggedMessage[payload.message_id][1].delete()
            self.taggedMessage.pop(payload.message_id)
        elif payload.emoji.name == up_down_emojis[3]:
            await self.taggedMessage[payload.message_id][1].delete()
            self.taggedMessage.pop(payload.message_id)


    async def tagSubscriber(self, count_emoji):
        message = await self.channel.send('@here {}'.format(count_emoji))
        for emoji in up_down_emojis:
            await message.add_reaction(emoji)
        self.taggedMessage[message.id] = (count_emojis.index(count_emoji), message)
        await self.refreshMessage()