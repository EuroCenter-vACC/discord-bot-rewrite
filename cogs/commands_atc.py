import discord
from discord.ext import commands

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
embed_colour = discord.Color.blue()

from EUCLib import ReactionsTracker as RTracker
from EUCLib import BookingHandler
import httpx
import json
import dateutil.parser
import datetime
import sqlite3

class commandsATC(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="application", aliases=['Application', 'apply', 'Apply'])
    async def command_apply(self, ctx):
        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Applying to EUC vACC")
        embed.add_field(name="**Requirements**", value="To Apply for membership in EUC vACC you __**MUST**__ obtain 75 hours on European CTR position on a C1 rating", inline=False)
        embed.add_field(name="**Where to apply?**", value="If you think you meet those requirements, head over [to our website by clicking here](https://vacc-euc.org/apply) and submit your application!", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="eurm", aliases=['EURM'])
    async def command_eurm(self, ctx):
        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Applying for EURM approval")
        embed.add_field(name="**Requirements**", value="To Apply for EURM you __**MUST**__ obtain at least 50 hours on any other EURx position", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="loa", aliases=['LOA'])
    async def command_loa(self, ctx):
        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Our LOAs")
        embed.add_field(name="**EURM**", value="[LOA for EURM (PDF file)](https://files.flying-fox.de/forum/vatsim/eucvacc_permanent/HOS_EURM_V4.1.pdf)", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="sectors", aliases=['Sectors', 'sector', 'Sector', 'sectorfiles', 'Sectorfiles', 'sf', 'SF'])
    async def command_sectors(self, ctx):
        await ctx.message.delete()
        letter_react = {
            "W": "\U0001f1fc",
            "I": "\U0001f1ee",
            "M": "\U0001f1f2",
            "S": "\U0001f1f8",
            "E": "\U0001f1ea",
            "N": "\U0001f1f3",
            "CANCEL": "\U0001f534"
        }
        embed = discord.Embed(color=embed_colour)
        embed.set_author(name="Sector files")
        embed.add_field(name="**Which sector would you like to know more about?**", value="\U0001f1fc - EURW\n\U0001f1ee - EURI\n\U0001f1f2 - EURM\n\U0001f1f8 - EURS\n\U0001f1ea - EURE\n\U0001f1f3 - EURN\n\U0001f534 - Cancel", inline=False)
        choice_msg = await ctx.send(embed=embed)
        res = RTracker().addMessage(int(choice_msg.id), "SF", f"CH1 {ctx.author.id} {ctx.channel.id}")
        if not res == 1:
            await choice_msg.delete()
        for s in letter_react:
            await choice_msg.add_reaction(letter_react[s])
    
    @commands.command(name="online", aliases=['Online'])
    async def command_online(self, ctx):
        conn = sqlite3.connect("./db/globalDB.db")
        c = conn.cursor()
        table_euc = "vatsimeuc"
        c.execute(f"SELECT * FROM {table_euc}")
        found_data = c.fetchall()
        if len(found_data) == 0:
            # return that there is no one online
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name="Current status of EUC sectors")
            embed.add_field(name=f"**Currently 0 sectors online**", value="No sectors of EUC vACC are currently online")
            await ctx.send(embed=embed)
            conn.close()
            return
        else:
            # return information about the currently online people
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name="Current status of EUC sectors")
            online_to_join = []
            for s in found_data:
                c.execute(f"SELECT * FROM users WHERE vatsim_id = ?", (int(s[3]),))
                res = c.fetchone()
                if not res:
                    text = f"**WARNING:** not authorised user with CID **{s[3]}** is currently controlling {s[2]}.\nUptime: {s[5]}"
                    online_to_join.append(text)
                else:
                    if res[1] == 0:
                        discord_obj = f"{res[2]} {res[3]}"
                    else:
                        discord_obj = self.client.get_user(int(res[1]))
                        discord_obj = f"{discord_obj.mention}"
                    text = f"**{s[2]}** is currently controlled by {discord_obj}.\nFrequency: `{s[4]}`\nUptime: {s[5]}"
                    online_to_join.append(text)
            nl = "\n\n"
            embed.add_field(name=f"**Currently {len(found_data)} {'sector' if len(found_data) == 1 else 'sectors'} online**", value=nl.join(online_to_join))
            await ctx.send(embed=embed)
            conn.close()
            return
    
    @commands.command(name="bookings", aliases=['booking', 'Bookings', 'Booking'])
    async def command_bookings(self, ctx):
        resembed = BookingHandler().outputBookings()
        await ctx.send(embed=resembed)
        return


def setup(client):
    client.add_cog(commandsATC(client))