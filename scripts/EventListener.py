import os
import discord
from discord import channel
from discord.colour import Colour
from discord.enums import Status
from discord.ext import commands
from discord.permissions import PermissionOverwrite, Permissions
from discord.utils import find, get

from scripts.Utils import setupLogger
from scripts.Keys import *
from scripts.DataStructure import MessageState

LOGGER_TAG = "Event Listener"

class EventListener(commands.Cog):
    def __init__(self, bot, handler, config):
        self.bot = bot
        self.logger = setupLogger(handler, LOGGER_TAG)
        self.channel = ""
        self.role = ""
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
        await self.findOrCreateRole(guild, self.config[CONFIG_KEY][NOT_ROLE_NAME])
        self.role = await self.findOrCreateRole(guild, self.config[CONFIG_KEY][ROLE_NAME])
        self.channel = await self.findOrCreateChannel(guild, self.config[CONFIG_KEY][BOT_NAME_KEY], self.config[CONFIG_KEY][BOT_TOPIC_KEY])
        async for elem in self.channel.history(limit=50).filter(self.botMessageFilter):
            await elem.delete()
        await self.sendMessage()

    @commands.Cog.listener('on_ready')
    async def ready(self):
        self.logger.info("On Ready")
        guild_list = self.bot.guilds
        guild = None
        if len(guild_list) == 0:
            self.logger.error("There is no guild connected")
            return
        elif len(guild_list) > 1:
            self.logger.error("There are more than 1 guild connected: {}, Connecting to {}".format(guild_list, guild_list[0].name))
        
        guild = guild_list[0]
        self.channel = await self.findOrCreateChannel(guild, self.config[CONFIG_KEY][BOT_NAME_KEY], self.config[CONFIG_KEY][BOT_TOPIC_KEY])
        self.role = await self.findOrCreateRole(guild, self.config[CONFIG_KEY][ROLE_NAME])
        await self.findOrCreateRole(guild, self.config[CONFIG_KEY][NOT_ROLE_NAME])
        await self.clearMessage()
        
        login_message = "Logged in as {0.user}".format(self.bot)
        self.logger.info(login_message)
        print(login_message)

    @commands.Cog.listener('on_message')
    async def onMessage(self, message):
        self.logger.info("On Message Received: {}".format(message))
        if not message.author.bot and message.channel == self.message.channel:
            await self.refreshMessage()
            await message.delete(delay=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_INTERRUPT_KEY])

    @commands.Cog.listener('on_message_delete')
    async def onMessageDelete(self, message):
        self.logger.info("On Message Delete: {}".format(message))
        if message.id in self.taggedMessage:
            await self.sendMessage()

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

    @commands.Cog.listener('on_member_update')
    async def onMemberUpdate(self, before, after):
        if before.status == after.status:
            return
        if before.status == Status.offline or after.status == Status.offline:
            check = find(lambda r: r.name == self.config[CONFIG_KEY][NOT_ROLE_NAME], before.roles)
            if check == None:
                if before.status == Status.offline:
                    await before.add_roles(self.role)
                elif after.status == Status.offline:
                    await after.remove_roles(self.role)


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
            await self.tagSubscriber(payload.emoji.name, payload.member.mention)

    async def handleTaggedMessage(self, payload):
        if payload.emoji.name == self.config[EMOJI_KEY][TAGS_EMOJI_KEY][0]:
            await self.editTaggedMessage(payload.message_id, payload.member)
        elif payload.emoji.name == self.config[EMOJI_KEY][TAGS_EMOJI_KEY][1]:
            await self.removeTaggedMessage(payload.message_id)
        elif payload.emoji.name in self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY]:
            idx = self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY].index(payload.emoji.name)
            if idx < len(self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY]) and idx >= 0:
                await self.tagSubscriber(self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY][idx], payload.member.mention)
                await self.removeTaggedMessage(payload.message_id)

    async def tagSubscriber(self, count_emoji, sender):
        message = await self.channel.send(self.config[SENTENCE_KEY][TAG_MESSAGE_KEY].format(self.role.mention, sender, count_emoji), delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_TAG_KEY])
        for emoji in self.config[EMOJI_KEY][TAGS_EMOJI_KEY]:
            await message.add_reaction(emoji)
        for emoji in self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY]:
            await message.add_reaction(emoji)
        self.taggedMessage[message.id] = (self.config[EMOJI_KEY][NUMBERES_EMOJI_KEY].index(count_emoji), message)
        await self.removeMessage()

    async def editTaggedMessage(self, message_id, joiner):
        msg = self.taggedMessage[message_id][1]
        if joiner not in msg.mentions:
            add_msg = self.config[SENTENCE_KEY][JOIN_MESSAGE_KEY].format(joiner.mention)
            await msg.edit(content=msg.content+add_msg , delete_after=self.config[CONFIG_KEY][MESSAGE_TIMEOUT_KEY][TIMEOUT_INTERRUPT_KEY])

    async def removeTaggedMessage(self, message_id):
        await self.taggedMessage[message_id][1].delete()
        self.taggedMessage.pop(message_id)

    async def findOrCreateChannel(self, guild, channel_name, topic): 
        found_channel = find(lambda guild_channel: guild_channel.name == channel_name, guild.channels)
        if found_channel == None: 
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                guild.me: PermissionOverwrite(send_messages=True)
            }
            self.logger.info("Channel not found, Creating")
            return await guild.create_text_channel(channel_name, overwrites=overwrite, position=0, topic=topic)
        else :
            return found_channel

    async def findOrCreateRole(self, guild, role_name):
        found_role = find(lambda guild_role: guild_role.name == role_name, guild.roles)
        if found_role == None:
            self.logger.info("Role not found: {}, Creating".format(role_name))
            return await guild.create_role(name=role_name, mentionable=True, colour=Colour.dark_teal())
        else:
            return found_role