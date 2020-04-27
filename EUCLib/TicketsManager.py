import discord
import sqlite3
import os
import time

embed_colour = discord.Color.blue()

# limiter variables
w_count_limit = 1200
post_limit = 10

class Issue:
    """Format of an issue"""
    def __init__(self, issue_id, issue_type, issue_type_verbose, author_discord, issue_content, issue_status, issue_creation_timestamp, assigned_staff_discord, issue_closed_timestamp, resolver_staff_discord):
        self.issue_id = issue_id
        self.issue_type = issue_type
        self.issue_type_verbose = issue_type_verbose
        self.author_discord = author_discord
        self.issue_content = issue_content
        self.issue_status = issue_status
        self.issue_creation_timestamp = issue_creation_timestamp
        self.assigned_staff_discord = assigned_staff_discord
        self.issue_closed_timestamp = issue_closed_timestamp
        self.resolver_staff_discord = resolver_staff_discord

    
    @property
    def simpleText(self):
        return f"Issue with ID {self.issue_id} by Discord User {self.author_discord}\nContent: {self.issue_content}\nCurrent status: {self.issue_status}"

    def __repr__(self):
        return "Issue('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(self.issue_id, self.issue_type, self.issue_type_verbose, self.author_discord, self.issue_content, self.issue_status, self.issue_creation_timestamp, self.assigned_staff_discord, self.issue_closed_timestamp, self.resolver_staff_discord)


