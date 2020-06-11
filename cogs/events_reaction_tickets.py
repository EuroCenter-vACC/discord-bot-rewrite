import discord
from discord.ext import commands, tasks
from discord.utils import get

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))
embed_colour = discord.Color.blue()
SupportRole = int(config.get("ROLES", "support"))

ReportChannelID = int(config.get('CHANNELS', 'tickets_submit')) # this is the submit channel
IssuesReportChannelID = int(config.get('CHANNELS', 'tickets_inbox')) # this is the inbox

from EUCLib import ReactionsTracker as RTracker
from EUCLib import issueTracker as iT
import time

class reactionsTickets(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guild = self.client.get_guild(int(config.get('GENERAL', 'server_id')))
        r_user_id = payload.user_id
        r_message_id = payload.message_id
        r_channel_id = payload.channel_id
        if not r_user_id == self.client.user.id:
            msg_source = payload.guild_id
            if not msg_source:
                msg_source = 0
            res, m_type, m_info = RTracker().fetchMessage(r_message_id)
            if not msg_source == 0:
                if m_type == "TICKETS": # Takes care of ticket related messages
                    if m_info == "ROOT": # Watches the root message (ticket creation)
                        new_tix_reaction = "\U0001f3ab"
                        if payload.emoji.name == new_tix_reaction:
                            author_object = self.client.get_user(r_user_id)
                            category_object = self.client.get_channel(int(config.get('CATEGORIES', 'tickets')))
                            overwrites = {
                                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                guild.me: discord.PermissionOverwrite(read_messages=True),
                                guild.get_member(r_user_id): discord.PermissionOverwrite(read_messages=True)
                            }

                            channel = self.client.get_channel(ReportChannelID)
                            member_obj = guild.get_member(r_user_id)
                            tix_msg_obj = await channel.fetch_message(r_message_id)
                            await tix_msg_obj.remove_reaction("\U0001f3ab", member_obj)

                            # This portion creates the ticket channel
                            channel = self.client.get_channel(IssuesReportChannelID)
                            ticket_channel = await guild.create_text_channel(f"Ticket draft", overwrites=overwrites, category=category_object, topic=f"Dedicated channel for ticket #draft - {author_object.display_name}") # creates the ticket channel
                            embed = discord.Embed(color=0x272c88)
                            embed.set_author(name=f"{author_object.display_name} ticket channel")
                            embed.add_field(name="**What do I do now?**", value=f"In this channel, explain as clearly and concisely as possible your issue.", inline=False)
                            embed.add_field(name="**And once I am done?**", value=f"To submit your issue, click on \U00002705 \nTo cancel, click on \U0000274c", inline=False)
                            embed.set_footer(text="This is an automated message. Please wait for a staff member to take on your issue")
                            info_msg = await ticket_channel.send(content=f"{author_object.mention}", embed=embed)
                            RTracker().addMessage(info_msg.id, "TICKETS", f"DRAFT {ticket_channel.id}")
                            await info_msg.add_reaction("\U00002705") # green check mark
                            await info_msg.add_reaction("\U0000274c") # red cross
                        else:
                            member_obj = guild.get_member(r_user_id)
                            channel = self.client.get_channel(ReportChannelID)
                            tix_msg_obj = await channel.fetch_message(r_message_id)
                            await tix_msg_obj.remove_reaction(payload.emoji, member_obj)
                
                    elif "DRAFT" in m_info: # watches the draft control message
                        channel_id = int(m_info.split(" ")[1])
                        react_types = {
                            "\U00002705": "SUBMIT",
                            "\U0000274c": "CANCEL"
                        }
                        res, m_list = RTracker().fetchMessageByType("TICKETS", m_info)
                        for m in m_list:
                            bot_msg_id = m[0]
                        channel_object = self.client.get_channel(channel_id)
                        bot_msg_obj = await channel_object.fetch_message(int(bot_msg_id))
                        if payload.emoji.name in react_types:
                            if react_types[payload.emoji.name] == "CANCEL":
                                old_list = []
                                old_list.append(bot_msg_id)
                                RTracker().retireMessages(old_list)
                                await bot_msg_obj.delete()
                                await channel_object.send(content="Ticket cancelled.")
                                time.sleep(1)
                                await channel_object.delete()
                            
                            elif react_types[payload.emoji.name] == "SUBMIT":
                                bot_obj = guild.get_member(self.client.user.id)
                                member_obj = guild.get_member(r_user_id)
                                # START CREATE LOG OF ISSUE DESCRIPTION
                                messages = await channel_object.history(limit=100).flatten()
                                if len(messages) == 1:
                                    error_msg = await channel_object.send("**Warning** - Please describe your issue in at least one line before submitting.")
                                    time.sleep(2)
                                    await error_msg.delete()
                                    await bot_msg_obj.remove_reaction("\U00002705", member_obj)
                                    return
                                else:
                                    await bot_msg_obj.remove_reaction("\U00002705", member_obj)
                                    await bot_msg_obj.remove_reaction("\U00002705", bot_obj)
                                    await bot_msg_obj.remove_reaction("\U0000274c", bot_obj)
                                    all_messages = []
                                    for m in messages:
                                        if not m.author == self.client.user:
                                            if len(m.attachments) > 0:
                                                for a in m.attachments:
                                                    all_messages.append(f"[{a.filename}]({a.proxy_url}) (*Size: {round(a.size * 0.001, 1)}kB*)")
                                            else:
                                                all_messages.append(f"{m.content}")
                                    nl = "\n"
                                    all_messages = reversed(all_messages)
                                    done_filtering = False
                                    batch_count = 1
                                    batches = []
                                    word_count = 0
                                    while not done_filtering:
                                        batch = []
                                        for m in all_messages:
                                            word_count = word_count + len(str(m))
                                            if not word_count >= 800:
                                                batch.append(m)
                                            else:
                                                batches.append(batch)
                                                word_count = 0
                                                batch_count += 1
                                                batch = []
                                                batch.append(m)
                                        batches.append(batch)
                                        done_filtering = True
                                    issue_content = []
                                    for b in batches:
                                        for m in b:
                                            issue_content.append(m)
                                    tr_id = iT().newIssue("ticket", r_user_id, nl.join(issue_content))
                                    iT().insertNewChannelID(tr_id, channel_object.id) # logs the ID of the new ticket channel
                                    # END CREATE LOG OF ISSUE DESCRIPTION

                                    author = r_user_id
                                    author_object = self.client.get_user(author)
                                    embed = discord.Embed(color=0x272c88)
                                    embed.set_author(name=f"{author_object.display_name} ticket channel")
                                    embed.add_field(name="**Update**", value=f"Your ticket was submitted. Please wait for a staff member to respond", inline=False)
                                    embed.set_footer(text="This is an automated message. Please wait for a staff member to take on your issue")
                                    await bot_msg_obj.edit(embed=embed)
                                    overwrites = {
                                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                                    guild.me: discord.PermissionOverwrite(read_messages=True),
                                    guild.get_member(author): discord.PermissionOverwrite(read_messages=True),
                                    guild.get_role(SupportRole): discord.PermissionOverwrite(read_messages=True)
                                    }
                                    await channel_object.edit(overwrites=overwrites, name=f"Ticket {tr_id}", topic=f"Dedicated channel for ticket #{tr_id} - {author_object.display_name}")
                                    await channel_object.send("A staff member will now take care of your issue as soon as possible.")
                                    
                                    # This portion creates the ticket
                                    issues_channel = self.client.get_channel(IssuesReportChannelID)

                                    support_ping = get(guild.roles, id=SupportRole)
                                    await issues_channel.send(content=f"{support_ping.mention}")
                                    for b in range(0,batch_count):
                                        embed = discord.Embed(color=0x272c88)
                                        embed.set_author(name=f"New ticket {tr_id} - {author_object.display_name} - {b+1}/{batch_count}", url="https://sasva.net")
                                        embed.add_field(name="**Summary of the issue description**", value=nl.join(batches[b]), inline=False)
                                        embed.set_footer(text="Bug to report? Submit a ticket using !ticket")
                                        await issues_channel.send(embed=embed)
                        else:
                            member_obj = guild.get_member(r_user_id)
                            await bot_msg_obj.remove_reaction(payload.emoji, member_obj)


def setup(client):
    client.add_cog(reactionsTickets(client))