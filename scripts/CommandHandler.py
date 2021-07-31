import discord

bot = ""
logger = ""

@bot.command(aliases=["b", "blame"])
async def blameSomeone(ctx, **args):
    print("yeah")
    print(ctx)
    print(args)