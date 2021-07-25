import discord
import enum
from discord import channel
from discord.ext import commands
import os
import asyncio
import json
import emoji

from dotenv import load_dotenv
load_dotenv(verbose=True)

class MessageState(enum.Enum):
    CREATED = 0
    DELETED = 1
    SELECTED = 2
    SENT = 3

token = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix=['/coach', 'cn!', '!'])
# client = discord.Client(activity=discord.Game(name="NOT BLAMING YOU"))
channels = dict()
myChannel = ""
myMessage = ""
myMessageFlag = MessageState.DELETED
# game_emojis = ['\U0001f44d', '<:ward:805396908293750784>']
count_emojis = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 6)]
# count_emojis = [u'\u00000031\u000020e3']
up_down_emojis = ['\U0001F53C', '\U0001F53D', '\U00002611']
role = "<@&868454738168016926>"
taggedMessage = dict()

@bot.listen('on_ready')
async def ready():
    global myChannel
    global myMessage
    myChannel = bot.get_channel(int(os.getenv("TEST_CHANNEL_ID"))) 
    print("Logged in as {0.user}".format(bot))
    async for elem in myChannel.history(limit=50).filter(botMessageFilter):
        await elem.delete()
    await sendMessage()

@bot.listen('on_message')
async def inMessage(message):
    if message.author != bot.user:
        await refreshMessage()

@bot.listen('on_raw_reaction_add')
async def reactionRawAdd(payload):
    await addedEmoji(payload)

@bot.listen('on_raw_reaction_remove')
async def reactionRawRemove(payload):
    await removedEmoji(payload)

# @bot.event
# async def on_voice_state_update(member, before, after) :
#      if before.channel is None and after.channel is not None and not member.bot:
#         voice_client = await after.channel.connect() 
#         voice_client.play(discord.FFmpegPCMAudio("sawas-dee-krub.mp3"))
#         while voice_client.is_playing(): 
#             await(asyncio.sleep(0.2))
#         try:
#             if voice_client.channel is not None:
#                 await voice_client.disconnect() 
#         except AttributeError:
#             pass 

def botMessageFilter(message):
    return message.author.bot

async def sendMessage():
    global myMessage, myMessageFlag
    if myMessageFlag == MessageState.DELETED:
        myMessageFlag = MessageState.CREATED
        print(myMessageFlag.name)
        myMessage = await myChannel.send("Hello world!")
        for emoji in count_emojis:
            await myMessage.add_reaction(emoji)

async def removeMessage():
    global myMessage, myMessageFlag
    if myMessageFlag == MessageState.CREATED or myMessageFlag == MessageState.SENT:
        myMessageFlag = MessageState.DELETED
        print(myMessageFlag.name)
        await myMessage.delete()

async def refreshMessage():
    await removeMessage()
    await sendMessage()

# async def addedEmoji(payload):
#     global myMessageFlag, selected_game_emoji
#     if payload.message_id == myMessage.id and payload.user_id != bot.user.id and (payload.emoji.name in game_emojis or payload.emoji.name in count_emojis):
#         if myMessageFlag == MessageState.CREATED:
#             myMessageFlag = MessageState.SELECTED
#             print(myMessageFlag.name)
#             selected_game_emoji = payload.emoji
#             for emoji in count_emojis:
#                 await myMessage.add_reaction(emoji)
#         elif myMessageFlag == MessageState.SELECTED:
#             myMessageFlag = MessageState.SENT
#             print(myMessageFlag.name)
#             await tagSubscriber(selected_game_emoji, payload.emoji)
#             await refreshMessage()

async def addedEmoji(payload):
    global myMessageFlag, selected_game_emoji
    if payload.user_id != bot.user.id:
        if payload.message_id == myMessage.id:
            await handleMyMessage(payload)
        elif payload.message_id in taggedMessage:
            await handleTaggedMessage(payload)

async def removedEmoji(payload):
    print("removed")
    
async def handleMyMessage(payload):
    global myMessageFlag
    if payload.emoji.name not in count_emojis:
        return
    if myMessageFlag == MessageState.CREATED:
        myMessageFlag = MessageState.SENT
        await tagSubscriber(payload.emoji.name)
        await refreshMessage()

async def handleTaggedMessage(payload):
    if payload.emoji.name == up_down_emojis[0]:
        current_count = taggedMessage[payload.message_id][0]
        if current_count >= (len(count_emojis)-1):
            return
        await tagSubscriber(count_emojis[current_count+1])
        await taggedMessage[payload.message_id][1].delete()
        taggedMessage.pop(payload.message_id)
    elif payload.emoji.name == up_down_emojis[1]:
        current_count = taggedMessage[payload.message_id][0]
        if current_count <= 0:
            return
        await tagSubscriber(count_emojis[current_count-1])
        await taggedMessage[payload.message_id][1].delete()
        taggedMessage.pop(payload.message_id)
    elif payload.emoji.name == up_down_emojis[2]:
        await taggedMessage[payload.message_id][1].delete()
        taggedMessage.pop(payload.message_id)


async def tagSubscriber(count_emoji):
    message = await myChannel.send('@here {}'.format(count_emoji))
    for emoji in up_down_emojis:
        await message.add_reaction(emoji)
    taggedMessage[message.id] = (count_emojis.index(count_emoji), message)

bot.run(token)