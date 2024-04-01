import sqlite3
import multiprocessing

class SQLiteProxy:
    def __init__(self, db_file):
        self.db_file = db_file
        self.lock = multiprocessing.Lock()

    def execute(self, query, params=None):
        with self.lock:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            conn.commit()
            conn.close()
        return result