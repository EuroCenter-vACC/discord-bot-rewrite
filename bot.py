import discord
import asyncio
import os
import mysql.connector
import time

from discord.ext import commands, tasks
from discord.utils import get
from discord.ext.commands import errors

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
bot_prefix = config.get('GENERAL', 'prefix')
OwnerID = int(config.get("USERS", "bot_owner"))
botcommandsChannelID = int(config.get('CHANNELS', 'botcommands'))

db_host = config.get("DATABASE", "host")
db_username = config.get("DATABASE", "username")
db_password = config.get("DATABASE", "password")
db_name = config.get("DATABASE", "database_name")

tokenFile = open("tokens/token.txt")
TOKEN = tokenFile.readline()

client = discord.Client()
client = commands.Bot(command_prefix=bot_prefix)
client.remove_command('help')

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HEADER = '\033[95m'

@client.event
async def on_connect():
    print("Bot connected")

@client.event
async def on_ready():
    import datetime
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"EUC sectors | {bot_prefix}help"))
    channel = client.get_channel(botcommandsChannelID)
    print(f'Bot ready\nLogged on as {client.user}')

def load_cogs():
    print(f"{bcolors.BOLD}{bcolors.HEADER}Loading extensions{bcolors.ENDC}")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not "__" in filename:
            client.load_extension(f"cogs.{filename[:-3]}")
            print(f"{bcolors.OKGREEN}Loaded cog:{bcolors.ENDC} {filename}")
        else:
            if not filename == "__pycache__":
                print(f"{bcolors.WARNING}Ignored cog:{bcolors.ENDC} {filename}")
    print(f"{bcolors.BOLD}{bcolors.OKBLUE}DONE.{bcolors.ENDC}")


@client.command()
async def load(ctx, cogname):
    if ctx.author.id == OwnerID:
        if f"{cogname}.py" in os.listdir("./cogs") and not "__" in cogname:
            try:
                client.load_extension(f"cogs.{cogname}")
                await ctx.send(f"**Loaded:** {cogname}")
                print(f"{bcolors.OKGREEN}Loaded cog:{bcolors.ENDC} {cogname}")
                return
            except commands.errors.ExtensionAlreadyLoaded:
                await ctx.send(f"**Error:** {cogname} is already loaded")
                return
        else:
            await ctx.send(f"**Error:** {cogname} does not exist")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")


@client.command()
async def unload(ctx, cogname):
    if ctx.author.id == OwnerID:
        if f"{cogname}.py" in os.listdir("./cogs") and not "__" in cogname:
            try:
                client.unload_extension(f"cogs.{cogname}")
                await ctx.send(f"**Unloaded:** {cogname}")
                print(f"{bcolors.WARNING}Unloaded cog:{bcolors.ENDC} {cogname}")
                return
            except commands.errors.ExtensionNotLoaded:
                await ctx.send(f"**Error:** {cogname} is not yet loaded")
                return
        else:
            await ctx.send(f"**Error:** {cogname} does not exist")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")

@client.command()
async def reload(ctx, cogname):
    if ctx.author.id == OwnerID:
        if f"{cogname}.py" in os.listdir("./cogs") and not "__" in cogname:
            try:
                client.unload_extension(f"cogs.{cogname}")
            except:
                pass
            try:
                client.load_extension(f"cogs.{cogname}")
            except:
                await ctx.send("Error occured loading the cog")
                return
            await ctx.send(f"**Reloaded:** {cogname}")
            print(f"{bcolors.OKGREEN}Reloaded cog:{bcolors.ENDC} {cogname}")
        else:
            await ctx.send(f"**Error:** {cogname} does not exist")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")

@client.command()
async def listcogs(ctx):
    if ctx.author.id == OwnerID:
        cogs_list = []
        for cog in os.listdir("./cogs"):
            if not "__" in cog:
                cogs_list.append(cog[:-3])
        nl = "\n"
        await ctx.send(f"**Detected cogs are**:\n{nl.join(cogs_list)}")
    else:
        await ctx.send(f"**Error:** you are not the owner of this bot")


@client.command()
async def logout(ctx):
    if ctx.author.id == OwnerID:
        await client.logout()

load_cogs()
client.run(TOKEN)