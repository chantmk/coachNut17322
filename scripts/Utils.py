import logging
import json
import asyncio
from discord import FFmpegPCMAudio
from gtts import gTTS
from datetime import datetime

async def sendTTS(ctx, message, filename):
    tts = gTTS(text=message, lang='th')
    tts.save(filename)
    user_channel = ctx.author.voice.channel

    # if voice_client is None or ctx.me.voice is None or ctx.me.voice.channel != user_channel:
    #     voice_client = await user_channel.connect() 

    voice_client = await user_channel.connect()        
    voice_client.play(FFmpegPCMAudio(source=filename))
    while voice_client.is_playing(): 
        await(asyncio.sleep(0.2))
    await voice_client.disconnect()

def getConfig(logger):
    return fromJsonFile("jsons/config.json", logger)

def setupHandler():
    filename = datetime.now().strftime("%Y%m%d%H%M%S")
    handler = logging.FileHandler(filename=f'logs\{filename}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    return handler

def setupLogger(handler, name="discord", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def toJsonFile(filename, dictJson, logger):
    try:
        with open(filename, 'w', encoding="utf8") as f:
            json.dump(dictJson, f, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)
        logger.info(f'Success dump to {filename}')
        return True
    except Exception as e:
        logger.error(str(e))
        return False

def fromJsonFile(filename, logger):
    try:
        with open(filename, 'r', encoding="utf8") as f:
            container = json.load(f)
        logger.info(f'Success load from {filename}')
        return container
    except Exception as e:
        logger.error(str(e))
        return dict()