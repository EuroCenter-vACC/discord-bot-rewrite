import discord
from discord.ext import commands

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))
embed_colour = discord.Color.blue()

import time
from EUCLib import ReactionsTracker as RTracker

class commandsRank(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.letter_react = {
            "W": "\U0001f1fc",
            "I": "\U0001f1ee",
            "M": "\U0001f1f2",
            "S": "\U0001f1f8",
            "E": "\U0001f1ea",
            "N": "\U0001f1f3",
            "CANCEL": "\U0001f534"
        }
    
    @commands.command(name="rank")
    async def command_rank(self, ctx, user : discord.Member = None):
        if user == None:
            err_msg = await ctx.send("Please specify a user to edit.")
            time.sleep(1)
            await ctx.channel.purge(limit=2)
            return
        sectors = ["EURW", "EURI", "EURM", "EURS", "EURE", "EURN"]
        sector_type = {
            "W": "EURW"
        }
        auth_type = {
            "atc": "CONTROLLER",
            "sb": "SECTORBUDDY"
        }
        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Edit user accreditation")
        embed.add_field(name=f"Choose one of the following options for {user.display_name}", value="Add or Remove an accreditation\n\U0001f1fc - EURW\n\U0001f1ee - EURI\n\U0001f1f2 - EURM\n\U0001f1f8 - EURS\n\U0001f1ea - EURE\n\U0001f1f3 - EURN\n\U0001f534 - Cancel")
        choice_msg = await ctx.send(embed=embed)
        res = RTracker().addMessage(int(choice_msg.id), "RANK", f"CH1 {user.id}")
        if not res == 1:
            await choice_msg.delete()
        for s in self.letter_react:
            await choice_msg.add_reaction(self.letter_react[s])


def setup(client):
    client.add_cog(commandsRank(client))