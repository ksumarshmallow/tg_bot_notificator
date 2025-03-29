import sqlite3

def init_db(db_path: str = "calendar.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          user_id INTEGER,
                          date TEXT,
                          time TEXT,
                          description TEXT)''')
    conn.commit()
    return conn

def add_event(conn: sqlite3.Connection, user_id: int, date: str, time: str, description: str):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (user_id, date, time, description) VALUES (?, ?, ?, ?)",
                   (user_id, date, time, description))
    conn.commit()

def get_events(conn: sqlite3.Connection, user_id: int, date: str):
    cursor = conn.cursor()
    cursor.execute("SELECT id, time, description FROM events WHERE user_id = ? AND date = ?", (user_id, date))
    return cursor.fetchall()

def delete_event(conn: sqlite3.Connection, user_id: int, date: str, time: str):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE user_id = ? AND date = ? AND time = ?", (user_id, date, time))
    conn.commit()
    return cursor.rowcount

def get_event_id(conn: sqlite3.Connection, user_id: int, date: str, time: str):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM events WHERE user_id = ? AND date = ? AND time = ?", (user_id, date, time))
    return cursor.fetchone()
