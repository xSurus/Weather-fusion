from sqlite3 import *
from typing import Union, List
import logging
import datetime


class RainDB:
    db: Union[None, str]

    con: Union[None, Connection]
    cur: Union[None, Cursor]

    logger: logging.Logger

    def __init__(self, db: str):
        self.logger = logging.getLogger(__name__)
        self.db = db
        self.con = None
        self.cur = None

        self.connect()

    def connect(self):
        self.con = connect(self.db)
        self.cur = self.con.cursor()

    def cleanup(self):
        self.con.commit()
        self.con.close()

        self.db = None
        self.con = None
        self.cur = None

    def debug_execute(self, stmt: str):
        """
        Debug the sql statement that went wrong by printing it out.
        """
        try:
            self.cur.execute(stmt)
        except Exception as e:
            self.logger.error(f"Failed to execute:", stmt, e)
            raise e

    def create_tables(self):
        """
        Create Database Tables
        """
        ndt = datetime.datetime.now() - datetime.timedelta(days=1)
        dt = datetime.datetime(ndt.year, ndt.month, ndt.day, 0, 0, 0)
        dts = dt.strftime("%Y-%m-%d %H:%M:%S")

        self.debug_execute("CREATE TABLE IF NOT EXISTS meteo_measure_data (key INTEGER PRIMARY KEY, dt TEXT, name TEXT)")
        self.debug_execute("SELECT key FROM meteo_measure_data WHERE name = 'init'")

        # Create init entry if not exists
        if self.cur.fetchone() is None:
            self.debug_execute(f"INSERT INTO meteo_measure_data (dt, name) VALUES ('{dts}', 'init')")

    def get_last_entry_radar(self) -> datetime.datetime:
        """
        Get the last entry in the table
        """
        self.debug_execute("SELECT MAX(dt) FROM meteo_measure_data WHERE name IN ('radar', 'init')")
        return datetime.datetime.strptime("%Y-%m-%d %H:%M:%S", self.cur.fetchone()[0])

    def insert_entry(self, dt: datetime.datetime, name: str):
        """
        Insert a new entry into the table
        """
        dts = dt.strftime("%Y-%m-%d %H:%M:%S")
        assert name in ["radar", "prediction"], "name must be radar or prediction"

        self.debug_execute(f"INSERT INTO meteo_measure_data (dt, name) VALUES ('{dts}', '{name}')")