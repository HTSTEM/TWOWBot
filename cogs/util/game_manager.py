'''
The database is in sqlite3 format and stored at `games.sqlite`
The current format (vTWOWb-1.0) is as follows:

    TABLE games:
    uuid | server | channel | round | status | name | finished | owner
    -----|--------|---------|-------|--------|------|-----------------
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
    PROMPT_SET = 0
    PROMPT_ALLREADY_SET = 1
    
    DATABASE_ERROR = -1

    def __init__(self, game_uuid, server, channel, round, status, name, finished, owner, gm):
        self.server = server
        self.channel = channel
        self.round = round
        self.status = status
        self.name = name
        self.finished = bool(finished)
        self.owner = owner
        
        self._game_uuid = game_uuid
        self._game_manager = gm
        
    def add_response(self, uid, response):
        dbcur = self._game_manager._database.cursor()
        if self.get_response(uid) is None:
            print("Add")
            dbcur.execute("""
                INSERT INTO responses(uuid, uid, round, response)
                VALUES (?, ?, ?, ?)
                """, (self._game_uuid, uid, self.round, response))
            dbcur.close()
            self._game_manager._database.commit()
            return True
        dbcur.close()
        return False
    def get_response(self, uid):
        dbcur = self._game_manager._database.cursor()
        dbcur.execute("""SELECT response FROM responses WHERE uuid='{0}' AND round={1} AND uid={2}""".format(self._game_uuid, self.round, uid))
        fo = dbcur.fetchall()
        if fo:
            dbcur.close()
            return fo[0]
            
        dbcur.close()
        return None
    def get_responses(self, anon=True):
        dbcur = self._game_manager._database.cursor()
        dbcur.execute("""SELECT response, uid FROM responses WHERE uuid='{0}'""".format(self._game_uuid))
        for response in dbcur.fetchall():
            yield response[0], response[1] if not anon else None
        dbcur.close()

    def is_owner(self, id):
        return id == self.owner
    
    def set_prompt(self, prompt):
        if self.get_prompt() is not None:
            return self.PROMPT_ALLREADY_SET
            
        dbcur = self._game_manager._database.cursor()
        dbcur.execute("""
            INSERT INTO prompts(uuid, round, prompt)
            VALUES(?, ?, ?)""", (self._game_uuid, self.round, prompt))
        dbcur.close()
        self._game_manager._database.commit()
            
        return self.PROMPT_SET
    def get_prompt(self):
        dbcur = self._game_manager._database.cursor()
        dbcur.execute("""
            SELECT prompt FROM prompts WHERE uuid='{0}' AND round={1};
            """.format(self._game_uuid, self.round))
        fo = dbcur.fetchone()
        if fo:
            dbcur.close()
            return fo[0]

        dbcur.close()
        return None
    
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
        
        # Create any tables that don't exist.
        if not self._check_table_exists("games"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE games(
                    uuid TEXT PRIMARY KEY, server INTEGER, channel INTEGER,
                    round INTEGER, status TEXT, name TEXT, finished INTEGER, owner INTEGER)""")
            self._database.commit()
        if not self._check_table_exists("contestants"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE contestants(
                    uuid TEXT, id INTEGER, status TEXT)""")
            self._database.commit()
        if not self._check_table_exists("responses"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE responses(
                    uuid TEXT, round INTEGER, response TEXT, uid INTEGER)""")
            self._database.commit()
        if not self._check_table_exists("prompts"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE prompts(
                    uuid TEXT, round INTEGER, prompt TEXT)""")
            self._database.commit()
        if not self._check_table_exists("votes"):
            dbcur = self._database.cursor()
            dbcur.execute("""
                CREATE TABLE votes(
                    uuid TEXT, round INTEGER, votes INTEGER,
                    v0 INTEGER, v1 INTEGER, v2 INTEGER, v3 INTEGER, v4 INTEGER,
                    v5 INTEGER, v6 INTEGER, v7 INTEGER, v8 INTEGER, v9 INTEGER)""")
            self._database.commit()

    # Game related functions
    def get_all_games(self):
        dbcur = self._database.cursor()
        dbcur.execute("""SELECT uuid, server, channel, round, status, name, finished, owner FROM games""")
        for game in dbcur.fetchall():
            yield Game(*game, self)
    def start_new_game(self, server, channel, name, owner):
        game_uuid = uuid.uuid4().hex
        status = 'responding'
        round = 1
        print(game_uuid)
        dbcur = self._database.cursor()
        dbcur.execute("""
            INSERT INTO games(uuid, server, channel, round, status, name, finished, owner)
            VALUES(?,?,?,?,?,?,?,?)
            """, (game_uuid, server, channel, round, status, name, 0, owner))
        self._database.commit()
    def get_game(self, channel):
        dbcur = self._database.cursor()
        dbcur.execute("""
            SELECT uuid, server, channel, round, status, name, finished, owner FROM games WHERE channel='{0}';
            """.format(str(channel).replace('\'', '\'\'')))
        fo = dbcur.fetchone()
        if fo:
            dbcur.close()
            return Game(*fo, self)

        dbcur.close()
        return None
            
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