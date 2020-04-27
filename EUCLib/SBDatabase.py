import sqlite3
import os
import time
import mysql.connector

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))

from EUCLib import GlobalDatabase

class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    HEADER = '\033[95m'

class SectorBuddyDatabase():
    def __init__(self):
        self.db_path = "./db"
        self.db_file = "globalDB.db"
        self.global_db = f"{self.db_path}/{self.db_file}"
        self.table_name = "sectorbuddies"
        self.user_table = "users"

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
        self.c.execute(f"CREATE TABLE {self.table_name} (vatsim_id integer, discord_id integer, first_name text, last_name text, sb_sectors text)")
        self.conn.commit()
        GlobalDatabase().logEntry("New table", f"Created table '{self.table_name}'")
        if close == True:
            self.conn.close()
        return
    
    def tableChecker(self):
        check_users = []
        self.c.execute(f"SELECT * FROM {self.user_table}")
        result = self.c.fetchall()
        for row in result:
            vatsim_id = int(row[0])
            discord_id = int(row[1])
            r_first_name = row[2]
            r_last_name = row[3]
            r_eurw_rank = int(row[10])
            r_euri_rank = int(row[12])
            r_eurn_rank = int(row[14])
            r_eure_rank = int(row[16])
            r_eurs_rank = int(row[18])
            r_eurm_rank = int(row[20])
            sb_sector_index = [10, 12, 14, 16, 18, 20]

            sb_sectors = []
            isSB = False
            for s in sb_sector_index:
                if int(row[s]) == 2:
                    isSB = True
                    sb_sectors.append(str(row[s+1]))
            if isSB is True:
                data = {
                    "vatsim_id": int(vatsim_id),
                    "discord_id": int(discord_id),
                    "fname": str(r_first_name),
                    "lname": str(r_last_name),
                    "sectors": "; ".join(sb_sectors)
                }
                check_users.append(data)
        
        for u in check_users:
            self.c.execute(f"SELECT * FROM {self.table_name} WHERE vatsim_id = ?", (u["vatsim_id"],))
            outp = self.c.fetchone()
            if not outp:
                query = f"INSERT INTO {self.table_name} VALUES(?, ?, ?, ?, ?)"
                values = (u['vatsim_id'], u['discord_id'], u['fname'], u['lname'], u['sectors'],)
                self.c.execute(query, values)
                self.conn.commit()
            else:
                if not outp[1] == u['discord_id']:
                    self.c.execute(f"UPDATE {self.table_name} SET discord_id = ? WHERE vatsim_id = ?", (u['discord_id'], u['vatsim_id'],))
                    self.conn.commit()
                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} SB DB updated Discord ID for {u['fname']} {u['lname']}")
                if not outp[2] == u['fname']:
                    self.c.execute(f"UPDATE {self.table_name} SET first_name = ? WHERE vatsim_id = ?", (u['fname'], u['vatsim_id'],))
                    self.conn.commit()
                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} SB DB updated first name for {u['fname']} {u['lname']}")
                if not outp[3] == u['lname']:
                    self.c.execute(f"UPDATE {self.table_name} SET last_name = ? WHERE vatsim_id = ?", (u['lname'], u['vatsim_id'],))
                    self.conn.commit()
                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} SB DB updated last name for {u['fname']} {u['lname']}")
                if not outp[4] == u['sectors']:
                    self.c.execute(f"UPDATE {self.table_name} SET sb_sectors = ? WHERE vatsim_id = ?", (u['sectors'], u['vatsim_id'],))
                    self.conn.commit()
                    print(f"{bcolors.WARNING}UPDATE:{bcolors.ENDC} SB DB updated sector buddy sectors for {u['fname']} {u['lname']}")




        self.conn.close()