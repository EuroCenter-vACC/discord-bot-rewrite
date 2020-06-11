import discord
from discord.ext import commands, tasks
from discord.utils import get

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))
botcommandsChannelID = int(config.get('CHANNELS', 'botcommands'))
OwnerID = int(config.get("USERS", "bot_owner"))
adminroleID = int(config.get("ROLES", "server_admin"))

db_host = config.get("DATABASE", "host")
db_username = config.get("DATABASE", "username")
db_password = config.get("DATABASE", "password")
db_name = config.get("DATABASE", "database_name")

ReportChannelID = int(config.get('CHANNELS', 'tickets_submit')) # this is the submit channel
IssuesReportChannelID = int(config.get('CHANNELS', 'tickets_inbox')) # this is the inbox

userdb_looptimer = int(config.get("LOOPTIMERS", "userdb"))
role_updater_looptimer = int(config.get("LOOPTIMERS", "role_updater"))
nickname_updater_looptimer = int(config.get("LOOPTIMERS", "nickname_updater"))
retire_msg_looptimer = int(config.get("LOOPTIMERS", "retire_messages"))
vatsim_db_looptimer = int(config.get("LOOPTIMERS", "vatsim_db"))
rootmsg_looptimer = int(config.get("LOOPTIMERS", "rootmsg"))

import time
import os
import mysql.connector
import sqlite3
from EUCLib import UserDatabase, GlobalDatabase, SectorBuddyDatabase, ReactionsTracker, VatsimData, BookingHandler
from EUCLib import ReactionsTracker as RTracker

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HEADER = '\033[95m'

