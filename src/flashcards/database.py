""" DatabaseRequest - SQLite database management module.

This module provides database management functionality for the Flashcards application using SQLite.

The :class:DatabaseRequest class handles database creation, data insertion, retrieval, updates, deletion, counting and JSON imports.

Dependencies:

- sqlite3
- pandas
- typing
- pathlib
- json
- flashcards.logger


Example:

>>> from pathlib import Path
>>> db = DatabaseRequest(name_database="flashcards.db")
>>> cards = db.get_from_db("cards", id_theme=1)

"""

import sqlite3
import pandas as pd
from typing import  Optional, List, Any
from pathlib import Path
import json
from flashcards.logger import get_log

logger = get_log(__name__)

## Config databasa
class DatabaseRequest:
    def __init__(self, name_database: str = "flashcards.db", json_path: Optional[Path] = None):
        self.conn = sqlite3.connect(name_database)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        logger.info(f'Connexion reuissite a la db {name_database}')

        if json_path:
            self.create_db()
            self.load_db(json_path)

    def create_db(self, script: Optional[str] = None) -> None:
        """
        Create db with type: NULL, INTEGER, REAL, DATA, TEXT et BLOB.
        
        Args:
        script (Optional[str]): SQL script used to create the database.

        Returns:
            None
        """
        try:
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
                            bonnes_reponses INTEGER,
                            mauvaises_reponses INTEGER,
                            date DATE UNIQUE NOT NULL
                        );'''
            self.cursor.executescript(script)
            self.conn.commit()
            logger.info("Table créer avec success")

        except Exception as e:
            self.conn.rollback()
            logger.error("Erreur lors de la création de la base de donnée", e)

    def add_on_db(self, table: str, **kwargs) -> None:
        """
        Add a new record to the specified table.

        Args:
            table (str): Name of the table.
            **kwargs: Column names and their corresponding values.

        Returns:
            None
        """
        cmd = f'''INSERT INTO {table} ({", ".join(kwargs.keys())})
            VALUES ({", ".join(["?"] * len(kwargs))});
        '''
        try:
            self.cursor.execute(cmd, tuple(kwargs.values()))
            self.conn.commit()
            logger.info('''Les valeurs on bien ete eregistrer dans la base de données
                Nombre de lignes modifiées : {self.cursor.rowcount}''')
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"La commande recu est: {cmd} pour la table {table}")
            logger.error("Erreur lors de inserstion", e)

    def get_from_db(self, table: str, **kwargs) -> pd.DataFrame:
        """
        Retrieve records from the specified table based on given criteria.

        Args:
            table (str): Name of the table.
            **kwargs: Column names and their corresponding filter values.

        Returns:
            pd.DataFrame: DataFrame containing the retrieved records.
        """
        cmd = f'''SELECT * FROM {table}'''

        try:
            if kwargs:
                cmd += f''' WHERE {" AND ".join([f"{key}=?" for key in kwargs.keys()])}'''

            self.cursor.execute(cmd, tuple(kwargs.values()))
            res = self.cursor.fetchall()

            # get colonm info from the table
            self.cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in self.cursor.fetchall()]
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"La commande recu est: {cmd} pour la table {table}")
            logger.error("Erreur lors de la recuperation", e)

        logger.info("Recuperation effectuer avec succes")
        return pd.DataFrame(res, columns=columns)

    def update_item(self, table: str, id_value:int, **kwargs) -> None:
        """
        Update an existing record in the specified table using its ID.

        Args:
            table (str): Name of the table.
            id_value (int): ID of the record to update.
            **kwargs: Column names and their updated values.

        Returns:
            None
        """
        id_value = int(id_value)
        cmd = f'''UPDATE {table} 
                SET {", ".join([f"{key} = ?" for key in kwargs.keys()])}
                WHERE {'id_' + table[:-1]} = ?'''

        try:
            values = tuple(kwargs.values()) + (id_value,)
            self.cursor.execute(cmd, values)
            self.conn.commit()
            logger.info(f'''Mise a jour de la table: {table} effectuer avec succes
                Nombre de lignes modifiées : {self.cursor.rowcount}''')
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"La commande recu est: {cmd} pour la table {table}")
            logger.error("Erreur lors de la modification", e)

    def delete_id(self, table: str, id: int) -> None:
        """
        Delete a record from the specified table using its ID.

        Args:
            table (str): Name of the table.
            id (int): ID of the record to delete.

        Returns:
            None
        """
        cmd = f'''DELETE FROM {table} WHERE {"id_" + table[:-1]} = ?'''

        try:
            self.cursor.execute(cmd, (id,))
            self.conn.commit()
            logger.info(f"Supression de ID: {id} dans la table {table}")
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"La commande recu est: {cmd} pour la table {table}")
            logger.error("Erreur lors de la supression", e)
    
    def count(self, table: str) -> int:
        """
        Count the total number of records in a table.

        Args:
            table (str): Name of the table.

        Returns:
            None
        """
        try:
            self.cursor.execute(f'''SELECT COUNT(*) FROM {table}''')
            res = self.cursor.fetchall()
            logger.info(f"Les nombre element dans le table {table} est: {res[0][0]}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f'Erreur lors du comptage', e)
        return res[0][0]

    
    def count_deep(self, table: str, **kwargs) -> List[Any]:
        """
        Count the number of records in a table that match the specified conditions.

        Args:
            table (str): Name of the table.
            **kwargs: Column names and their corresponding filter values.

        Returns:
            tuple: Query result containing the number of matching records.
        """
        cmd = f'''SELECT COUNT(*) FROM {table}'''

        if kwargs:
            cmd += f''' WHERE {" AND ".join([f"{key}=?" for key in kwargs.keys()])}'''
        try:
            self.cursor.execute(cmd, tuple(kwargs.values()))
            res = self.cursor.fetchall()
            logger.info(f"Les nombre element dans le table {table} qui respecte la condition est de : {res[0][0]}")
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"La commande recu est: {cmd} pour la table {table}")
            logger.error("Erreur lors de la conptage", e)
        
        return res 
    
    def load_db(self, json_path: Path) -> None:
        """
        Load data from a JSON file into the database.

        Args:
            json_path (Path): Path to the JSON file containing the data to import.

        Returns:
            None
        """
        with open(json_path, 'r') as f:
            data = json.load(f)

        #Read Json file and inser element
        try:
            for key, values in data.items():
                for value in values:
                    self.add_on_db(key, **value)
            logger.info("Importation réussie !")

        except Exception as e:
            logger.error(f"Erreur lors de l'importation : {e}")

# 
if __name__ == "__main__":
    # flascards.create_db()
    flascards = DatabaseRequest(json_path=Path("data/flashcards.json"))
    flascards.get_from_db('cards', id_theme=1)
    # flascards.update_item('cards', 1, reponse="Réseau de neurones convolutif")


    