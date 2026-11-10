import sqlite3
import pandas as pd
from typing import  Optional 

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
                    id_card INTEGER PRIMARY KEY,
                    question TEXT,
                    reponse TEXT,
                    probabilite REAL,
                    id_theme INTEGER,
                    FOREIGN KEY (id_theme)
                        REFERENCES themes(id_theme)
                        ON DELETE RESTRICT
                );
                    CREATE TABLE IF NOT EXISTS themes(
                        id_theme INTEGER PRIMARY KEY,
                        theme TEXT
                    );

                    CREATE TABLE IF NOT EXISTS stats(
                        id_stat INTEGER PRIMARY KEY,
                        bonnees_reponse INTEGER,
                        mauvaises_reponses INTEGER,
                        date DATE
                    );'''
        self.cursor.executescript(script)
        self.conn.commit()
        print("Table créer avec success")

    def add_on_db(self, table: str, **kwargs):
        """
        Add element into database
        """
        cmd = f'''INSERT INTO {table} ({", ".join(kwargs.keys())})
            VALUES ({", ".join(["?"] * len(kwargs))});
        '''
        self.cursor.execute(cmd, tuple(kwargs.values()))
        self.conn.commit()
        print('Les valeurs on bien ete eregistrer dans la base de données')

    def get_from_db(self, table: str, **kwargs):
        cmd = f'''SELECT * FROM {table}'''

        if kwargs:
            cmd += f''' WHERE {" AND ".join([f"{key}=?" for key in kwargs.keys()])}'''

        self.cursor.execute(cmd, tuple(kwargs.values()))
        res = self.cursor.fetchall()
        print("Recuperation effectuer avec succes")
        return res

    def update_item(self, table: str, id:int,   **kwargs):
        cmd = f'''UPDATE {table} 
                SET {", ".join([f"{key}=?" for key in kwargs.keys()])}
                WHERE {'id_'+table[:-1]}=?'''

        values = tuple(kwargs.values()) + (id,)
        self.cursor.execute(cmd, values)
        self.conn.commit()
        print("Mise a jour effectuer avec succes")

    def delete_id(self, table: str, id: int):
        cmd = f'''DELETE * FROM {table} WHERE {"id_" + table[:-1]} = ?'''

        self.cursor.execute(cmd, (id,))
        self.conn.commit()
        print(f"Spression de ID: {id} dans la table {table}")
    
    def count(self, table: str):
        self.cursor.execute(f'''SELECT COUNT(*) FROM {table}''')
        res = self.cursor.fetchall()
        print(f"Les nombre element dans le table {table} est: {res[0][0]}")

    def count_deep(self, table: str, **kwargs):
        cmd = f'''SELECT COUNT(*) FROM {table}'''

        if kwargs:
            cmd += f''' WHERE {" AND ".join([f"{key}=?" for key in kwargs.keys()])}'''
        
        self.cursor.execute(cmd, tuple(kwargs.values()))
        res = self.cursor.fetchall()
        print(f"Les nombre element dans le table {table} qui respecte la condition est de : {res[0][0]}")

# 
if __name__ == "__main__":
    flascards = DatabaseRequest()
    flascards.create_db()
    flascards.update_item(
    'cards',
    1,
    reponse="Réseau de neurones convolutif"
)
    flascards.get_from_db('cards', id_theme=1)
    flascards.count_deep('cards', id_theme=1)
    # flascards.add_on_db('stats', 
    #                     bonnees_reponse = 5,
    #                     mauvaises_reponses = 1)
    # flascards.add_on_db('themes', theme="Culture")
    # flascards.add_on_db('cards',
    #                      question="Quelle est la capitale de la France ?",
    #                     reponse="Paris",
    #                     probabilite=0.5,
    #                     id_theme=2
    #     )

    