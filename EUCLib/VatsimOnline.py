import sqlite3
import time
import os
import json
import httpx
import dateutil.parser
import datetime

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")

from EUCLib import GlobalDatabase

class VatsimData():
    def __init__(self):
        self.global_db = "./db/globalDB.db"
        self.db_path = "./db"
        self.table = "vatsimeuc"
        GlobalDatabase().selfCheck()
        self.gconn = sqlite3.connect(self.global_db)
        self.gc = self.gconn.cursor()
        self.gc.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (self.table,))
        if not self.gc.fetchone()[0] == 1:
            self.__buildVatsimTable()
        
        self.vatsim_url = config.get('GENERAL', 'vatsimUrl')
        
    def __buildVatsimTable(self):
        query = f"""CREATE TABLE {self.table} (
            status text,
            callsign text,
            sector text,
            vatsim_id integer,
            frequency text,
            time_online text,
            timestamp text
        )"""
        self.gc.execute(query)
        self.gconn.commit()
        GlobalDatabase().logEntry("New table", f"Created table '{self.table}'")
        return
    
    def retrieve(self):
        reqRaw = httpx.get(self.vatsim_url)
        jsondata = json.loads(reqRaw.text)
        target_list = ["EURW", "EURI", "EURN", "EURE", "EURS", "EURM"]
        found_data = []
        for c in jsondata['clients']:
            if c['callsign'][:4] in target_list:
                try:
                    sector = c['callsign'].replace("_FSS", "")
                except:
                    sector = c['callsign'].replace("_CTR", "")
                tim2 = dateutil.parser.isoparse(c['time_logon'])
                delta = datetime.datetime.utcnow() - datetime.datetime.replace(tim2, tzinfo=None)
                seconds = delta.seconds
                hours = seconds // 3600
                minutes = (seconds // 60) - (hours * 60)
                time_online = f"Online for {hours} {'hour' if hours==1 else 'hours'} and {minutes} {'minute' if minutes==1 else 'minutes'}"
                data = {
                    "callsign": c['callsign'],
                    "sector": sector,
                    "vatsim_id": c['cid'],
                    "frequency": c['frequency'],
                    "time_online": time_online
                }
                found_data.append(data)
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        current_date = time.strftime("%Y-%m-%d", t)
        timestamp = f"{current_date} {current_time}"
        query = f"SELECT * FROM {self.table}"
        self.gc.execute(query)
        result = self.gc.fetchall()
        if len(result) == 0:
            query = f"INSERT INTO {self.table} VALUES(?, ?, ?, ?, ?, ?, ?)"
            for v in found_data:
                values = ("current", v['callsign'], v['sector'], int(v['vatsim_id']), v['frequency'], v['time_online'], timestamp)
                self.gc.execute(query, values)
                self.gconn.commit()
        else:
            query = f"DELETE FROM {self.table} WHERE status = 'current'"
            self.gc.execute(query)
            self.gconn.commit()
            query = f"INSERT INTO {self.table} VALUES(?, ?, ?, ?, ?, ?, ?)"
            for v in found_data:
                values = ("current", v['callsign'], v['sector'], int(v['vatsim_id']), v['frequency'], v['time_online'], timestamp)
                self.gc.execute(query, values)
                self.gconn.commit()
        
        self.gconn.close()

"""
status text,
callsign text,
sector text,
vatsim_id integer,
frequency text,
time_online text,
timestamp text
"""