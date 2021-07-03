import discord
from discord.ext import commands
import os
import asyncio

from dotenv import load_dotenv
load_dotenv(verbose=True)

token = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix=['/coach'])

@bot.event
async def on_ready(): 
    print("Logged in as {0.user}".format(bot))

@bot.event
async def on_voice_state_update(member, before, after) :
     if before.channel is None and after.channel is not None and not member.bot:
        voice_client = await after.channel.connect() 
        voice_client.play(discord.FFmpegPCMAudio("sawas-dee-krub.mp3"))
        while voice_client.is_playing(): 
            await(asyncio.sleep(0.2))
        try:
            if voice_client.channel is not None:
                await voice_client.disconnect() 
        except AttributeError:
            pass 

@bot.event
async def on_message() :
    
bot.run(token)