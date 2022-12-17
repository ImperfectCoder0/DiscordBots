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
load_dotenv("heavy_variables/environment.env")
TOKEN = os.getenv('DISCORD_TOKEN2')

def updateData(member: discord.Member, msgs):
    with open("data.json", "r") as jsonFile:
        try:
            jsonData: dict = json.load(jsonFile)
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
        number: dict = json.load(jsonFile)[str(member.id)]
        jsonFile.close()

    return int(number)


@bot.event
async def on_ready():
    global start_time
    start_time = datetime.now()
    print("Ready!")
    print(start_time)



@commands.has_permissions(ban_members=True)
@bot.slash_command(name='regulate', description='Set a max message on a member.')
async def regulate(ctx, member: discord.Option(discord.Member, "Enter someone", required=True), number: discord.Option(int, required=True)):
    if type(number) is not int:
        await ctx.respond("NUMBER MUST BE A NUMBER")
        return
    updateData(member, number)
    await ctx.respond(f"Done! {member}'s message limit is {number}")

@bot.slash_command(name='purge', description='Begin the purge')
async def purge(ctx: discord.Message, member: discord.Option(discord.Member, "Enter someone", required=True)):
    print("Purge")
    messages = []
    async for message in ctx.channel.history():
        if message.author == member:
            messages.append(message.content)
    await ctx.respond("Purging... 0.00%")
    print(len(messages) - getData(member))
    for var in range(len(messages) - getData(member)):
        await ctx.channel.purge(limit=1, oldest_first=True)
        await ctx.edit(content=f"Purging... {var/(len(messages) - getData(member))*100:.2f}% done")
    await ctx.edit(content=f"Purge completed")


@bot.slash_command(name='message', description='Stupid command')
async def message(ctx, member: discord.Option(discord.Member, "Enter someone", required=True)):
    await ctx.respond("Funny fun funs")

bot.run(TOKEN)





