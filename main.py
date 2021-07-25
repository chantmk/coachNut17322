import discord
import enum
from discord.ext import commands
import os

from dotenv import load_dotenv
load_dotenv(verbose=True)

class MessageState(enum.Enum):
    CREATED = 0
    DELETED = 1
    SELECTED = 2
    SENT = 3

token = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix=['/coach', 'cn!', '!', '/'])
channels = dict()
myChannel = ""
myMessage = ""
myMessageFlag = MessageState.DELETED
count_emojis = ["{}\N{COMBINING ENCLOSING KEYCAP}".format(num) for num in range(1, 6)]
up_down_emojis = ['\U0001F44A', '\U0001F53C', '\U0001F53D', '\U00002611']
taggedMessage = dict()

@bot.listen('on_ready')
async def ready():

    global myChannel, myMessage, generalChannel

    channel_name = os.getenv("CHANNEL_NAME")
    if(channel_name == None):
        channel_name = "general"
    myChannel = discord.utils.get(bot.get_all_channels(), name=channel_name)

    async for elem in myChannel.history(limit=50).filter(botMessageFilter):
        await elem.delete()
    await sendMessage()
    print("Logged in as {0.user} in {1}".format(bot, channel_name))

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

def botMessageFilter(message):
    return message.author == bot.user

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
    global myMessageFlag
    found = await myChannel.history(limit = 10).find(botMessageFilter)
    if found == None:
        myMessageFlag = MessageState.DELETED
        print("assumed deleted")
        await sendMessage()
    else :
        await removeMessage()
        await sendMessage()

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

async def handleTaggedMessage(payload):
    if payload.emoji.name == up_down_emojis[1]:
        current_count = taggedMessage[payload.message_id][0]
        if current_count >= (len(count_emojis)-1):
            return
        await tagSubscriber(count_emojis[current_count+1])
        await taggedMessage[payload.message_id][1].delete()
        taggedMessage.pop(payload.message_id)
    elif payload.emoji.name == up_down_emojis[2]:
        current_count = taggedMessage[payload.message_id][0]
        if current_count <= 0:
            return
        await tagSubscriber(count_emojis[current_count-1])
        await taggedMessage[payload.message_id][1].delete()
        taggedMessage.pop(payload.message_id)
    elif payload.emoji.name == up_down_emojis[3]:
        await taggedMessage[payload.message_id][1].delete()
        taggedMessage.pop(payload.message_id)


async def tagSubscriber(count_emoji):
    message = await myChannel.send('@here {}'.format(count_emoji))
    for emoji in up_down_emojis:
        await message.add_reaction(emoji)
    taggedMessage[message.id] = (count_emojis.index(count_emoji), message)
    await refreshMessage()

bot.run(token)