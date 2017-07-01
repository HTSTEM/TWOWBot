'''
The database is in sqlite3 format and stored at `games.sqlite`
The current format (vTWOWb-1.0) is as follows:

    TABLE games:
    uuid | server | channel | round | status | name | finished
    -----|--------|---------|-------|--------|------|---------
    WHERE status is one of "responding", "voting", "results"

    TABLE contestants
    uuid | id | status
    -----|----|-------
    WHERE status is one of "responding", "responded", "dead"

    TABLE responses
    uuid | round | response | uid
    -----|-------|----------|----

    TABLE prompts
    uuid | round | prompt
    -----|-------|-------

    TABLE votes
    uuid | round | voter | v0 | v1 | v2 | v3 | v4 | v5 | v6 | v7 | v8 | v9
    -----|-------|-------|----|----|----|----|----|----|----|----|----|----
    
    TABLE slides
    uuid | uid | round | s0 | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9
    -----|-----|-------|----|----|----|----|----|----|----|----|----|---
'''

import sqlite3
import random
import uuid


class Game:
    def __init__(self, game_uuid, server, channel, round, status, name, finished, gm):
        self.server = server
        self.channel = channel
        self.round = round
        self.status = status
        self.name = name
        self.finished = bool(finished)
        
        self._game_uuid = game_uuid
        self._game_manager = gm
        
    def add_response(self, uid, response):
        while "  " in response:
            response = response.replace("  ", " ")
        if len(response.split(" ")) != 10:
            return "**Response does not appear to the 10 words!** (I counted {0})".format(len(response.split(" ")))
        dbcur = self._game_manager._database.cursor()
        dbcur.execute("""SELECT response FROM responses WHERE uid='?' AND uuid='?' AND round=?""", uid, self._game_uuid, self.round)
        responses = dbcur.fetchall()
        if len(responses) == 0:
            dbcur.execute("""
                INSERT INTO response(uuid, uid, round, response)
                VALUES (?, ?, ?, ?)
                """, self._game_uuid, uid, self.round, response)
            self._game_manager._database.commit()
            return "**Response Recorded.**"
        return "**You have already responded**"
    def get_responses(self, anon=True):
        dbcur = self._game_manager._database.cursor()
        dbcur.execute("""SELECT response, uid FROM games WHERE uuid='?'""", self._game_uuid)
        for response in dbcur.fetchall():
            yield response[0], response[1] if not anon else None
    
    def get_slides(self, uid):
        if self.status != "voting":
            return None
    
        dbcur = self._game_manager._database.cursor()
        dbcur.execute("""SELECT s0, s1, s2, s3, s4, s5, s6, s7, s8, s9 FROM slides WHERE uid='?' AND uuid='?' AND round=?""", uid, self._game_uuid, self.round)
        responses = dbcur.fetchall()
        if len(responses) == 0:
            resps = [i for i in self.get_responses(False)]
            random.shuffle(resps)
            size = min(len(resps), 10)
            slides = resps[size:]
            while len(slides) < 10:
                slides.append(None)
            dbcur.execute("""
                INSERT INTO slides(uuid, uid, round, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, self._game_uuid, uid, self.round, *slides)
            self._game_manager._database.commit()
            return slides
        return responses

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
                    round INTEGER, status TEXT, name TEXT, finished INTEGER)""")
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

    def get_all_games(self):
        dbcur = self._database.cursor()
        dbcur.execute("""SELECT uuid, server, channel, round, status, name, finished FROM games""")
        for game in dbcur.fetchall():
            yield Game(*game, self)
    def start_new_game(self, server, channel, name):
        game_uuid = uuid.uuid4().bytes
        status = 'responding'
        round = 0
        print(game_uuid)
        dbcur = self._database.cursor()
        dbcur.execute("""
            INSERT INTO games(uuid, server, channel, round, status, name, finished)
            VALUES(?,?,?,?,?,?)
            """, (game_uuid, server, channel, round, status, name, 0))
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