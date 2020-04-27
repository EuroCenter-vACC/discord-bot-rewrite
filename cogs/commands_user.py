import discord
from discord.ext import commands

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
bot_prefix = config.get("GENERAL", "prefix")
embed_colour = discord.Color.blue()

import sqlite3

class commandsUser(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="userinfo", aliases=['Userinfo'])
    async def command_userinfo(self, ctx, user : discord.Member = None): # https://cert.vatsim.net/cert/vatsimnet/idstatus.php?cid=1401513
        user_db = "./db/globalDB.db"
        table_name = "users"

        conn = sqlite3.connect(user_db)
        c = conn.cursor()

        if user == None:
            target_id = ctx.author.id
            target_obj = ctx.author
        else:
            target_id = user.id
            target_obj = user
        c.execute(f"SELECt * FROM {table_name} WHERE discord_id = ?", (int(target_id),))
        result = c.fetchone()
        if not result:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"User information for {target_obj.display_name}")
            embed.add_field(name="**ERROR**", value=f"{target_obj.mention} did not link their discord account to their EUC vACC account.", inline=False)
            embed.add_field(name="**How do I link my discord?**", value=f"Log into [the EUC website](https://www.vacc-euc.org) and go to your profile page.\nUnder *Personal Details*, follow the steps to link your discord.\n\nIt can take up to 5 minutes for the bot to synchronise your data.", inline=False)
            await ctx.send(embed=embed)
        else:
            f_name = result[2]
            l_name = result[3]
            vatsim_id = result[0]
            vatsim_rating = result[4]
            division_name = result[8]
            subdivision_name = result[9]
            eurw_rank = result[10]
            euri_rank = result[12]
            eurn_rank = result[14]
            eure_rank = result[16]
            eurs_rank = result[18]
            eurm_rank = result[20]
            
            division_text = f"**Division:** {division_name} | {subdivision_name}"
            if subdivision_name == None:
                division_text = f"**Division:** {division_name}"

            sect_conv = {
                0: "\U0000274c",
                1: "\U00002705",
                2: "\U00002705 & \U0001f1f2"
            }
            sect_key = "Key: \U0000274c = not approved, \U00002705 = approved, \U0001f1f2 = mentor"

            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"User information for {target_obj.display_name}")
            embed.add_field(name="**Profile**", value=f"**Name:** {f_name} {l_name} - {target_obj.mention}\n**Vatsim ID and rating:** {vatsim_id} | {vatsim_rating}\n{division_text}", inline=False)
            embed.add_field(name="**EUC sector authorisations**", value=f"**EURW:** {sect_conv[int(eurw_rank)]}\n**EURI:** {sect_conv[int(euri_rank)]}\n**EURN:** {sect_conv[int(eurn_rank)]}\n**EURE:** {sect_conv[int(eure_rank)]}\n**EURS:** {sect_conv[int(eurs_rank)]}\n**EURM:** {sect_conv[int(eurm_rank)]}\n\n{sect_key}", inline=False)
            embed.add_field(name="**LINKS**", value=f"[Vatsim statistics page](https://stats.vatsim.net/search_id.php?id={vatsim_id})", inline=False)
            embed.set_footer(text="Generated automatically from www.vacc-euc.org website data")
            await ctx.send(embed=embed)
        
        conn.close()




def setup(client):
    client.add_cog(commandsUser(client))