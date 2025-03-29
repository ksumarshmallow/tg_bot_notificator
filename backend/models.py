from dataclasses import dataclass
from backend.database import get_db_connection, init_db
import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


@dataclass
class CalendarDatabase:
    table_name: str

    def __post_init__(self):
        init_db()

    def _execute_query(self, query, params=None, fetch=False):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params if params else ())
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None
        conn.close()
        return result

    def save(self, user_id, name, date):
        query = f"INSERT INTO {self.table_name} (user_id, name, date) VALUES (?, ?, ?)"
        self._execute_query(query, (user_id, name, date))
    
    def get_date_events(self, user_id, date):
        query = f"SELECT name FROM {self.table_name} WHERE DATE(date) = ? AND user_id = ?"
        return self._execute_query(query, (date, user_id), fetch=True)

    def get_all(self, user_id):
        query = f"SELECT name, date FROM {self.table_name} WHERE user_id = ?"
        return self._execute_query(query, (user_id, ), fetch=True)
    
    def delete_event(self, user_id, name, date):
        query = f"DELETE FROM {self.table_name} WHERE user_id = ? AND name = ? AND DATE(date) = ?"
        self._execute_query(query, (user_id, name, date))
        return True #TODO: number of rows


class EventCalendar(CalendarDatabase):
    def __init__(self):
        super().__init__("events")

    def save_event(self, user_id, event_name, event_date):
        self.save(user_id, event_name, event_date)

    def get_events(self, user_id):
        return self.get_all(user_id)


class TodoCalendar(CalendarDatabase):
    def __init__(self):
        super().__init__("todos")

    def save_todo(self, user_id, todo_name, todo_date):
        self.save(user_id, todo_name, todo_date)

    def get_todos(self, user_id):
        return self.get_all(user_id)
