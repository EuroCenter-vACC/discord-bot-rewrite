import discord
from discord.ext import commands

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))
embed_colour = discord.Color.blue()
BotLogChannelID = int(config.get("CHANNELS", "logchannel"))
SupportRole = int(config.get("ROLES", "support"))

import time
from EUCLib import ReactionsTracker as RTracker
from EUCLib import issueTracker as iT

class commandsRank(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    
    @commands.command(name="ticket", aliases=['tickets', 'Ticket', 'Tickets', 'tix'])
    @commands.has_role(SupportRole)
    async def command_tickets(self, ctx, *, args):
        fetch_type = "not defined"
        multiple_args = False
        accepted_dict = {
            'open': 'O',
            'closed': 'C',
            'close': 'Cl',
            'all': 'A',
            'id': 'id',
            'h': 'help',
            'help': 'help',
            'assigned': 'assnd',
            'assign': 'assign',
            'reassign': 'reas',
        }
        if ' ' in args:
            args_list = args.split(' ')
            first_arg = args_list[0]
            second_arg = args_list[1]
            multiple_args = True
        else:
            first_arg = args
            second_arg = ""
        first_arg = first_arg.lower()
        if first_arg in accepted_dict:
            fetch_type = accepted_dict[first_arg]

        if fetch_type == "O":
            response = iT().pullAllOpen()
            await ctx.send(embed=response)
            return
        elif fetch_type == "C":
            response = iT().pullAllClosed()
            await ctx.send(embed=response)
            return
        elif fetch_type == "A":
            response = iT().pullAll()
            await ctx.send(embed=response)
            return
        elif fetch_type == "id":
            if multiple_args:
                second_arg = int(second_arg)
                if isinstance(second_arg, int):
                    response = iT().pullByID(second_arg)
                    await ctx.send(embed=response)
                    return
        elif fetch_type == 'Cl':
            if multiple_args:
                second_arg = int(second_arg)
                if isinstance(second_arg, int):
                    author = ctx.author.id
                    response = iT().closeIssue(second_arg, author)
                    await ctx.send(embed=response)

                    dm_dict = iT().pullIssueUpdate(second_arg)
                    target_user = self.client.get_user(dm_dict[0])
                    embed = dm_dict[1]
                    await target_user.send(embed=embed)

                    channel_id = iT().pullChannelID(int(second_arg))
                    if not channel_id == 0:
                        channel_obj = self.client.get_channel(int(channel_id))
                        messages = await channel_obj.history(limit=100).flatten()
                        all_messages = []
                        for m in messages:
                            if not m.author == self.client.user:
                                if len(m.attachments) > 0:
                                    for a in m.attachments:
                                        a_url = a.proxy_url
                                        a_size = a.size
                                        a_name = a.filename
                                        all_messages.append(f"**{m.author.display_name}:** [{a.filename}]({a.proxy_url}) (*Size: {round(a.size * 0.001, 1)}kB*)")
                                elif len(m.embeds) > 0:
                                    for e in m.embeds:
                                        if not e.author == discord.Embed.Empty:
                                            e_title = e.author.name
                                        elif not e.title == None:
                                            e_title = e.title
                                        else:
                                            e_title = "No title found"
                                        all_messages.append(f"**{m.author.display_name}:** *embed with title* '{e_title}'")
                                else:
                                    all_messages.append(f"**{m.author.display_name}:** {m.content}")
                        RTracker().retireByTopic(f"DRAFT {channel_id}")
                        await channel_obj.delete(reason="Ticket closed")
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
                        
                        for b in range(0,batch_count):
                            embed = discord.Embed(color=embed_colour)  
                            embed.set_author(name=f"Ticket {second_arg} - Message history - {b+1}/{batch_count}")
                            embed.add_field(name="**All messages sent in the ticket channel**", value=nl.join(batches[b]), inline=False)
                            await target_user.send(embed=embed)
                            log_channel = self.client.get_channel(int(BotLogChannelID))
                            await log_channel.send(embed=embed)
                    else:
                        print("No channel deleted")

                    return
        elif fetch_type == "assnd":
            if not multiple_args:
                response = iT().pullAllAssigned()
                await ctx.send(embed=response)
                return
            else:
                if second_arg == "me":
                    mem = ctx.author.id
                    name = ctx.author.display_name
                    response = iT().pullMyAssigned(mem, name)
                    await ctx.send(embed=response)
                    return
                else:
                    mem = second_arg
                    mem = mem.replace("!", "")
                    mem = mem.replace("<", "")
                    mem = mem.replace(">", "")
                    mem = mem.replace("@", "")
                    mem = int(mem)
                    name = self.client.get_user(mem)
                    name = name.display_name
                    response = iT().pullMyAssigned(mem, name)
                    await ctx.send(embed=response)
                    return

        elif fetch_type == "assign":
            if len(args_list) == 3:
                mem = args_list[2]
                mem = mem.replace("!", "")
                mem = mem.replace("<", "")
                mem = mem.replace(">", "")
                mem = mem.replace("@", "")
                mem = int(mem)
                response = iT().assignIssue(second_arg, mem)
                await ctx.send(embed=response)
                dm_dict = iT().pullIssueUpdate(second_arg)
                ticket_channel = iT().pullChannelID(second_arg)
                if not ticket_channel == 0:
                    ticket_channel = self.client.get_channel(int(ticket_channel))
                    target_user = self.client.get_user(dm_dict[0])
                    embed = dm_dict[1]
                    await ticket_channel.send(f"Ticket update - {target_user.mention}")
                    await ticket_channel.send(embed=embed)
                return
            elif len(args_list) == 2:
                mem = ctx.author.id
                response = iT().assignIssue(second_arg, mem)
                await ctx.send(embed=response)
                dm_dict = iT().pullIssueUpdate(second_arg)
                ticket_channel = iT().pullChannelID(second_arg)
                if not ticket_channel == 0:
                    ticket_channel = self.client.get_channel(int(ticket_channel))
                    target_user = self.client.get_user(dm_dict[0])
                    embed = dm_dict[1]
                    await ticket_channel.send(f"Ticket update - {target_user.mention}")
                    await ticket_channel.send(embed=embed)
                return
        
        elif fetch_type == "reas":
            if len(args_list) == 3:
                mem = args_list[2]
                mem = mem.replace("!", "")
                mem = mem.replace("<", "")
                mem = mem.replace(">", "")
                mem = mem.replace("@", "")
                mem = int(mem)
                response = iT().reassignIssue(second_arg, mem)
                await ctx.send(embed=response)
                dm_dict = iT().pullIssueUpdate(second_arg)
                ticket_channel = iT().pullChannelID(second_arg)
                if not ticket_channel == 0:
                    ticket_channel = self.client.get_channel(int(ticket_channel))
                    target_user = self.client.get_user(dm_dict[0])
                    embed = dm_dict[1]
                    await ticket_channel.send(f"Ticket update - {target_user.mention}")
                    await ticket_channel.send(embed=embed)
                return
            elif len(args_list) == 2:
                mem = ctx.author.id
                response = iT().reassignIssue(second_arg, mem)
                await ctx.send(embed=response)
                dm_dict = iT().pullIssueUpdate(second_arg)
                ticket_channel = iT().pullChannelID(second_arg)
                if not ticket_channel == 0:
                    ticket_channel = self.client.get_channel(int(ticket_channel))
                    target_user = self.client.get_user(dm_dict[0])
                    embed = dm_dict[1]
                    await ticket_channel.send(f"Ticket update - {target_user.mention}")
                    await ticket_channel.send(embed=embed)
                return
                

        elif fetch_type == 'help':
            message_text = f"**The following options are available for this command:**\n`!ticket open` displays all open issues\n`!ticket closed` displays all closed issues\n`!ticket all` displays ALL issues"
            message_text2 = f"**You can also view issues by id, or close an issue.**\n`!ticket id 5` will display the issue of ID 5\n`!ticket close 5` will close the issue of ID 5"
            message_text3 = f"**On any new ticket, you must assign the ticket to a staff member.**\n`!ticket assign 5` will assign ticket #5 to yourself\n`!ticket assign 5 @Baguette` will assign ticket #5 to Baguette"
            message_text4 = f"**You can also reassign an already assign ticket.**\n`!ticket reassign 9` will reassign ticket #9 to yourself\n`!ticket reassign 9 @Baguette` will reassign ticket #9 to Baguette"
            await ctx.send(message_text)
            await ctx.send(message_text2)
            await ctx.send(message_text3)
            await ctx.send(message_text4)
            return
        else:
            await ctx.send("This command is unknown.")
        


def setup(client):
    client.add_cog(commandsRank(client))