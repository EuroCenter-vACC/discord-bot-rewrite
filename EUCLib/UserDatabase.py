import sqlite3
import os
import time
import mysql.connector

from configparser import ConfigParser
config = ConfigParser()
config.read("config.ini")
server_id = int(config.get("GENERAL", "server_id"))

db_host = config.get("DATABASE", "host")
db_username = config.get("DATABASE", "username")
db_password = config.get("DATABASE", "password")
db_name = config.get("DATABASE", "database_name")

from EUCLib import GlobalDatabase

class UserDatabase():
    def __init__(self):
        self.db_path = "./db"
        self.db_file = "globalDB.db"
        self.global_db = f"{self.db_path}/{self.db_file}"
        self.table_name = "users"

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
        self.c.execute("""CREATE TABLE users (
                    vatsim_id integer,
                    discord_id integer,
                    firstname text,
                    lastname text,
                    vatsim_rating text,
                    region_code text,
                    region_name text,
                    division_code text,
                    division_name text,
                    subdivision_name text,
                    eurw_rank integer,
                    eurw_rank_verbose text,
                    euri_rank integer,
                    euri_rank_verbose text,
                    eurn_rank integer,
                    eurn_rank_verbose text,
                    eure_rank integer,
                    eure_rank_verbose text,
                    eurs_rank integer,
                    eurs_rank_verbose text,
                    eurm_rank integer,
                    eurm_rank_verbose text
                    )""")
        self.conn.commit()
        GlobalDatabase().logEntry("New table", "Created table 'users'")
        if close == True:
            self.conn.close()
        return
    
    def tableChecker(self):
        update_log = []
        conn_euc = mysql.connector.connect(
            host=str(db_host),
            user=str(db_username),
            password=str(db_password),
            database=str(db_name)
            )
        c_euc = conn_euc.cursor()
        
        query = f"SELECT * FROM roster"
        c_euc.execute(query)
        result = c_euc.fetchall()
        for row in result:
            l_query = f"SELECT * FROM users WHERE vatsim_id = ?"
            l_values = (int(row[1]),)
            self.c.execute(l_query, l_values)
            l_result = self.c.fetchone()
            if not l_result:
                vatsim_id = int(row[1])
                n_discord_id = row[2]
                if n_discord_id == None:
                    n_discord_id = 0
                
                m_query = f"SELECT * FROM users WHERE id = {vatsim_id}"
                c_euc.execute(m_query)
                m_record = c_euc.fetchone()
                first_name = m_record[2]
                last_name = m_record[3]
                vatsim_rating = m_record[7]
                region_code = m_record[11]
                region_name = m_record[12]
                div_code = m_record[14]
                div_name = m_record[15]
                subdiv_name = m_record[17]

                new_query = f"INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                new_values = (vatsim_id, n_discord_id, first_name, last_name, vatsim_rating, region_code, region_name, div_code, div_name, subdiv_name, int(row[3]), "EURW", int(row[4]), "EURI", int(row[5]), "EURN", int(row[6]), "EURE", int(row[7]), "EURS", int(row[8]), "EURM",)
                self.c.execute(new_query, new_values)
                self.conn.commit()
                GlobalDatabase().logEntry("Update table 'users'", f"New user added. Name: {first_name} {last_name} | Vatsim ID: {row[1]} | Rating: {vatsim_rating}")
                print(f"New user added. Name: {first_name} {last_name} | Vatsim ID: {row[1]} | Rating: {vatsim_rating}")
            else:
                updated = []
                update_flag = False
                vatsim_id = int(row[1])
                r_discord_id = row[2]
                if r_discord_id == None:
                    r_discord_id = 0
                
                m_query = f"SELECT * FROM users WHERE id = {vatsim_id}"
                c_euc.execute(m_query)
                m_record = c_euc.fetchone()
                r_first_name = m_record[2]
                r_last_name = m_record[3]
                r_vatsim_rating = m_record[7]
                r_region_code = m_record[11]
                r_region_name = m_record[12]
                r_div_code = m_record[14]
                r_div_name = m_record[15]
                r_subdiv_name = m_record[17]
                r_eurw_rank = int(row[3])
                r_euri_rank = int(row[4])
                r_eurn_rank = int(row[5])
                r_eure_rank = int(row[6])
                r_eurs_rank = int(row[7])
                r_eurm_rank = int(row[8])

                self.c.execute("SELECT * FROM users WHERE vatsim_id = ?", (vatsim_id,))
                up_result = self.c.fetchall()
                for lrow in up_result:
                    # check for discord_id update
                    if not int(lrow[1]) == int(r_discord_id):
                        self.c.execute("UPDATE users SET discord_id = ? WHERE vatsim_id = ?", (r_discord_id, vatsim_id,))
                        self.conn.commit()

                    # check for first name update
                    if not str(lrow[2]) == str(r_first_name):
                        old_firstname = lrow[2]
                        update_flag = True
                        self.c.execute("UPDATE users SET firstname = ? WHERE vatsim_id = ?", (r_first_name, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_first_name,
                            'old': old_firstname,
                            'text': f"$USER$ changed their first name.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for last name update
                    if not lrow[3] == r_last_name:
                        old_lastname = lrow[3]
                        update_flag = True
                        self.c.execute("UPDATE users SET lastname = ? WHERE vatsim_id = ?", (r_last_name, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_last_name,
                            'old': old_lastname,
                            'text': f"$USER$ changed their last name.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for vatsim rating update
                    if not lrow[4] == r_vatsim_rating:
                        old_rating = lrow[4]
                        update_flag = True
                        self.c.execute("UPDATE users SET vatsim_rating = ? WHERE vatsim_id = ?", (r_vatsim_rating, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_vatsim_rating,
                            'old': old_rating,
                            'text': f"$USER$ changed their vatsim rating.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for region code update
                    if not lrow[5] == r_region_code:
                        old_region_code = lrow[5]
                        update_flag = True
                        self.c.execute("UPDATE users SET region_code = ? WHERE vatsim_id = ?", (r_region_code, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_region_code,
                            'old': old_region_code,
                            'text': f"$USER$ changed their region code.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for region name update
                    if not lrow[6] == r_region_name:
                        old_region_name = lrow[6]
                        update_flag = True
                        self.c.execute("UPDATE users SET region_name = ? WHERE vatsim_id = ?", (r_region_name, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_region_name,
                            'old': old_region_name,
                            'text': f"$USER$ changed their region name.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for division code update
                    if not lrow[7] == r_div_code:
                        old_div_code = lrow[7]
                        update_flag = True
                        self.c.execute("UPDATE users SET division_code = ? WHERE vatsim_id = ?", (r_div_code, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_div_code,
                            'old': old_div_code,
                            'text': f"$USER$ changed their divison code.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for division name update
                    if not lrow[8] == r_div_name:
                        old_div_name = lrow[8]
                        update_flag = True
                        self.c.execute("UPDATE users SET division_name = ? WHERE vatsim_id = ?", (r_div_name, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_div_name,
                            'old': old_div_name,
                            'text': f"$USER$ changed their division name.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for subdivision name update
                    if not lrow[9] == r_subdiv_name:
                        old_subdiv_name = lrow[9]
                        update_flag = True
                        self.c.execute("UPDATE users SET subdivision_name = ? WHERE vatsim_id = ?", (r_subdiv_name, vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_subdiv_name,
                            'old': old_subdiv_name,
                            'text': f"$USER$ changed their subdivision name.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for EURW rank update
                    if not lrow[10] == int(r_eurw_rank):
                        old_rank = lrow[10]
                        update_flag = True
                        self.c.execute("UPDATE users SET eurw_rank = ? WHERE vatsim_id = ?", (int(r_eurw_rank), vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_eurw_rank,
                            'old': old_rank,
                            'text': f"$USER$ changed their EURW rank.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for EURI rank update
                    if not lrow[12] == int(r_euri_rank):
                        old_rank = lrow[12]
                        update_flag = True
                        self.c.execute("UPDATE users SET euri_rank = ? WHERE vatsim_id = ?", (int(r_euri_rank), vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_euri_rank,
                            'old': old_rank,
                            'text': f"$USER$ changed their EURI rank.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for EURN rank update
                    if not lrow[14] == int(r_eurn_rank):
                        old_rank = lrow[14]
                        update_flag = True
                        self.c.execute("UPDATE users SET eurn_rank = ? WHERE vatsim_id = ?", (int(r_eurn_rank), vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_eurn_rank,
                            'old': old_rank,
                            'text': f"$USER$ changed their EURN rank.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for EURE rank update
                    if not lrow[16] == int(r_eure_rank):
                        old_rank = lrow[16]
                        update_flag = True
                        self.c.execute("UPDATE users SET eure_rank = ? WHERE vatsim_id = ?", (int(r_eure_rank), vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_eure_rank,
                            'old': old_rank,
                            'text': f"$USER$ changed their EURE rank.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for EURS rank update
                    if not lrow[18] == int(r_eurs_rank):
                        old_rank = lrow[18]
                        update_flag = True
                        self.c.execute("UPDATE users SET eurs_rank = ? WHERE vatsim_id = ?", (int(r_eurs_rank), vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_eurs_rank,
                            'old': old_rank,
                            'text': f"$USER$ changed their EURS rank.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)

                    # check for EURM rank update
                    if not lrow[20] == int(r_eurm_rank):
                        old_rank = lrow[20]
                        update_flag = True
                        self.c.execute("UPDATE users SET eurm_rank = ? WHERE vatsim_id = ?", (int(r_eurm_rank), vatsim_id,))
                        self.conn.commit()
                        val_updated = {
                            'new': r_eurm_rank,
                            'old': old_rank,
                            'text': f"$USER$ changed their EURM rank.\nOld: $OLD$ \nNew: $NEW$"
                        }
                        updated.append(val_updated)
                    
                    if update_flag == True:
                        updated_user = {
                            'vatsim_id': vatsim_id,
                            'discord_id': r_discord_id,
                            'update_flag': update_flag,
                            'log_updates': updated
                        }
                        update_log.append(updated_user)

        print(update_log)
        conn_euc.close()
        self.conn.close()
        return update_log