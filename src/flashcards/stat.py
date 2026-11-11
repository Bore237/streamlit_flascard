""" StatTools - Flashcards statistics and probability management module.

This module provides tools to track flashcard learning statistics and adjust card probabilities based on user performance.

The :class:StatTools class provides methods to:

- Initialize a database connection.
- Track the number of correct and incorrect answers per day.
- Create or update daily statistics.
- Update flashcard probabilities based on user answers.
- Increase or decrease card probabilities according to performance.


Dependencies:

- datetime: Date and time management.
- flashcards.database: Database management.
- flashcards.logger: Application logging.


Example:

>>> stat = StatTools("flashcards.db")
>>> stat.update_stats(is_correct=True)
>>> stat.update_card_probability(card_id=1, is_correct=True)

"""

from flashcards.database import DatabaseRequest
from datetime import datetime
from flashcards.logger import get_log

logger = get_log(__name__)
class StatTools:
    def __init__(self, database_path: str) -> None:
        """
        Initialize the statistics management class.

        Args:
            database_path (str): Path to the SQLite database.

        Returns:
            None
        """
        self.db = DatabaseRequest(name_database=database_path)

    def  update_stats(self, is_correct: bool, date: str | None = None) -> None:
        """
        Update the daily flashcard statistics.

        If no statistics exist for the specified date, a new record is created.
        Otherwise, the number of correct or incorrect answers is incremented
        according to the user's result.

        Args:
            is_correct (bool): Indicates whether the user's answer is correct.
            date (str | None, optional): Date of the statistics in YYYY-MM-DD
                format. If None, the current date is used. Defaults to None.

        Returns:
            None
        """
        if date:
            now = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            now = datetime.now().strftime('%Y-%m-%d')

        data = self.db.get_from_db('stats', date=now)
        logger.info(data)

        try:
            # If the day does exist creat new row else update depend on the result
            if data.empty:
                bonnes_reponses = 1 if is_correct else 0
                mauvaises_reponses = 0 if is_correct else 1
                self.db.add_on_db('stats', bonnes_reponses=bonnes_reponses, mauvaises_reponses=mauvaises_reponses, date=now)
            else:
                if is_correct:
                    self.db.update_item('stats', data['id_stat'][0], bonnes_reponses = int(data['bonnes_reponses'][0] + 1))
                else:
                    self.db.update_item('stats', data['id_stat'][0], mauvaises_reponses = int(data['mauvaises_reponses'][0] +1))
        except Exception as e:
            logger.error("Erreur lors de la mise a jours des stats", e)

    def update_card_probability(self, card_id: int, is_correct: bool) -> None:
        """
        Update a flashcard's probability based on the user's answer.

        The probability is decreased by 10% after a correct answer and
        increased by 10% after an incorrect answer. The probability is
        constrained between 0.1 and 1.0.

        Args:
            card_id (int): ID of the flashcard to update.
            is_correct (bool): Indicates whether the user's answer is correct.

        Returns:
            None
        """
        data = self.db.get_from_db('cards', id_card=card_id)
        logger.info(data)

        try:
            # If the day does exist creat new row else update depend on the result
            if data.empty:
               logger.warning("Bizzare cette carte n'existe pas")
            else:
                proba = float(data['probabilite'][0])
                if is_correct:
                    nouvelle_probabilité =  max(0.1, min(proba *  0.9, 1.0)) 
                    self.db.update_item('cards', data['id_card'][0], probabilite = nouvelle_probabilité )
                else:
                    nouvelle_probabilité =  max(0.1, min(proba *  1.1, 1.0)) 
                    self.db.update_item('cards', data['id_card'][0], probabilite = nouvelle_probabilité)
        except Exception as e:
            self.db.conn.rollback()
            logger.error("Erreur lors de la mise a jours des probabilité", e)
        

if __name__ == "__main__":
    stat = StatTools('flashcards.db')
    is_correct = False
    id_card = 1
    stat.update_stats(is_correct)
    stat.update_card_probability(id_card, is_correct)