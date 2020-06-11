import discord
from discord.ext import commands
from discord.ext.commands import errors

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
bot_prefix = config.get("GENERAL", "prefix")
log_channel_id = int(config.get("CHANNELS", "logchannel"))

class eventsJoinLeave(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = self.client.get_channel(log_channel_id)
        try:
            await member.send(f'''Welcome to the official EuroCenter Discord, {member.mention}! \n If you're approved on certain sector and that isn't on the website, please message Samy or Jonas.''')
        except:
            print(f"Failed to send DM to {member.name}")
        await log_channel.send(f"{member.name} just joined the server.")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = self.client.get_channel(log_channel_id)
        await log_channel.send(f"{member.name} just left the server.")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        channel = self.client.get_channel(log_channel_id)
        await channel.send(f'{member.name} has been banned from the server.')

def setup(client):
    client.add_cog(eventsJoinLeave(client))