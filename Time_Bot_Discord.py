import random
from datetime import datetime, timedelta
import os
import threading
import discord
from dotenv import load_dotenv
import re
from discord.ext import commands


intents = discord.Intents.all()
bot = discord.Bot(intents=intents)


load_dotenv("heavy_variables/environment.env")
TOKEN = os.getenv('DISCORD_TOKEN')
guild_ids = bot.guilds
start_time = None
running = True
act_list = {}
__version__ = "0.0.8.001"

@bot.event
async def on_ready():
    global act_list, start_time
    # 0 -> Time
    # 1 -> Member Locked
    # 2 -> Cooldown
    # 3 -> Online Time

    for guilds in bot.guilds:
        for members in guilds.members:
            if members not in act_list.keys():
                act_list[members] = [None, None, None, None]
                act_list[members][0] = datetime.now()
                act_list[members][1] = False
                act_list[members][2] = [datetime.now(), datetime.now()-timedelta(minutes=30), datetime.now()-timedelta(minutes=30)]
                act_list[members][3] = [timedelta(seconds=0)]

    start_time = datetime.now()
    print("Ready!")
    print(start_time)
    runThread.start()


@bot.slash_command(name='checktime', description='Check the time that someone is online')
async def checktime(ctx, member: discord.Option(discord.Member, "Enter someone", required=True)):
    global act_list
    print(member)
    if not await cooldown(ctx, ctx.author, 4, 1):
        return
    print("here")
    embed = discord.Embed(title=f"Checking time of... {member.display_name}",
                          description=f"Percent of time: {((sum(act_list[member][3], timedelta())).total_seconds()) / ((datetime.now() - start_time).total_seconds()) * 100: .2f}%")
    try:
        embed.set_thumbnail(url=member.avatar.url)
    except:
        embed.set_thumbnail(url=member.default_avatar.url)
    embed.add_field(name="Start Time", value=start_time.strftime("%H:%M:%S" + " UTC" + " at %Y-%m-%d"))
    embed.set_footer(text="Note: Bot is in experimental phase, and times may reset during the day.\nAll data is not fully accurate.")


    await ctx.respond(embed=embed)
    act_list[ctx.author][2][1] = datetime.now()

# @bot.command()
# async def leaderboard(ctx):
#     global act_list
#     if start_time < datetime.now()+timedelta(seconds=4):
#         await ctx.respond("I don't see what you're trying to do here. \nThe bot just started, and you're immediately asking for stats! \nWait a minute!")
#         return
#     timelist = []
#     for person in act_list.keys():
#         if person.guild == ctx.guild:
#             print(act_list[person][3])
#             timelist.append((person.name, sum(act_list[person][3])))
# 
#     print(timelist)


@bot.slash_command(name='starttime', description='Check when the bot started')
async def starttime(ctx):
    print("Starttime")
    await ctx.respond(f"Start time of {__version__}: {start_time} UTC")


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != None:
        vc = bot.get_channel(before.channel.id)
        guild = member.guild
        if not discord.utils.get(guild.roles, name=vc.name):
            await guild.create_role(name=vc.name)
        role = discord.utils.get(guild.roles, name=vc.name)
        await member.remove_roles(role)
    if after.channel != None:
        vc = bot.get_channel(after.channel.id)
        guild = member.guild
        if not discord.utils.get(guild.roles, name=vc.name):
            await guild.create_role(name=vc.name)
        role = discord.utils.get(guild.roles, name=vc.name)
        chat_check_name = re.compile(r'[a-zA-Z0-9\s]-?')
        matches = chat_check_name.findall(str(vc.name))
        string = ''
        for match in matches:
            string = string + match.replace(' ', '-').lower()
        if not check_channel(string + '-chat', guild):
            role_list = []
            for roles in guild.roles:
                if role.permissions.kick_members and role.permissions.ban_members:
                    role_list.append(discord.utils.get(guild.roles, name=role.name))
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True),
            }
            for roles in role_list:
                overwrites[roles] = discord.PermissionOverwrite(read_messages=True)

            await guild.create_text_channel(string + '-chat', overwrites=overwrites, category=after.channel.category)
        await member.add_roles(role)


def check_channel(channel_name, server):
    check = False
    for channel in server.channels:
        if channel.name == channel_name:
            check = True
    return check


async def cooldown(ctx, member, seconds, pos):
    global act_list
    if datetime.now() - act_list[member][2][pos] <= timedelta(seconds=seconds):
        embedVar = discord.Embed(title="Man, you gotta slow it down!", description=f"You still have {timedelta(seconds=seconds) - (datetime.now() - act_list[member][2][pos])} left!", color=0x044322)
        await ctx.respond(embed=embedVar)
        return False
    else:
        return True


def run():
    global start_time, running, act_list
    for member_ in act_list.keys():
        act_list[member_][1] = False
    while running:
        for member_ in act_list.keys():
            if not member_.status == discord.Status.offline:
                act_list[member_][3][-1] = datetime.now() - act_list[member_][0]
                act_list[member_][1] = True
            elif member_.status == discord.Status.offline:
                act_list[member_][0] = datetime.now()
                if act_list[member_][1]:
                    act_list[member_][1] = False
                    act_list[member_][3].append(timedelta(seconds=0))
                    if len(act_list[member_][3]) > 300:
                        act_list[member_][3][0] = sum(act_list[member_][3])

@bot.slash_command(name='rate', description='Rates you!')
async def rate(ctx):
    values = [random.randrange(0, 1000), random.randrange(0, 1000),
              random.randrange(0, 1000), random.randrange(0, 1000),
              random.randrange(0, 1000), random.randrange(0, 1000),
              random.randrange(0, 1000)]
    embed = discord.Embed(title="You rate as:", description=f"""
    Strength - {values[0]/10}%
    Stealth - {values[1]/10}%
    Intelligence - {values[2]/10}%
    Wisdom - {values[3]/10}%
    Charisma - {values[4]/10}%
    Persistence - {values[5]/10}%
    Good - {values[6]/10}%
    Evil - {(1000 - values[6])/10}%

    """)

    class_ = ["Normal"]
    if values[0] <= 150 and values[2] >= 900:
        class_.append("Brain")
        if values[2] == 1000:
            class_.append("Super Brain")
    if values[0] >= 750 and values[1] >= 850 and values[2] >= 900 and values[5] >= 900:
        class_.append("Agent")
        if values[0] == 1000 and values[1] == 1000 and values[2] == 1000 and values[5] == 1000:
            class_.append("Super Agent")
    if values[0] >= 950 and values[5] >= 750:
        class_.append("Warrior")
    if values[6] <= 300:
        class_.append("Reluctant Evil")
        if values[6] <= 150:
            class_.append("Pure Evil")
    if values[6] >= 700:
        class_.append("Reluctant Good")
        if values[6] >= 850:
            class_.append("Pure Good")

    embed.add_field(name="Class(es)", value=class_)
    await ctx.respond(embed=embed)




runThread = threading.Thread(target=run)

bot.run(TOKEN)