class issueTracker():
    def __init__(self):
        self.db_path = "./db"
        self.db_file = "issuesDB.db"
        self.issue_db = f"{self.db_path}/{self.db_file}"
        self.accepted_issue_types = ["ticket"]
        self.issue_types_verbose = {
            "ticket" : "Ticket",
        }
        self.table_issues = "issues"
        self.table_channels = "issue_channels"

        self.selfCheck()

        self.conn = sqlite3.connect(self.issue_db)
        self.c = self.conn.cursor()

    def selfCheck(self):
        if not self.db_file in os.listdir(self.db_path):
            self.__buildAll()
        else:
            self.__checkTablesExist()

    def __buildAll(self):
        self.__buildDatabase()
        self.__buildIssueChannelsTable()
    
    def __checkTablesExist(self):
        conn = sqlite3.connect(self.issue_db)
        c = conn.cursor()
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (self.table_issues,))
        if not c.fetchone()[0] == 1:
            self.__buildDatabase()
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (self.table_channels,))
        if not c.fetchone()[0] == 1:
            self.__buildIssueChannelsTable()
        conn.close()


    def __buildDatabase(self):
        conn = sqlite3.connect(self.issue_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE issues (
                        issue_id integer,
                        issue_type text,
                        issue_type_verbose text,
                        author_discord integer,
                        issue_content text,
                        issue_status text,
                        issue_creation_timestamp text,
                        assigned_staff_discord integer,
                        issue_closed_timestamp text,
                        resolver_staff_discord integer
                        )""")
        conn.commit()
        print("Issues Database says: Database created")
    
    def __buildIssueChannelsTable(self):
        conn = sqlite3.connect(self.issue_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE issue_channels (
                        issue_id integer,
                        channel_id integer
                        )""")
        conn.commit()
        print("Issues Database says: Channel table created")


    def __lastIssueID(self):
        last_id = 0
        try:
            self.c.execute("SELECT * FROM issues ORDER BY issue_id DESC LIMIT 1")
            result = self.c.fetchone()
            last_id = result[0]
            return int(last_id)
        except TypeError:
            return last_id
    
    def __closeDatabase(self, commit_or_not):
        """Provide 'True' if you wish to commit before closing, else 'False'"""
        if commit_or_not:
            self.conn.commit()
        self.conn.close()
        return
    
    def __SimpleEmbedBuilder(self, embed_purpose, data_dictionary):
        # This function builds an embed that can be returned to discord by each individual function
        """
        All the arguments are required except for the last two.
        For the last two arguments, the only accepted placeholder is 'NONE'
        """
        for data in data_dictionary:
            if data['issue_status'] == "OPEN":
                status_line = f"This issue is **{data['issue_status']}**"
            elif data['issue_status'] == "ASSIGNED":
                status_line = f"This issue is **ASSIGNED** to <@{data['assigned_staff_discord']}>"
            elif data['issue_status'] == "CLOSED":
                status_line = f"This issue is **{data['issue_status']}**\nClosed by: <@{data['resolver_staff_discord']}>\nTimestamp: {data['issue_closed_timestamp']}"

            embed = discord.Embed(description=f"Created by <@{data['author_discord']}>\nTimestamp: {data['issue_creation_timestamp']}", color=embed_colour)
            embed.set_author(name=embed_purpose)
            embed.add_field(name="**STATUS**", value=status_line, inline=False)
            embed.add_field(name="**CONTENT**", value=data['issue_content'], inline=False)
        
        return embed
    
    def __RepeatEmbedBuilder(self, embed_purpose, data_dictionary):
        # This function builds an embed with n number of lines that can be returned to discord by each individual function
        """
        All the arguments are required except for the last two.
        For the last two arguments, the only accepted placeholder is 'NONE'
        """
        #    0          1             2                    3                4             5           6                          7                       8
        # issue_id, issue_type, issue_type_verbose, author_discord, issue_content, issue_status, issue_creation_timestamp, issue_closed_timestamp, resolver_staff_discord

        embed = discord.Embed(color=embed_colour)
        embed.set_author(name=f"{embed_purpose}")
        for data in data_dictionary:
            if data['issue_status'] == "OPEN":
                status_line = f"This issue is **{data['issue_status']}**"
            elif data['issue_status'] == "ASSIGNED":
                status_line = f"This issue is **ASSIGNED** to <@{data['assigned_staff_discord']}>"
            elif data['issue_status'] == "CLOSED":
                status_line = f"This issue is **{data['issue_status']}**\nClosed by: <@{data['resolver_staff_discord']}>\nTimestamp: {data['issue_closed_timestamp']}"

            embed.add_field(name=f"**Issue type '{data['issue_type_verbose']}' - ID #{data['issue_id']}**", value=f"**Info:**\nOpened by <@{data['author_discord']}> at {data['issue_creation_timestamp']}\n**Status**:\n{status_line}\n**Content**:\n{data['issue_content']}\n", inline=False)

        return embed


    def newIssue(self, issue_type, author_discord, issue_content):
        # This function creates a new issue and assigns it its ID, etc.
        if not issue_type in self.accepted_issue_types:
            raise Exception("Invalid or unkown issue type")
        else:
            issue_verbose = self.issue_types_verbose[issue_type]
            last_issue_id = self.__lastIssueID()
            new_issue_id = last_issue_id + 1

            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            current_date = time.strftime("%Y-%m-%d", t)
            timestamp = f"{current_date} {current_time}"
            
            new_issue = Issue(new_issue_id, issue_type, issue_verbose, author_discord, issue_content, "OPEN", timestamp, "NONE", "NONE", "NONE")

            self.c.execute("INSERT INTO issues VALUES (:issue_id, :issue_type, :issue_type_verbose, :author_discord, :issue_content, :issue_status, :issue_creation_timestamp, :assigned_staff_discord, :issue_closed_timestamp, :resolver_staff_discord)", 
                        {'issue_id': new_issue.issue_id,
                        'issue_type': new_issue.issue_type,
                        'issue_type_verbose': new_issue.issue_type_verbose, 
                        'author_discord': new_issue.author_discord, 
                        'issue_content': new_issue.issue_content, 
                        'issue_status': new_issue.issue_status, 
                        'issue_creation_timestamp': new_issue.issue_creation_timestamp,
                        'assigned_staff_discord': new_issue.assigned_staff_discord,
                        'issue_closed_timestamp': new_issue.issue_closed_timestamp,
                        'resolver_staff_discord': new_issue.resolver_staff_discord})
            
            self.__closeDatabase(True)
            return new_issue.issue_id


    def closeIssue(self, issue_id, resolver_discord_id):
        # This function closes an open issue and assigns the resolver's ID
        self.c.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
        result = self.c.fetchone()
        if not result:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"Issue #{issue_id}")
            embed.add_field(name="**ERROR**", value="This issue does not exist", inline=False)
            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_id=?", (issue_id,))
            for row in self.c.fetchall():
                if row[5] == "CLOSED":
                    embed = discord.Embed(color=embed_colour)
                    embed.set_author(name=f"Issue #{issue_id}")
                    embed.add_field(name="**ERROR**", value=f"This issue was already closed.\n\nResolver: <@{row[9]}>\nTimestamp: {row[8]}", inline=False)
                    self.__closeDatabase(False)
                    return embed
                else:
                    t = time.localtime()
                    current_time = time.strftime("%H:%M:%S", t)
                    current_date = time.strftime("%Y-%m-%d", t)
                    timestamp = f"{current_date} {current_time}"
                    self.c.execute("UPDATE issues SET issue_status = 'CLOSED' where issue_id = ?", (issue_id,))
                    self.conn.commit()
                    self.c.execute("UPDATE issues SET resolver_staff_discord = ? where issue_id = ?", (resolver_discord_id, issue_id,))
                    self.conn.commit()
                    self.c.execute("UPDATE issues SET issue_closed_timestamp = ? where issue_id = ?", (timestamp, issue_id,))
                    self.conn.commit()
                
                    embed = discord.Embed(color=embed_colour)
                    embed.set_author(name=f"Issue #{issue_id}")
                    embed.add_field(name="**ACTION**", value=f"This issue was closed by <@{resolver_discord_id}>", inline=False)

                    self.__closeDatabase(False)
                    return embed
    

    def assignIssue(self, issue_id, assignee_discord_id):
        # This function assigns an issue to a staff member with discord id
        self.c.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
        result = self.c.fetchone()
        if not result:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"Issue #{issue_id}")
            embed.add_field(name="**ERROR**", value="This issue does not exist", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_id=?", (issue_id,))
            for row in self.c.fetchall():
                if row[5] == "ASSIGNED":
                    embed = discord.Embed(color=embed_colour)
                    embed.set_author(name=f"Issue #{issue_id}")
                    embed.add_field(name="**ERROR**", value=f"This issue was already assigned.\n\nAssignee: <@{row[7]}>", inline=False)

                    self.__closeDatabase(False)
                    return embed
                elif row[5] == "CLOSED":
                    embed = discord.Embed(color=embed_colour)
                    embed.set_author(name=f"Issue #{issue_id}")
                    embed.add_field(name="**ERROR**", value=f"This issue is closed.\n\Resolver: <@{row[9]}>", inline=False)

                    self.__closeDatabase(False)
                    return embed
                else:
                    self.c.execute("UPDATE issues SET issue_status = 'ASSIGNED' where issue_id = ?", (issue_id,))
                    self.conn.commit()
                    self.c.execute("UPDATE issues SET assigned_staff_discord = ? where issue_id = ?", (assignee_discord_id, issue_id,))
                    self.conn.commit()
                
                    embed = discord.Embed(color=embed_colour)
                    embed.set_author(name=f"Issue #{issue_id}")
                    embed.add_field(name="**ACTION**", value=f"This issue was assigned to <@{assignee_discord_id}>", inline=False)

                    self.__closeDatabase(False)
                    return embed
    
    def reassignIssue(self, issue_id, assignee_discord_id):
        # This function reassigns an already assigned issue to another staff member with discord id
        self.c.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
        result = self.c.fetchone()
        if not result:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"Issue #{issue_id}")
            embed.add_field(name="**ERROR**", value="This issue does not exist", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_id=?", (issue_id,))
            for row in self.c.fetchall():
                if row[5] == "OPEN":
                    embed = self.assignIssue(issue_id, assignee_discord_id)
                    return embed
                else:
                    self.c.execute("SELECT * FROM issues WHERE issue_id=?", (issue_id,))
                    for row in self.c.fetchall():
                        ex_assignee = row[7]
                    self.c.execute("UPDATE issues SET assigned_staff_discord = ? where issue_id = ?", (assignee_discord_id, issue_id,))
                    self.conn.commit()
                
                    embed = discord.Embed(color=embed_colour)
                    embed.set_author(name=f"Issue #{issue_id}")
                    embed.add_field(name="**ACTION**", value=f"This issue was re-assigned to <@{assignee_discord_id}>\nPreviously assigned to <@{ex_assignee}>", inline=False)

                    self.__closeDatabase(False)
                    return embed

    
    def pullByID(self, issue_id):
        # This function pulls data by its issue_id
        data_dict = []
        self.c.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
        if len(self.c.fetchall()) == 0:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"Issue #{issue_id}")
            embed.add_field(name="**ERROR**", value="This issue does not exist", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
            for row in self.c.fetchall():
                data_in = {
                    'issue_id': row[0],
                    'issue_type': row[1],
                    'issue_type_verbose': row[2],
                    'author_discord': row[3],
                    'issue_content': row[4],
                    'issue_status': row[5],
                    'issue_creation_timestamp': row[6],
                    'assigned_staff_discord': row[7],
                    'issue_closed_timestamp': row[8],
                    'resolver_staff_discord': row[9]
                }
                issue_type_verbose_pass = row[2]
                data_dict.append(data_in)
            self.__closeDatabase(False)
            embed_response = self.__SimpleEmbedBuilder(f"Issue #{issue_id} - {issue_type_verbose_pass}", data_dict)
            return embed_response
    
    def pullAll(self):
        # This function pulls ALL records from the database
        data_dict = []
        self.c.execute("SELECT * FROM issues")
        if len(self.c.fetchall()) == 0:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"All Issues")
            embed.add_field(name="**ERROR**", value="There are no issues on record", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues ORDER BY issue_id DESC")
            limiter = False
            w_count = 0
            count = 0
            for row in self.c.fetchall():
                if not row[5] == "ARCHIVED":
                    if limiter == False and count < post_limit:
                        w_count += len(row[4])
                        if w_count > w_count_limit:
                            limiter = True
                        count += 1
                        data_in = {
                            'issue_id': row[0],
                            'issue_type': row[1],
                            'issue_type_verbose': row[2],
                            'author_discord': row[3],
                            'issue_content': row[4],
                            'issue_status': row[5],
                            'issue_creation_timestamp': row[6],
                            'assigned_staff_discord': row[7],
                            'issue_closed_timestamp': row[8],
                            'resolver_staff_discord': row[9]
                        }
                        data_dict.append(data_in)
                    else:
                        pass
            self.__closeDatabase(False)

            embed_response = self.__RepeatEmbedBuilder("Latest Issues - Unfiltered", data_dict)
            return embed_response
    
    def pullAllOpen(self):
        # This function pulls all OPEN data from the database
        data_dict = []
        self.c.execute("SELECT * FROM issues WHERE issue_status='OPEN'")
        if len(self.c.fetchall()) == 0:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"All Open Issues")
            embed.add_field(name="**ERROR**", value="There are no open issues", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_status='OPEN' ORDER BY issue_id DESC")
            limiter = False
            w_count = 0
            count = 0
            for row in self.c.fetchall():
                if limiter == False and count < post_limit:
                    w_count += len(row[4])
                    if w_count > w_count_limit:
                        limiter = True
                    count += 1
                    data_in = {
                        'issue_id': row[0],
                        'issue_type': row[1],
                        'issue_type_verbose': row[2],
                        'author_discord': row[3],
                        'issue_content': row[4],
                        'issue_status': row[5],
                        'issue_creation_timestamp': row[6],
                        'assigned_staff_discord': row[7],
                        'issue_closed_timestamp': row[8],
                        'resolver_staff_discord': row[9]
                    }
                    data_dict.append(data_in)
                else:
                    pass
            self.__closeDatabase(False)

            embed_response = self.__RepeatEmbedBuilder("Latest Open Issues", data_dict)
            return embed_response
    
    def pullAllClosed(self):
        # This function pulls all CLOSED data from the database
        data_dict = []
        self.c.execute("SELECT * FROM issues WHERE issue_status='CLOSED'")
        if len(self.c.fetchall()) == 0:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"All Closed Issues")
            embed.add_field(name="**ERROR**", value="There are no closed issues", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_status='CLOSED' ORDER BY issue_id DESC")
            limiter = False
            w_count = 0
            count = 0
            for row in self.c.fetchall():
                if limiter == False and count < post_limit:
                    w_count += len(row[4])
                    if w_count > w_count_limit:
                        limiter = True
                    count += 1
                    data_in = {
                        'issue_id': row[0],
                        'issue_type': row[1],
                        'issue_type_verbose': row[2],
                        'author_discord': row[3],
                        'issue_content': row[4],
                        'issue_status': row[5],
                        'issue_creation_timestamp': row[6],
                        'assigned_staff_discord': row[7],
                        'issue_closed_timestamp': row[8],
                        'resolver_staff_discord': row[9]
                    }
                    data_dict.append(data_in)
                else:
                    pass
            self.__closeDatabase(False)

            embed_response = self.__RepeatEmbedBuilder("Latest Closed Issues", data_dict)
            return embed_response
    
    def pullAllAssigned(self):
        # This function pulls all ASSIGNED data from the database
        data_dict = []
        self.c.execute("SELECT * FROM issues WHERE issue_status='ASSIGNED'")
        if len(self.c.fetchall()) == 0:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"All Assigned Issues")
            embed.add_field(name="**ERROR**", value="There are no assigned issues", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_status='ASSIGNED' ORDER BY issue_id DESC")
            limiter = False
            w_count = 0
            count = 0
            for row in self.c.fetchall():
                if limiter == False and count < post_limit:
                    w_count += len(row[4])
                    if w_count > w_count_limit:
                        limiter = True
                    count += 1
                    data_in = {
                        'issue_id': row[0],
                        'issue_type': row[1],
                        'issue_type_verbose': row[2],
                        'author_discord': row[3],
                        'issue_content': row[4],
                        'issue_status': row[5],
                        'issue_creation_timestamp': row[6],
                        'assigned_staff_discord': row[7],
                        'issue_closed_timestamp': row[8],
                        'resolver_staff_discord': row[9]
                    }
                    data_dict.append(data_in)
                else:
                    pass
            self.__closeDatabase(False)

            embed_response = self.__RepeatEmbedBuilder("Latest Assigned Issues", data_dict)
            return embed_response
    

    def pullMyAssigned(self, target_discord, target_name):
        # This function pulls all CLOSED data from the database
        data_dict = []
        self.c.execute("SELECT * FROM issues WHERE issue_status='ASSIGNED'")
        if len(self.c.fetchall()) == 0:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name=f"All Assigned Issues")
            embed.add_field(name="**ERROR**", value=f"<@{target_discord}> has currently no assigned issues", inline=False)

            self.__closeDatabase(False)
            return embed
        else:
            self.c.execute("SELECT * FROM issues WHERE assigned_staff_discord = ? ORDER BY issue_id DESC", (target_discord,))
            result = self.c.fetchall()
            if len(result) == 0:
                embed = discord.Embed(color=embed_colour)
                embed.set_author(name=f"All Assigned Issues")
                embed.add_field(name="**ERROR**", value=f"<@{target_discord}> has currently no assigned issues", inline=False)

                self.__closeDatabase(False)
                return embed
            limiter = False
            w_count = 0
            count = 0
            for row in result:
                if not row[5] == "CLOSED":
                    if limiter == False and count < post_limit:
                        w_count += len(row[4])
                        if w_count > w_count_limit:
                            limiter = True
                        count += 1
                        data_in = {
                            'issue_id': row[0],
                            'issue_type': row[1],
                            'issue_type_verbose': row[2],
                            'author_discord': row[3],
                            'issue_content': row[4],
                            'issue_status': row[5],
                            'issue_creation_timestamp': row[6],
                            'assigned_staff_discord': row[7],
                            'issue_closed_timestamp': row[8],
                            'resolver_staff_discord': row[9]
                        }
                        data_dict.append(data_in)
                    else:
                        pass
            self.__closeDatabase(False)

            embed_response = self.__RepeatEmbedBuilder(f"{target_name}'s Assigned Issues", data_dict)
            return embed_response
    
    def pullIssueUpdate(self, issue_id):
        # This function is invoked when there is an update to a case.
        # It pulls data about the issue and returns a list of values.
        # These values are sent in a DM to the ticket's author.
        data_dict = {'exist': False}
        self.c.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
        if len(self.c.fetchall()) == 0:
            self.__closeDatabase(False)
            return data_dict
        else:
            self.c.execute("SELECT * FROM issues WHERE issue_id = ?", (issue_id,))
            for row in self.c.fetchall():
                data_dict = {
                    'exist': True,
                    'issue_id': row[0],
                    'issue_type': row[1],
                    'issue_type_verbose': row[2],
                    'author_discord': row[3],
                    'issue_content': row[4],
                    'issue_status': row[5],
                    'issue_creation_timestamp': row[6],
                    'assigned_staff_discord': row[7],
                    'issue_closed_timestamp': row[8],
                    'resolver_staff_discord': row[9]
                }
            self.__closeDatabase(False)
            response = self.__issueUpdateEmbedBuilder(issue_id, data_dict)
            return response
    
    def __issueUpdateEmbedBuilder(self, issue_id, dm_dict):
        # This function builds the dm embed to send to the user that needs to be updated
        resp_dict = []
        if dm_dict['exist']:
            dm_text = "ERROR - NoTicketData"
            target_user = dm_dict['author_discord']
            assignee = dm_dict['assigned_staff_discord']
            resolver = dm_dict['resolver_staff_discord']
            issue_status = dm_dict['issue_status']
            if issue_status == "ASSIGNED":
                dm_text = f"Your ticket was **assigned** to <@{assignee}>"
            elif issue_status == "CLOSED":
                dm_text = f"Your ticket was **closed** by <@{resolver}>.\nIf you believe this was an error, please contact the staff."
            
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name="There was an update to your ticket")
            embed.add_field(name=f"**Ticket ID #{issue_id}**", value=dm_text, inline=False)
            
            resp_dict.append(target_user)
            resp_dict.append(embed)
            return resp_dict
    
    def buildIssueChannelsTable(self):
        conn = sqlite3.connect(self.issue_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE issue_channels (
                        issue_id integer,
                        channel_id integer
                        )""")
        conn.commit()
        print("Issues Database says: Channel table created")
        conn.close()
    
    def insertNewChannelID(self, issue_id, channel_id):
        query = "INSERT INTO issue_channels VALUES(?, ?)"
        values = (issue_id, channel_id)
        self.c.execute(query, values)
        self.conn.commit()
        self.conn.close()
        return 1
    
    def pullChannelID(self, issue_id):
        query = f"SELECT * FROM issue_channels WHERE issue_id = {issue_id}"
        self.c.execute(query)
        result = self.c.fetchone()
        if not result:
            return 0
        else:
            return result[1]
        self.conn.close()