class backgroundTasks(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.options = {
            'userdb': self.task_userdbUpdater,
            'roleupdater': self.task_roleUpdater,
            'nickupdater': self.task_nicknameUpdater,
            'SBdb': self.task_sectorbuddies,
            'msgRetire': self.task_messageRetire,
            'bookingsDB': self.task_bookingschecker,
            'rootMsg': self.task_rootmessages
        }
        self.options_verbose = {
            'userdb': "Updates bot's local private user database",
            'roleupdater': "Updates the roles of users in the server based on their authorisations",
            'nickupdater': "Updates the nicknames of users in the server to same format",
            'SBdb': "Updates the sector buddy list based on database data",
            'msgRetire': "Retires messages in the Reactions Tracker framework database",
            'bookingsDB': "Retrieves EUC vACC member bookings and removes outdated ones in bot's local database",
            'rootMsg': "Checks on 'ROOT' messages in the server, such as the ticket submit message etc."
        }
    
    @commands.Cog.listener()
    async def on_ready(self):
        global_log_exist = False
        while not global_log_exist:
            if "globalDB.db" in os.listdir("./db"):
                for a in self.options:
                    try:
                        self.options[a].start()
                    except Exception as e:
                        pass
                global_log_exist = True
                
            else:
                print("Global DB not found...")
                GlobalDatabase().selfCheck()
                UserDatabase().selfCheck()
                time.sleep(3)
    
    def __error_embed_maker(self, task_name, error_log):
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        current_date = time.strftime("%d/%m/%Y", t)
        embed = discord.Embed(title="Task failed", description=f"Task '{task_name}' failed at {current_time} {current_date}", color=0x272c88)
        embed.add_field(name=f"**Error log**", value=f"{error_log}", inline=True)
        return embed
    
    @tasks.loop(seconds=userdb_looptimer) # Update User database every X seconds
    async def task_userdbUpdater(self):
        task_name = "User DB updater"
        try: 
            start = time.time()
            UserDatabase().tableChecker()
            end = time.time()
            elapsed = end - start
            print(f"It took {round(elapsed, 2)} seconds to update the local user database.\n")
        except Exception as e:
            log_channel = self.client.get_channel(int(botcommandsChannelID))
            owner_ping = self.client.get_user(OwnerID)
            embed_log = self.__error_embed_maker(task_name, e)
            await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
            self.task_userdbUpdater.cancel()
    
    @tasks.loop(seconds=userdb_looptimer) # Update bookings database every X seconds
    async def task_bookingschecker(self):
        task_name = "EUC Bookings checker"
        try: 
            start = time.time()
            BookingHandler().tableChecker()
            BookingHandler().delOldBookings()
            end = time.time()
            elapsed = end - start
            print(f"It took {round(elapsed, 2)} seconds to update the bookings database.\n")
        except Exception as e:
            log_channel = self.client.get_channel(int(botcommandsChannelID))
            owner_ping = self.client.get_user(OwnerID)
            embed_log = self.__error_embed_maker(task_name, e)
            await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
            self.task_bookingschecker.cancel()
    
    @tasks.loop(seconds=userdb_looptimer) # Update Sector buddy database every X seconds
    async def task_sectorbuddies(self):
        task_name = "Sector Buddy DB updater"
        try: 
            start = time.time()
            SectorBuddyDatabase().tableChecker()
            end = time.time()
            elapsed = end - start
            print(f"It took {round(elapsed, 2)} seconds to update the local sector buddy database.\n")
        except Exception as e:
            log_channel = self.client.get_channel(int(botcommandsChannelID))
            owner_ping = self.client.get_user(OwnerID)
            embed_log = self.__error_embed_maker(task_name, e)
            await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
            self.task_sectorbuddies.cancel()
        
    @tasks.loop(seconds=retire_msg_looptimer) # Retires messages in Reactions Tracker when they are shown as deleted
    async def task_messageRetire(self):
        task_name = "Message Retire RTracker"
        try: 
            start = time.time()
            ReactionsTracker().autoRetireDeleted()
            end = time.time()
            elapsed = end - start
            print(f"It took {round(elapsed, 2)} seconds to check for deleted messages in RTracker.\n")
        except Exception as e:
            log_channel = self.client.get_channel(int(botcommandsChannelID))
            owner_ping = self.client.get_user(OwnerID)
            embed_log = self.__error_embed_maker(task_name, e)
            await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
            self.task_messageRetire.cancel()
    
    @tasks.loop(seconds=rootmsg_looptimer) # Checks on root messages inside the server
    async def task_rootmessages(self):
        task_name = "Root message tracker"
        try: 
            embed = discord.Embed(title="Ticket system", color=0x272c88)
            embed.add_field(name="**How do I submit a ticket?**", value=f"To submit a ticket, simply click on the \U0001f3ab below", inline=False)
            embed.add_field(name="**What happens then?**", value=f"A new channel will be created for you to explain your issue.\nOnce your are done, you will be able to send your ticket and wait for a staff member to take on your request", inline=False)
            res, m_list = RTracker().fetchMessageByType("TICKETS", "ROOT")
            if not res:
                tix_chann_obj = self.client.get_channel(ReportChannelID)
                msg_obj = await tix_chann_obj.send(embed=embed)
                await msg_obj.add_reaction("\U0001f3ab") # adds ticket emoji
                RTracker().addMessage(msg_obj.id, "TICKETS", "ROOT")
            elif res:
                for m in m_list:
                    if m[1] == "ROOT":
                        m_id = int(m[0])
                try:
                    tix_chann_obj = await self.client.fetch_channel(ReportChannelID)
                    msg_obj = await tix_chann_obj.fetch_message(m_id)
                except Exception as e:
                    old_list = []
                    old_list.append(m_id)
                    RTracker().retireMessages(old_list)
                    tix_chann_obj = self.client.get_channel(ReportChannelID)
                    msg_obj = await tix_chann_obj.send(embed=embed)
                    await msg_obj.add_reaction("\U0001f3ab") # adds ticket emoji
                    RTracker().addMessage(msg_obj.id, "TICKETS", "ROOT")
        except Exception as e:
            log_channel = self.client.get_channel(int(botcommandsChannelID))
            owner_ping = self.client.get_user(OwnerID)
            embed_log = self.__error_embed_maker(task_name, e)
            await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
            self.task_rootmessages.cancel()
        
    
    @tasks.loop(seconds=role_updater_looptimer)
    async def task_roleUpdater(self):
        task_name = "User role updater"
        try:
            startTime = time.time()
            guild = self.client.get_guild(server_id)
            users = guild.members

            db_path = "./db/globalDB.db"
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            roleAdmin = get(guild.roles, id=adminroleID)
            roleController = get(guild.roles, id=int(config.get("ROLES", "controller")))
            roleSectorbuddy = get(guild.roles, id=int(config.get("ROLES", "sectorbuddy")))
            roleEurw = get(guild.roles, id=int(config.get("ROLES", "eurw")))
            roleEuri = get(guild.roles, id=int(config.get("ROLES", "euri")))
            roleEurn = get(guild.roles, id=int(config.get("ROLES", "eurn")))
            roleEure = get(guild.roles, id=int(config.get("ROLES", "eure")))
            roleEurs = get(guild.roles, id=int(config.get("ROLES", "eurs")))
            roleEurm = get(guild.roles, id=int(config.get("ROLES", "eurm")))
            roleEurwSB = get(guild.roles, id=int(config.get("ROLES", "eurw_sb")))
            roleEuriSB = get(guild.roles, id=int(config.get("ROLES", "euri_sb")))
            roleEurnSB = get(guild.roles, id=int(config.get("ROLES", "eurn_sb")))
            roleEureSB = get(guild.roles, id=int(config.get("ROLES", "eure_sb")))
            roleEursSB = get(guild.roles, id=int(config.get("ROLES", "eurs_sb")))
            roleEurmSB = get(guild.roles, id=int(config.get("ROLES", "eurm_sb")))

            c.execute("SELECT * FROM users")
            result = c.fetchall()
            for user in users:
                foundUser = False
                for row in result:
                    if not row[1] == 0:
                        userDiscord = int(row[1])
                        if userDiscord == user.id:
                            foundUser == True
                            userName = f"{row[2]} {row[3]}"
                            eurw_rank = int(row[10])
                            euri_rank = int(row[12])
                            eurn_rank = int(row[14])
                            eure_rank = int(row[16])
                            eurs_rank = int(row[18])
                            eurm_rank = int(row[20])

                            user_ranks = []
                            # check for EURW roles
                            if eurw_rank == 0:
                                user_ranks.append("0")
                                if roleEurw in user.roles:
                                    await user.remove_roles(roleEurw)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW in user {userName} erroneous. Removed.")
                                if roleEurwSB in user.roles:
                                    await user.remove_roles(roleEurwSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW SB in user {userName} erroneous. Removed.")

                            elif eurw_rank == 1:
                                user_ranks.append("1")
                                if not roleEurw in user.roles:
                                    await user.add_roles(roleEurw)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW not in user {userName} erroneous. Added.")
                                if roleEurwSB in user.roles:
                                    await user.remove_roles(roleEurwSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW SB in user {userName} erroneous. Removed.")
                            
                            elif eurw_rank == 2:
                                user_ranks.append("2")
                                if roleEurw in user.roles:
                                    await user.remove_roles(roleEurw)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW in user {userName} erroneous. Removed.")
                                if not roleEurwSB in user.roles:
                                    await user.add_roles(roleEurwSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW SB not in user {userName} erroneous. Added.")
                            
                            # check for EURI roles
                            if euri_rank == 0:
                                user_ranks.append("0")
                                if roleEuri in user.roles:
                                    await user.remove_roles(roleEuri)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI in user {userName} erroneous. Removed.")
                                if roleEuriSB in user.roles:
                                    await user.remove_roles(roleEuriSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI SB in user {userName} erroneous. Removed.")

                            elif euri_rank == 1:
                                user_ranks.append("1")
                                if not roleEuri in user.roles:
                                    await user.add_roles(roleEuri)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI not in user {userName} erroneous. Added.")
                                if roleEuriSB in user.roles:
                                    await user.remove_roles(roleEuriSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI SB in user {userName} erroneous. Removed.")
                            
                            elif euri_rank == 2:
                                user_ranks.append("2")
                                if roleEuri in user.roles:
                                    await user.remove_roles(roleEuri)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI in user {userName} erroneous. Removed.")
                                if not roleEuriSB in user.roles:
                                    await user.add_roles(roleEuriSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI SB not in user {userName} erroneous. Added.")
                            
                            # check for EURN roles
                            if eurn_rank == 0:
                                user_ranks.append("0")
                                if roleEurn in user.roles:
                                    await user.remove_roles(roleEurn)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN in user {userName} erroneous. Removed.")
                                if roleEurnSB in user.roles:
                                    await user.remove_roles(roleEurnSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN SB in user {userName} erroneous. Removed.")

                            elif eurn_rank == 1:
                                user_ranks.append("1")
                                if not roleEurn in user.roles:
                                    await user.add_roles(roleEurn)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN not in user {userName} erroneous. Added.")
                                if roleEurnSB in user.roles:
                                    await user.remove_roles(roleEurnSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN SB in user {userName} erroneous. Removed.")
                            
                            elif eurn_rank == 2:
                                user_ranks.append("2")
                                if roleEurn in user.roles:
                                    await user.remove_roles(roleEurn)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN in user {userName} erroneous. Removed.")
                                if not roleEurnSB in user.roles:
                                    await user.add_roles(roleEurnSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN SB not in user {userName} erroneous. Added.")
                            
                            # check for EURE roles
                            if eure_rank == 0:
                                user_ranks.append("0")
                                if roleEure in user.roles:
                                    await user.remove_roles(roleEure)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE in user {userName} erroneous. Removed.")
                                if roleEureSB in user.roles:
                                    await user.remove_roles(roleEureSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE SB in user {userName} erroneous. Removed.")

                            elif eure_rank == 1:
                                user_ranks.append("1")
                                if not roleEure in user.roles:
                                    await user.add_roles(roleEure)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE not in user {userName} erroneous. Added.")
                                if roleEureSB in user.roles:
                                    await user.remove_roles(roleEureSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE SB in user {userName} erroneous. Removed.")
                            
                            elif eure_rank == 2:
                                user_ranks.append("2")
                                if roleEure in user.roles:
                                    await user.remove_roles(roleEure)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE in user {userName} erroneous. Removed.")
                                if not roleEureSB in user.roles:
                                    await user.add_roles(roleEureSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE SB not in user {userName} erroneous. Added.")
                            
                            # check for EURS roles
                            if eurs_rank == 0:
                                user_ranks.append("0")
                                if roleEurs in user.roles:
                                    await user.remove_roles(roleEurs)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS in user {userName} erroneous. Removed.")
                                if roleEursSB in user.roles:
                                    await user.remove_roles(roleEursSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS SB in user {userName} erroneous. Removed.")

                            elif eurs_rank == 1:
                                user_ranks.append("1")
                                if not roleEurs in user.roles:
                                    await user.add_roles(roleEurs)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS not in user {userName} erroneous. Added.")
                                if roleEursSB in user.roles:
                                    await user.remove_roles(roleEursSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS SB in user {userName} erroneous. Removed.")
                            
                            elif eurs_rank == 2:
                                user_ranks.append("2")
                                if roleEurs in user.roles:
                                    await user.remove_roles(roleEurs)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS in user {userName} erroneous. Removed.")
                                if not roleEursSB in user.roles:
                                    await user.add_roles(roleEursSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS SB not in user {userName} erroneous. Added.")
                            
                            # check for EURM roles
                            if eurm_rank == 0:
                                user_ranks.append("0")
                                if roleEurm in user.roles:
                                    await user.remove_roles(roleEurm)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM in user {userName} erroneous. Removed.")
                                if roleEurmSB in user.roles:
                                    await user.remove_roles(roleEurmSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM SB in user {userName} erroneous. Removed.")

                            elif eurm_rank == 1:
                                user_ranks.append("1")
                                if not roleEurm in user.roles:
                                    await user.add_roles(roleEurm)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM not in user {userName} erroneous. Added.")
                                if roleEurmSB in user.roles:
                                    await user.remove_roles(roleEurmSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM SB in user {userName} erroneous. Removed.")
                            
                            elif eurm_rank == 2:
                                user_ranks.append("2")
                                if roleEurm in user.roles:
                                    await user.remove_roles(roleEurm)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM in user {userName} erroneous. Removed.")
                                if not roleEurmSB in user.roles:
                                    await user.add_roles(roleEurmSB)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM SB not in user {userName} erroneous. Added.")
                            
                            if "2" in user_ranks:
                                if not roleController in user.roles:
                                    await user.add_roles(roleController)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role Controller not in user {userName} erroneous. Added.")
                                if not roleSectorbuddy in user.roles:
                                    await user.add_roles(roleSectorbuddy)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role SB not in user {userName} erroneous. Added.")
                            elif "1" in user_ranks:
                                if not roleController in user.roles:
                                    await user.add_roles(roleController)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role Controller not in user {userName} erroneous. Added.")
                                if roleSectorbuddy in user.roles:
                                    await user.remove_roles(roleSectorbuddy)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role SB in user {userName} erroneous. Removed.")
                            elif "0" in user_ranks:
                                if roleController in user.roles:
                                    await user.remove_roles(roleController)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role Controller in user {userName} erroneous. Removed.")
                                if roleSectorbuddy in user.roles:
                                    await user.remove_roles(roleSectorbuddy)
                                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role SB in user {userName} erroneous. Removed.")
                
                if not foundUser:
                    if roleController in user.roles:
                        await user.remove_roles(roleController)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role Controller in user {userName} erroneous. Removed.")
                    
                    if roleSectorbuddy in user.roles:
                        await user.remove_roles(roleSectorbuddy)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role Scetor Buddy in user {userName} erroneous. Removed.")

                    if roleEure in user.roles:
                        await user.remove_roles(roleEure)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE in user {userName} erroneous. Removed.")
                    if roleEureSB in user.roles:
                        await user.remove_roles(roleEureSB)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURE SB in user {userName} erroneous. Removed.")
                    
                    if roleEuri in user.roles:
                        await user.remove_roles(roleEuri)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI in user {userName} erroneous. Removed.")
                    if roleEuriSB in user.roles:
                        await user.remove_roles(roleEuriSB)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURI SB in user {userName} erroneous. Removed.")
                    
                    if roleEurm in user.roles:
                        await user.remove_roles(roleEurm)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM in user {userName} erroneous. Removed.")
                    if roleEurmSB in user.roles:
                        await user.remove_roles(roleEurmSB)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURM SB in user {userName} erroneous. Removed.")

                    if roleEurn in user.roles:
                        await user.remove_roles(roleEurn)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN in user {userName} erroneous. Removed.")
                    if roleEurnSB in user.roles:
                        await user.remove_roles(roleEurnSB)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURN SB in user {userName} erroneous. Removed.")
                    
                    if roleEurs in user.roles:
                        await user.remove_roles(roleEurs)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS in user {userName} erroneous. Removed.")
                    if roleEursSB in user.roles:
                        await user.remove_roles(roleEursSB)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURS SB in user {userName} erroneous. Removed.")
                    
                    if roleEurw in user.roles:
                        await user.remove_roles(roleEurw)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW in user {userName} erroneous. Removed.")
                    if roleEurwSB in user.roles:
                        await user.remove_roles(roleEurwSB)
                        print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} role EURW SB in user {userName} erroneous. Removed.")



                        
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)

            endTime = time.time()
            elapsedTime = endTime - startTime

            loopCompleteMessage = f"\nRole update loop end at {current_time}.\nIt took {round(elapsedTime)} seconds to update roles.\nNext loop in {role_updater_looptimer} seconds.\n"

            print(loopCompleteMessage)



        except Exception as e:
            log_channel = self.client.get_channel(int(botcommandsChannelID))
            owner_ping = self.client.get_user(OwnerID)
            embed_log = self.__error_embed_maker(task_name, e)
            await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
            self.task_roleUpdater.cancel()

    @tasks.loop(seconds=nickname_updater_looptimer)
    async def task_nicknameUpdater(self):
        task_name = "User nickname updater"
        try:
            startTime = time.time()
            guild = self.client.get_guild(server_id)
            users = guild.members

            db_path = "./db/globalDB.db"
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            roleAdmin = get(guild.roles, id=adminroleID)

            c.execute(f"SELECT * FROM users")
            result = c.fetchall()
            for user in users:
                notFound = True
                for row in result:
                    if not row[1] == 0:
                        f_discord_id = int(row[1])
                        if f_discord_id == int(user.id):
                            notFound = False
                            f_name = row[2]
                            l_name = row[3]
                            vatsim_id = row[0]

                            #name_syntax = config.get("USERS", "nickname_syntax")
                            #name_syntax_short = config.get("USERS", "nickname_syntax_short")

                            if not roleAdmin in user.roles:
                                name_syntax = config.get("USERS", "nickname_syntax")
                                name_syntax_short = config.get("USERS", "nickname_syntax_short")
                                syntax = name_syntax.replace("$FNAME", f_name)
                                syntax = syntax.replace("$LNAME", l_name)
                                syntax = syntax.replace("$VATSIMID", str(vatsim_id))
                                if len(syntax) > 32:
                                    syntax = name_syntax_short.replace("$FNAME", f_name)
                                    syntax = syntax.replace("$VATSIMID", str(vatsim_id))
                                if not user.display_name == syntax:
                                    try:
                                        await user.edit(nick=syntax)
                                        print(f"Changed nickname for {f_name} {l_name} to proper format.")
                                    except Exception as e:
                                        print(f"Failed to change nickname for {f_name} {l_name} due to: {e}")
                
                if notFound == True:
                    name = user.name
                    if not roleAdmin in user.roles and not user.bot:
                        if len(name) > 23:
                            name = name[:24]
                        syntax = config.get("USERS", "guest_syntax")
                        syntax = syntax.replace("$NAME", name)
                        if not user.display_name == syntax:
                            try:
                                await user.edit(nick=syntax)
                                print(f"Added guest status for {user.display_name}")
                            except Exception as e:
                                print(f"Failed to change nickname for {user.display_name} due to: {e}")

            conn.close()

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            endTime = time.time()
            elapsedTime = endTime - startTime
            loopCompleteMessage = f"\nNickname edit loop end at {current_time}.\nIt took {round(elapsedTime)} seconds to update nicknames.\nNext loop in {nickname_updater_looptimer} seconds.\n"
            print(loopCompleteMessage)
        except Exception as e:
            log_channel = self.client.get_channel(int(botcommandsChannelID))
            owner_ping = self.client.get_user(OwnerID)
            embed_log = self.__error_embed_maker(task_name, e)
            await log_channel.send(content=f"{owner_ping.mention}", embed=embed_log)
            self.task_nicknameUpdater.cancel()
    
    # Background Task management commands
    @commands.command(name="start", aliases=['START', 'Start'])
    async def start(self, ctx, args):
        if ctx.author.id == OwnerID:
            args = args.split(" ")[0]
            if not args in self.options:
                await ctx.send(f"Option unknown. Choose one of the following: {', '.join(self.options)}")
            else:
                if args in self.options:
                    try:
                        self.options[args].start()
                        await ctx.send(f"Starting task: {args}")
                    except Exception as e:
                        await ctx.send(f"Starting task {args} failed.\nError: {e}")
        else:
            await ctx.send(f"**Error:** you are not the owner of this bot")
        

    @commands.command(name="stop", aliases=['STOP', 'Stop'])
    async def stop(self, ctx, args):
        if ctx.author.id == OwnerID:
            args = args.split(" ")[0]
            if not args in self.options:
                await ctx.send(f"Option unknown. Choose one of the following: {', '.join(self.options)}")
            else:
                if args in self.options:
                    try:
                        self.options[args].cancel()
                        await ctx.send(f"Stopping task: {args}")
                    except Exception as e:
                        await ctx.send(f"Stopping task {args} failed.\nError: {e}")
        else:
            await ctx.send(f"**Error:** you are not the owner of this bot")
        

    @commands.command(name="reboot", aliases=['REBOOT', 'Reboot'])
    async def reboot(self, ctx, args):
        if ctx.author.id == OwnerID:
            args = args.split(" ")[0]
            if not args in self.options:
                await ctx.send(f"Option unknown. Choose one of the following: {', '.join(self.options)}")
            else:
                if args in self.options:
                    try:
                        self.options[args].restart()
                        await ctx.send(f"Rebooting task: {args}")
                    except Exception as e:
                        await ctx.send(f"Rebooting task {args} failed.\nError: {e}")
        else:
            await ctx.send(f"**Error:** you are not the owner of this bot")
        


    @commands.command()
    async def status(self, ctx):
        embed = discord.Embed(title="EUC Bot", description=f"Current status of tasks", color=0x272c88)
        for t in self.options:
            st = self.options[t].get_task().done()
            if st:
                t_st = "**Stopped**"
            elif not st: 
                t_st = "*Running*"
            else:
                t_st = "***Unknown***"
            embed.add_field(name=f"**{t}**", value=f"Name: {t}\nDescription: {self.options_verbose[t]}\nStatus: {t_st}", inline=True)
        await ctx.send(embed=embed)



def setup(client):
    client.add_cog(backgroundTasks(client))