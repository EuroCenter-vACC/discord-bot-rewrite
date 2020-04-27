import sqlite3
import multiprocessing

from multiprocessing import Process

from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")
vatsim_db_looptimer = int(config.get("LOOPTIMERS", "vatsim_db"))

from EUCLib import VatsimData
import time
import datetime

def updateVatsimDatabase(looptimer):
    crashed = False
    while not crashed:
        try:
            start = time.time()
            VatsimData().retrieve()
            end = time.time()
            elapsed = end - start
            print(f"It took {round(elapsed, 2)} seconds to update the local vatsim data DB.\n")
            time.sleep(looptimer)
        except Exception as e:
            errortext = f"Vatsim database updater failed at {datetime.datetime.utcnow()}\nCause {e}"
            with open("bgerrorlog.txt", "w") as f:
                print(errortext, file=f)
            print(errortext)
            crashed = True


if __name__ == "__main__":
    VatsimDatabaseProcess = Process(target=updateVatsimDatabase, args=[vatsim_db_looptimer])

    VatsimDatabaseProcess.start()