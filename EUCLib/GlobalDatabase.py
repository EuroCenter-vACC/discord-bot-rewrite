import os
import sqlite3
import discord
import time

class GlobalDatabase():
    def __init__(self):
        self.db_path = "./db"
        self.db_file = "globalDB.db"
        self.global_db = f"{self.db_path}/{self.db_file}"

        self.selfCheck()
    
    def selfCheck(self):
        if not self.db_file in os.listdir(self.db_path):
            self.__buildGlobalDB(True)

    def __buildGlobalDB(self, close = None):
        conn = sqlite3.connect(self.global_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE global_log (
                    id integer,
                    name text,
                    description text,
                    timestamp text
                    )""")
        conn.commit()
        print("Global Database says: Global Database created")
        self.logEntry("Alpha", "Created database 'GlobalDB'")
        if close == True:
            conn.close()
        return
    
    def __lastLogID(self):
        last_id = 0
        try:
            self.c.execute("SELECT * FROM global_log ORDER BY id DESC LIMIT 1")
            result = self.c.fetchone()
            last_id = result[0]
            return int(last_id)
        except TypeError:
            return last_id

    def logEntry(self, entry_name, entry_descr):
        """
        entry_name is the Name or short name of the entry
        entry_descr is the Description of the entry
        """
        self.conn = sqlite3.connect(self.global_db)
        self.c = self.conn.cursor()
        entry_id = self.__lastLogID()
        entry_id += 1
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        current_date = time.strftime("%Y-%m-%d", t)
        timestamp = f"{current_date} {current_time}"

        query = f"INSERT INTO global_log VALUES(?, ?, ?, ?)"
        values = (entry_id, entry_name, entry_descr, timestamp)
        self.c.execute(query, values)
        self.conn.commit()
        print(f"Global Database says: Entry logged with ID {entry_id}")
        self.conn.close()
        return
