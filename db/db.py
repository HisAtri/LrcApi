import os
import sqlite3


class SQLite:
    def __init__(self, file: str):
        self.file: str = os.path.join(os.getcwd(), file)

    def create_table(self, table_name: str, fields: list[tuple[str, str]], if_not_exist: bool = False):
        # Generate the SQL statement
        field_definitions = ", ".join([f"{name} {type}" for name, type in fields])
        if_not_exist_clause = "IF NOT EXISTS" if if_not_exist else ""
        sql = f"CREATE TABLE {if_not_exist_clause} {table_name} ({field_definitions})"

        # Use a new connection with context manager
        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

    def create_json_table(self, table_name: str, if_not_exist: bool = False):
        if_not_exist_clause = "IF NOT EXISTS" if if_not_exist else ""
        sql = (f"CREATE TABLE {if_not_exist_clause} {table_name} ("
               f"id INTEGER PRIMARY KEY,"
               f"data JSON"
               f")")

        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

    def is_json_table(self, table_name: str) -> bool:
        # Check if the table exists and has a 'data' column of type 'JSON'
        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            # Check if there is a column named 'data' with type 'JSON'
            for column in columns:
                if column[1] == 'data' and column[2] == 'JSON':
                    return True
            return False

    def init_kv_table(self, table_name: str = 'kv_table'):
        sql = (f"CREATE TABLE IF NOT EXISTS {table_name} ("
               f"_key TEXT PRIMARY KEY,"
               f"_value TEXT"
               f")")

        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

    def kv_insert(self, key: str, value: str, table_name: str = 'kv_table'):
        sql = f"INSERT INTO {table_name} (_key, _value) VALUES (?, ?)"
        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (key, value))
            conn.commit()

    def kv_read(self, key: str, table_name: str = 'kv_table') -> str:
        sql = f"SELECT _value FROM {table_name} WHERE _key = ?"
        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (key,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None

    def kv_update(self, key: str, value: str, table_name: str = 'kv_table'):
        sql = f"UPDATE {table_name} SET _value = ? WHERE _key = ?"
        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (value, key))
            conn.commit()
            
    def custom_sql(self, sql:str):
        with sqlite3.connect(self.file) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
