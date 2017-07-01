'''
The database is in sqlite3 format and stored at `games.sqlite`
The current format (vTWOWb-1.0) is as follows:

    TABLE games:
    uuid | server | channel | round | status | name
    -----|--------|---------|-------|--------|-----

    TABLE contestants
    uuid | id | status
    -----|----|-------

    TABLE responses
    uuid | round | response | uid
    -----|-------|----------|----

    TABLE prompts
    uuid | round | prompt
    -----|-------|-------

    TABLE votes
    uuid | round | voter | v0 | v1 | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9
    -----|-------|-------|----|----|----|----|----|----|----|----|----|----
'''

import sqlite3


class Game_Manager:
    PATH = 'games.sqlite'

    def __init__(self, bot):
        self._database = sqlite3.connect(self.PATH)
        self.bot = bot
        
        if not self._check_table_exists("games"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE games(
                    uuid BLOB PRIMARY KEY, server INTEGER, channel INTEGER,
                    round INTEGER, status TEXT, name TEXT)""")
            self._database.commit()
        if not self._check_table_exists("contestants"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE contestants(
                    uuid BLOB PRIMARY KEY, id INTEGER, status TEXT)""")
            self._database.commit()
        if not self._check_table_exists("responses"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE responses(
                    uuid BLOB PRIMARY KEY, round INTEGER, response TEXT, uid INTEGER)""")
            self._database.commit()
        if not self._check_table_exists("prompts"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE prompts(
                    uuid BLOB PRIMARY KEY, round INTEGER, prompt TEXT)""")
            self._database.commit()
        if not self._check_table_exists("votes"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE votes(
                    uuid BLOB PRIMARY KEY, round INTEGER, votes INTEGER,
                    v0 INTEGER, v1 INTEGER, v2 INTEGER, v3 INTEGER, v4 INTEGER,
                    v5 INTEGER, v6 INTEGER, v7 INTEGER, v8 INTEGER, v9 INTEGER)""")
            self._database.commit()

    def _check_table_exists(self, tablename):
        dbcur = self._database.cursor()
        dbcur.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='{0}';
            """.format(tablename.replace('\'', '\'\'')))
        if dbcur.fetchone():
            dbcur.close()
            return True

        dbcur.close()
        return False
        
    def close(self):
        self._database.close()