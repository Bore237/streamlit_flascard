from flashcards.database import DatabaseRequest
from datetime import datetime

class StatTools:
    def __init__(self, database_path: str) -> None:
        self.db = DatabaseRequest(name_database=database_path)

    def  update_stats(self, is_correct: bool, date: str|None = None):
        if date:
            now = datetime.strptime('2026-11-10', '%Y-%m-%d').date()
        else:
            now = datetime.now().strftime('%Y-%m-%d')

        data = self.db.get_from_db('stats', date=now)
        print(data)
        
        # If the day does exist creat new row else update depend on the result
        if data.empty:
            bonnes_reponses = 1 if is_correct else 0
            mauvaises_reponses = 0 if is_correct else 1
            self.db.add_on_db('stats', bonnes_reponses=bonnes_reponses, mauvaises_reponses=mauvaises_reponses, date=now)
        else:
            if is_correct:
                self.db.update_item('stats', data['id_stat'][0], bonnes_reponses = data['bonnes_reponses'][0] + 1)
            else:
                self.db.update_item('stats', data['id_stat'][0], mauvaises_reponses = data['mauvaises_reponses'][0] +1)
        self.db.conn.commit() 

    def  update_card_probability(self, card_id, is_correct):
        pass

if __name__ == "__main__":
    stat = StatTools('flashcards.db')
    stat.update_stats(False)