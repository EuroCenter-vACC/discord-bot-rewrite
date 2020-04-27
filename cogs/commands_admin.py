import discord
from discord.ext import commands

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
nav = config.get("USERS", "nav_list").split(", ")
server_id = int(config.get("GENERAL", "server_id"))

class commandsAdmin(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.guild = self.client.get_guild(server_id)

    @commands.command(name="update", aliases=['Update', 'UPDATE'])
    async def update(self, ctx, *, args):
        if ctx.author.id in nav:
            pass
        else:
            await ctx.send("You are not allowed to use this command")
    
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def command_clear(self, ctx, amount=1):
        amount += 1
        await ctx.channel.purge(limit=amount)

def setup(client):
    client.add_cog(commandsAdmin(client))