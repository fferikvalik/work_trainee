from db.postgres import PostgresDB

class SchemaCreator:
    def __init__(self, db: PostgresDB):
        """Инициализация создателя схемы с подключением к БД"""
        self.db = db

    def create_tables(self):
        # Создание таблицы rooms
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
            """
        )
        # Создание таблицы students
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                birth_date DATE NOT NULL,
                gender CHAR(1) NOT NULL CHECK (gender IN ('M','F')),
                room_id INTEGER NOT NULL REFERENCES rooms(id)
            );
            """
        )