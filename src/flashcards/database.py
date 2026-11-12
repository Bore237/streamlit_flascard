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
from typing import Optional, List, Any
from pathlib import Path
import json
from flashcards.logger import get_log

logger = get_log(__name__)

class DatabaseRequest:
    def __init__(self, name_database: str = "flashcards.db", json_path: Optional[Path] = None):
        self.name_database = name_database
        logger.info(f'Initialisation de la base de données {name_database}')

        if json_path:
            self.create_db()
            self.load_db(json_path)

    def _get_connection(self):
        """Helper to open a thread-safe connection with foreign keys enabled."""
        conn = sqlite3.connect(self.name_database)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_db(self, script: Optional[str] = None) -> None:
        """
        Create db with types: NULL, INTEGER, REAL, TEXT, and BLOB.
        
        Args:
            script (Optional[str]): SQL script used to create the database.

        Returns:
            None
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
                    bonnes_reponses INTEGER,
                    mauvaises_reponses INTEGER,
                    date DATE UNIQUE NOT NULL
                );'''
        
        try:
            with self._get_connection() as conn:
                conn.executescript(script)
                conn.commit()
            logger.info("Tables créées avec succès")
        except Exception as e:
            logger.error("Erreur lors de la création de la base de données", exc_info=e)

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
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(cmd, tuple(kwargs.values()))
                conn.commit()
                rowcount = cursor.rowcount
            logger.info(f"Les valeurs ont bien été enregistrées dans la base de données. Nombre de lignes modifiées : {rowcount}")
        except Exception as e:
            logger.warning(f"La commande reçue est: {cmd} pour la table {table}")
            logger.error(f"Erreur lors de l'insertion: {e}")

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
        res = []
        columns = []

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if kwargs:
                    cmd += f''' WHERE {" AND ".join([f"{key}=?" for key in kwargs.keys()])}'''

                cursor.execute(cmd, tuple(kwargs.values()))
                res = cursor.fetchall()

                # Get column info from the table
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [column[1] for column in cursor.fetchall()]
            
            logger.info("Récupération effectuée avec succès")
        except Exception as e:
            logger.warning(f"La commande reçue est: {cmd} pour la table {table}")
            logger.error(f"Erreur lors de la récupération: {e}")

        return pd.DataFrame(res, columns=columns)

    def update_item(self, table: str, id: int, **kwargs) -> None:
        """
        Update an existing record in the specified table using its ID.

        Args:
            table (str): Name of the table.
            id (int): ID of the record to update.
            **kwargs: Column names and their updated values.

        Returns:
            None
        """
        id_value = int(id)
        id_column = 'id_' + table[:-1]
        cmd = f'''UPDATE {table} 
                SET {", ".join([f"{key} = ?" for key in kwargs.keys()])}
                WHERE {id_column} = ?'''

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                values = tuple(kwargs.values()) + (id_value,)
                cursor.execute(cmd, values)
                conn.commit()
                rowcount = cursor.rowcount
            logger.info(f"Mise à jour de la table: {table} effectuée avec succès. Nombre de lignes modifiées : {rowcount}")
        except Exception as e:
            logger.warning(f"La commande reçue est: {cmd} pour la table {table}")
            logger.error(f"Erreur lors de la modification: {e}")

    def delete_id(self, table: str, id: int) -> None:
        """
        Delete a record from the specified table using its ID.

        Args:
            table (str): Name of the table.
            id (int): ID of the record to delete.

        Returns:
            None
        """
        id_column = 'id_' + table[:-1]
        cmd = f'''DELETE FROM {table} WHERE {id_column} = ?'''

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(cmd, (id,))
                conn.commit()
            logger.info(f"Suppression de l'ID: {id} dans la table {table}")
        except Exception as e:
            logger.warning(f"La commande reçue est: {cmd} pour la table {table}")
            logger.error(f"Erreur lors de la suppression: {e}")
    
    def count(self, table: str) -> int:
        """
        Count the total number of records in a table.

        Args:
            table (str): Name of the table.

        Returns:
            int: Total count of records.
        """
        res = [[0]]
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''SELECT COUNT(*) FROM {table}''')
                res = cursor.fetchall()
            logger.info(f"Le nombre d'éléments dans la table {table} est: {res[0][0]}")
        except Exception as e:
            logger.error(f"Erreur lors du comptage: {e}")
        return res[0][0]

    def count_deep(self, table: str, **kwargs) -> List[Any]:
        """
        Count the number of records in a table that match the specified conditions.

        Args:
            table (str): Name of the table.
            **kwargs: Column names and their corresponding filter values.

        Returns:
            list: Query result containing the number of matching records.
        """
        cmd = f'''SELECT COUNT(*) FROM {table}'''
        res = [[0]]

        if kwargs:
            cmd += f''' WHERE {" AND ".join([f"{key}=?" for key in kwargs.keys()])}'''
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(cmd, tuple(kwargs.values()))
                res = cursor.fetchall()
            logger.info(f"Le nombre d'éléments dans la table {table} qui respectent la condition est de : {res[0][0]}")
        except Exception as e:
            logger.warning(f"La commande reçue est: {cmd} pour la table {table}")
            logger.error(f"Erreur lors du comptage: {e}")
        
        return res 
    
    def load_db(self, json_path: Path) -> None:
        """
        Load data from a JSON file into the database.

        Args:
            json_path (Path): Path to the JSON file containing the data to import.

        Returns:
            None
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        try:
            for key, values in data.items():
                for value in values:
                    self.add_on_db(key, **value)
            logger.info("Importation réussie !")
        except Exception as e:
            logger.error(f"Erreur lors de l'importation : {e}")

if __name__ == "__main__":
    flashcards = DatabaseRequest(json_path=Path("data/flashcards.json"))
    flashcards.get_from_db('cards', id_theme=1)