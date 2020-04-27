import sqlite3
import os
import time

class ReactionsTracker():
    def __init__(self):
        self.db_path = "./db"
        self.db_file = "reactionsDB.db"
        self.staff_db = f"{self.db_path}/{self.db_file}"
        self.table_messages = "watchlist"

        self.selfCheck()

        self.conn = sqlite3.connect(self.staff_db)
        self.c = self.conn.cursor()
    
    def selfCheck(self):
        if not self.db_file in os.listdir(self.db_path):
            self.__buildAll()
        else:
            self.__checkTablesExist()

    def __buildAll(self):
        self.__buildWatchlistTable()
    
    def __checkTablesExist(self):
        conn = sqlite3.connect(self.staff_db)
        c = conn.cursor()
        c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (self.table_messages,))
        if not c.fetchone()[0] == 1:
            self.__buildWatchlistTable()
        conn.close()

    def __buildWatchlistTable(self):
        conn = sqlite3.connect(self.staff_db)
        c = conn.cursor()
        c.execute("""CREATE TABLE watchlist (
                        message_id integer,
                        message_type text,
                        type_info text,
                        message_timestamp text,
                        message_status text
                        )""")
        conn.commit()
        print("Reactions Database says: Watchlist table created")
        conn.close()
    
    def addMessage(self, message_id, message_type, type_info):
        query = f"SELECT * FROM {self.table_messages} WHERE message_id = {message_id}"
        self.c.execute(query)
        result = self.c.fetchall()
        if not len(result) == 0:
            return -1
        else:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            current_date = time.strftime("%d/%m/%Y", t)
            timestamp = f"{current_date} {current_time}"
            query = f"INSERT INTO {self.table_messages} VALUES(?, ?, ?, ?, ?)"
            values = (int(message_id), message_type, type_info, timestamp, "VALID")
            self.c.execute(query, values)
            self.conn.commit()
            return 1

    def fetchMessage(self, message_id):
        query = f"SELECT * FROM {self.table_messages} WHERE message_id = {message_id}"
        self.c.execute(query)
        result = self.c.fetchall()
        if len(result) == 0:
            return False, None, None
        else:
            for row in result:
                m_type = row[1]
                m_info = row[2]
            return True, m_type, m_info
    
    def fetchMessageByType(self, message_type, message_info):
        query = f"SELECT * FROM {self.table_messages} WHERE message_type = '{message_type}'"
        self.c.execute(query)
        result = self.c.fetchall()
        if len(result) == 0:
            return False, None
        else:
            found = False
            message_list = []
            for row in result:
                if row[4] == "VALID":
                    if row[2] == message_info:
                        found = True
                        root = [row[0], row[2]]
                        message_list.append(root)
            if not found:
                message_list = None
            return found, message_list


    def autoRetireDeleted(self):
        query = f"SELECT * FROM {self.table_messages} WHERE message_status = 'DELETED'"
        to_delete = []
        self.c.execute(query)
        for r in self.c.fetchall():
            to_delete.append(r[0])
        for d in to_delete:
            query = f"DELETE FROM {self.table_messages} WHERE message_id = {d}"
            self.c.execute(query)
            self.conn.commit()
        self.conn.close()

    def retireMessages(self, old_list=list):
        for m in old_list:
            query = f"UPDATE {self.table_messages} SET message_status = 'DELETED' WHERE message_id = {m}"
            self.c.execute(query)
            self.conn.commit()
        
        self.conn.close()
    
    def retireByTopic(self, topic):
        query = f"UPDATE {self.table_messages} SET message_status = 'DELETED' WHERE type_info = '{topic}'"
        self.c.execute(query)
        self.conn.commit()
        self.conn.close()
