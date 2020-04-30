import discord
from discord.ext import commands
from discord.utils import get

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))

class commandsAdmin(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.command(name="update", aliases=['Update', 'UPDATE'])
    async def update(self, ctx, *, args):
        guild = self.client.get_guild(server_id)
        roleNav = get(guild.roles, id=int(config.get("ROLES", "nav_role")))
        if ctx.channel.id == int(config.get("CHANNELS", "send_updates")):
            if roleNav in ctx.author.roles:
                sfupdate_channel = self.client.get_channel(int(config.get("CHANNELS", "sector_file_update")))
                try:
                    await sfupdate_channel.send(args)
                except Exception as e:
                    await ctx.send(f"Error occured: {e}\nCould not post update")
            else:
                await ctx.send("You are not allowed to use this command")
    
    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def command_clear(self, ctx, amount=1):
        amount += 1
        await ctx.channel.purge(limit=amount)

def setup(client):
    client.add_cog(commandsAdmin(client))