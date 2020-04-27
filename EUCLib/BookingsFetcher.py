import sqlite3
import os
import time
import mysql.connector
import discord

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))

db_host = config.get("DATABASE", "host")
db_username = config.get("DATABASE", "username")
db_password = config.get("DATABASE", "password")
db_name = config.get("DATABASE", "database_name")

embed_colour = discord.Color.blue()

from EUCLib import GlobalDatabase

class BookingHandler():
    def __init__(self):
        self.db_path = "./db"
        self.db_file = "globalDB.db"
        self.global_db = f"{self.db_path}/{self.db_file}"
        self.table_name = "bookings"

        self.selfCheck()
        self.conn = sqlite3.connect(self.global_db)
        self.c = self.conn.cursor()

    
    def selfCheck(self):
        self.conn = sqlite3.connect(self.global_db)
        self.c = self.conn.cursor()
        self.c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (self.table_name,))
        if not self.c.fetchone()[0] == 1:
            self.__buildUserTable(True)

    def __buildUserTable(self, close = None):
        self.c.execute("""CREATE TABLE bookings (
                    booking_id integer,
                    vatsim_id integer,
                    slot_date text,
                    start_time text,
                    end_time text,
                    sector text,
                    is_training integer,
                    created_at text
                    )""")
        self.conn.commit()
        GlobalDatabase().logEntry("New table", "Created table 'bookings'")
        if close == True:
            self.conn.close()
        return
    
    def tableChecker(self):
        t = time.localtime()
        n_year = int(time.strftime("%Y", t))
        n_month = int(time.strftime("%m", t))
        n_day = int(time.strftime("%d", t))

        conn_euc = mysql.connector.connect(
            host=str(db_host),
            user=str(db_username),
            password=str(db_password),
            database=str(db_name)
        )
        c_euc = conn_euc.cursor()
        
        query = f"SELECT * FROM bookings ORDER BY created_at DESC"
        c_euc.execute(query)
        result = c_euc.fetchall()
        for row in result:
            booking_date = row[3].split(".")
            b_day = int(booking_date[0])
            b_month = int(booking_date[1])
            b_year = int(booking_date[2])
            if b_year >= n_year and b_month >= n_month and b_day >= n_day:
                self.c.execute(f"SELECT * FROM {self.table_name} WHERE booking_id = ?", (int(row[0]),))
                checkresult = self.c.fetchall()
                if len(checkresult) == 0:
                    self.c.execute(f"INSERT INTO {self.table_name} VALUES(?, ?, ?, ?, ?, ?, ?, ?)", (int(row[0]), int(row[2]), str(row[3]), str(row[5]), str(row[6]), str(row[8]), int(row[7]), str(row[9]),))
                    self.conn.commit()
                    print("Insert the booking")
                    print(f"Booking by {row[2]} for {row[8]} - Date: {row[3]} | {row[4]}")
                else:
                    print("Already in the table")         
        self.conn.close()       
        conn_euc.close()

    def outputBookings(self):
        booking_data = []
        nl ="\n"
        self.c.execute(f"SELECT * FROM {self.table_name}")
        allbookings = self.c.fetchall()
        if not len(allbookings) == 0:
            for b in allbookings:
                self.c.execute(f"SELECT * FROM users WHERE vatsim_id = ?", (int(b[1]),))
                userdata = self.c.fetchone()
                if userdata[1] == 0:
                    user_name = f"{userdata[2]} {userdata[3]}"
                else:
                    user_name = f"<@{userdata[1]}>"
                
                text = f"**{b[5]}** - **{b[2]}**\nBooked by: {user_name}\nTimes: {b[3]} - {b[4]} {f'{nl}*Training session*' if b[6] == 1 else ''}\n"
                booking_data.append(text)
            
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name="EUC vACC Bookings")
            embed.add_field(name="Results", value=nl.join(booking_data))
            self.conn.close()
            return embed
        else:
            embed = discord.Embed(color=embed_colour)
            embed.set_author(name="EUC vACC Bookings")
            embed.add_field(name="Results", value="There are currently no bookings on the website.")
            self.conn.close()
            return embed
                

    def delOldBookings(self):
        t = time.localtime()
        n_year = int(time.strftime("%Y", t))
        n_month = int(time.strftime("%m", t))
        n_day = int(time.strftime("%d", t))
        
        self.c.execute(f"SELECT * FROM {self.table_name}")
        result = self.c.fetchall()
        if len(result) == 0:
            print("No bookings.")
        else:
            for row in result:
                booking_id = int(row[0])
                booking_date = row[2].split(".")
                b_day = int(booking_date[0])
                b_month = int(booking_date[1])
                b_year = int(booking_date[2])

                if b_year <= n_year and b_month <= n_month and b_day < n_day:
                    self.c.execute(f"DELETE FROM {self.table_name} WHERE booking_id = ?", (int(booking_id),))
                    self.conn.commit()
                elif b_year <= n_year and b_month < n_month and b_day > n_day:
                    self.c.execute(f"DELETE FROM {self.table_name} WHERE booking_id = ?", (int(booking_id),))
                    self.conn.commit()
                else:
                    pass
        self.conn.close()