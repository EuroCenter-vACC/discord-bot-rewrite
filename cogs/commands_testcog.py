import discord
from discord.ext import commands

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
bot_prefix = config.get("GENERAL", "prefix")
embed_colour = discord.Color.blue()

import sqlite3

class commandsForTesting(commands.Cog):
    
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(commandsForTesting(client))