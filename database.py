import sqlite3
from typing import Union, Optional 

## Config databasa
class DatabaseRequest:
    def __init__(self, name_database: str = "flashcards.db"):
        self.conn = sqlite3.connect(name_database)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        print(f'Connexion reuissite a la db {name_database}')

    def create_db(self, script: Optional[str] = None):
        """
        Create db with type: NULL, INTEGER, REAL, TEXT et BLOB.
        """
        if script is None:
            script = '''
                CREATE TABLE IF NOT EXISTS cards(
                    id_cards INTEGER PRIMARY KEY,
                    question TEXT,
                    reponse TEXT,
                    probabilite REAL,
                    id_theme INTEGER,
                    FOREIGN KEY (id_theme)
                        REFERENCES themes(id_theme)
                        ON DELETE RESTRICT
                );
                    CREATE TABLE IF NOT EXISTS themes(
                        id_themes INTEGER PRIMARY KEY,
                        theme TEXT
                    );

                    CREATE TABLE IF NOT EXISTS stats(
                        id_stats INTEGER PRIMARY KEY,
                        bonnees_reponse INTEGER,
                        mauvaises_reponses INTEGER,
                        date DATE
                    );'''
        self.cursor.executescript(script)
        self.conn.commit()
        print("Table créer avec success")


flascards = DatabaseRequest()
flascards.create_db()

    