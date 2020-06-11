import discord
from discord.ext import commands

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
bot_prefix = config.get("GENERAL", "prefix")
embed_colour = discord.Color.blue()

import sqlite3

class commandsGeneral(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="help", aliases=['Help', 'HELP'])
    async def command_help(self, ctx):
        embed = discord.Embed(title="Help", description="Here are the things I can do", color=embed_colour)
        embed.add_field(name="**userinfo**", value=f"Gives information about you, or another user\nUsage: `{bot_prefix}userinfo <optional: tag a user>`", inline=True)
        embed.add_field(name="**sectors**", value=f"Gives information about all EUC vACC sectors\nUsage: `{bot_prefix}sectors` or `{bot_prefix}sf` or `{bot_prefix}sectorfiles`", inline=True)
        embed.add_field(name="**sectorbuddy**", value=f"Gives the current sector buddies\nUsage: `{bot_prefix}sectorbuddy` or `{bot_prefix}sb`", inline=True)
        embed.add_field(name="**online**", value=f"Gives all currently online EUC sectors\nUsage: `{bot_prefix}online`", inline=True)
        embed.add_field(name="**bookings**", value=f"Gives all upcoming bookings on EUC sectors\nUsage: `{bot_prefix}bookings`", inline=True)
        embed.add_field(name="**links**", value=f"Gives important links\nUsage: `{bot_prefix}links`", inline=True)
        embed.add_field(name="**contact**", value=f"Gives options to contact the vACC staff\nUsage: `{bot_prefix}contact`", inline=True)
        embed.add_field(name="**applying**", value=f"Explains how to apply\nUsage: `{bot_prefix}application` or `{bot_prefix}apply`", inline=True)
        embed.add_field(name="**EURM**", value=f"Explains how to become EURM Maastricht authorised controller\nUsage: `{bot_prefix}eurm`", inline=True)
        embed.add_field(name="**LOAs**", value=f"Gives available LOA documents\nUsage: `{bot_prefix}loa`", inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name="modhelp", aliases=['Modhelp'])
    async def command_mod_help(self, ctx):
        embed = discord.Embed(title="Moderation commands", description="Here are the things I can do for you when you are staff", color=embed_colour)
        embed.add_field(name="**clear**", value=f"Clears X number of messages in the channel it is used in\nUsage: `{bot_prefix}clear <number of messages to erase>`", inline=True)
        embed.add_field(name="**tickets**", value=f"Handle tickets\nUsage: `{bot_prefix}tickets help` for more information.", inline=True)
        embed.add_field(name="**update**", value=f"Allows staff to post updates (WIP)\nUsage: `{bot_prefix}update <update message>`", inline=True)
        embed.add_field(name="**rank**", value=f"Allows staff to change authorised sectors of a user directly from discord (WIP)\nUsage: `{bot_prefix}rank <user to update the sector authorisation of>`", inline=True)
        await ctx.send(embed=embed)
    
    @commands.command(name="adminhelp", aliases=['Adminhelp'])
    async def command_admin_help(self, ctx):
        embed = discord.Embed(title="Administrator commands", description="Here are the things I can do for you when you are a server admin", color=embed_colour)
        embed.add_field(name="**status**", value=f"Gives a status of currently running background tasks\nUsage: `{bot_prefix}status`", inline=True)
        embed.add_field(name="**start**", value=f"Starts a specified background task\nUsage: `{bot_prefix}start <background task to start>`", inline=True)
        embed.add_field(name="**stop**", value=f"Stops a specified background task\nUsage: `{bot_prefix}stop <background task to stop>`", inline=True)
        embed.add_field(name="**reboot**", value=f"Reboots a specified background task\nUsage: `{bot_prefix}reboot <background task to reboot>`", inline=True)
        embed.add_field(name="**listcogs**", value=f"Lists available cogs\nUsage: `{bot_prefix}listcogs`", inline=True)
        embed.add_field(name="**load**", value=f"Loads a specified cog\nUsage: `{bot_prefix}load <name of cog to load>`", inline=True)
        embed.add_field(name="**unload**", value=f"Unloads a specified cog\nUsage: `{bot_prefix}unload <name of cog to unload>`", inline=True)
        embed.add_field(name="**reload**", value=f"Reloads a specified cog\nUsage: `{bot_prefix}reload <name of cog to reload>`", inline=True)
        embed.add_field(name="**logout**", value=f"Disconnects the bot\nUsage: `{bot_prefix}logout`", inline=True)
        await ctx.send(embed=embed)
        

    @commands.command(name="contact", aliases=['Contact', 'CONTACT'])
    async def command_contact(self, ctx):
        text = "You can contact the EUC vACC staff in two ways:\n- via discord PMs\n- via emails ([click here for a list of emails](https://vacc-euc.org/staff))."
        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Contact")
        embed.add_field(name="EUC Staff Contact Information", value=text)
        await ctx.send(embed=embed)

    @commands.command(name="links", aliases=['Links', 'link', 'Link'])
    async def command_useful_links(self, ctx):
        text = "- [Our main website](https://vacc-euc.org)\n- [Our forum](https://forum.vacc-euc.org)"
        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Links")
        embed.add_field(name="Links to our main webpages", value=text)
        await ctx.send(embed=embed)
        pass # forum and website links

    @commands.command(name='sectorbuddy', aliases=['sb', 'SB'])
    async def command_sb(self, ctx):
        conn = sqlite3.connect("./db/globalDB.db")
        c = conn.cursor()
        table_name = "sectorbuddies"

        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Our sector buddies")

        c.execute(f"SELECT * FROM {table_name}")
        outp = c.fetchall()

        sectors = ["EURW", "EURI", "EURN", "EURE", "EURS", "EURM"]
        nl = "\n"
        for s in sectors:
            s_buddy_list = []
            for b in outp:
                b_sectors = b[4].split("; ")
                if s in b_sectors:
                    if not b[1] == 0:
                        usr_obj = self.client.get_user(int(b[1]))
                        name_to_add = f"{usr_obj.mention}"
                        s_buddy_list.append(name_to_add)
                    else:
                        name_to_add = f"{b[2]} {b[3]}"
                        s_buddy_list.append(name_to_add)
            embed.add_field(name=f"{s} sector buddies", value=nl.join(s_buddy_list), inline=True)


        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(commandsGeneral(client))