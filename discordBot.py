import threading
import os
from datetime import datetime
import discord
from discord.ext import commands
from discord.ext import bridge
from dotenv import load_dotenv
import json

intents = discord.Intents.all()
start_time = None
bot = commands.Bot(command_prefix="::", intents=intents)
load_dotenv("environment.env")
TOKEN = os.getenv('DISCORD_TOKEN')


def updateData(member: discord.Member, msgs):
    with open("data.json", "r+") as jsonFile:
        try:
            jsonData: dict = dict(json.load(jsonFile))
        except json.decoder.JSONDecodeError:
            jsonData = {}
        jsonFile.close()

    with open("data.json", "w") as jsonFile:
        try:
            jsonData[member.id] = msgs
            json.dump(jsonData, jsonFile)
        except json.decoder.JSONDecodeError as err:
            print(err)
            json.dump({member.id: msgs}, jsonFile)
        jsonFile.close()


def getData(member: discord.Member):
    with open("data.json", "r") as jsonFile:
        number = json.load(jsonFile)[str(member.id)]
        jsonFile.close()

    return int(number)


@bot.event
async def on_ready():
    global start_time
    start_time = datetime.now()
    print("Ready!")
    print(start_time)

@bot.slash_command(name='regulate', description='Set a max message on a member.')
@commands.has_permissions(ban_members=True)
async def regulate(ctx, member: discord.Option(discord.Member, "Enter someone's name", required=True),
                   number: discord.Option(int, required=True)):
    if type(number) is not int:
        await ctx.respond("Number must be an actual number")
        return
    updateData(member, number)
    await ctx.respond(f"Done! {member}'s message limit is {number}")


@bot.slash_command(name='purge', description='Begin the purge')
async def purge(ctx: discord.ApplicationContext, member: discord.Option(discord.Member, "Enter someone's name", required=True)):
    try:
        messages = []
        async for message in ctx.channel.history():
            if message.author == member:
                messages.append(message.id)
        print(messages)
        print(messages[getData(member):])
        def func(msg):
            return (msg.author.id == member.id and msg.id in messages[getData(member):])
        await ctx.channel.purge(limit=ctx.channel.history().limit, oldest_first=True, check=func)
        await ctx.respond(f"Purge completed")
    except discord.errors.ApplicationCommandInvokeError:
        await ctx.respond(f"You haven't done /regulate yet!")



bot.run(TOKEN)
