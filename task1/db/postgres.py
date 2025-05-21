# task1/db/postgres.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class DatabaseError(Exception):
    """Исключение для ошибок базы данных."""
    pass

class PostgresDB:
    """Класс для работы с PostgreSQL."""
    def __init__(self):
        """Инициализация подключения к базе данных."""
        self._conn = None
        try:
            self._conn = psycopg2.connect(
                host=os.getenv("PGHOST", "localhost"),
                port=os.getenv("PGPORT", "5432"),
                database=os.getenv("PGDATABASE"),
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD")
            )
        except psycopg2.Error as e:
            raise DatabaseError(f"Ошибка подключения к базе данных: {e}")

    def __enter__(self):
        """Поддержка контекстного менеджера."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Закрытие подключения при выходе из контекста."""
        self.close()

    def close(self):
        """Закрывает соединение с базой данных."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(self, query: str, params: Optional[List[Tuple]] = None, fetch: bool = False) -> List[Dict[str, Any]]:
        """
        Выполняет SQL-запрос.
        Args:
            query: SQL-запрос.
            params: Список кортежей с параметрами для запроса.
            fetch: Если True, возвращает результаты.
        Returns:
            Список словарей с результатами (если fetch=True).
        """
        try:
            with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
                if params and len(params) > 0:
                    # Если передан список кортежей, используем executemany
                    cur.executemany(query, params)
                else:
                    cur.execute(query)
                if fetch:
                    return cur.fetchall()
                self._conn.commit()
                return []
        except psycopg2.Error as e:
            self._conn.rollback()
            raise DatabaseError(f"Ошибка выполнения запроса: {e}")

    def create_indexes(self):
        """Создаёт индексы для оптимизации запросов."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_students_room_id ON students(room_id);",
            "CREATE INDEX IF NOT EXISTS idx_students_age ON students(birth_date);",
            "CREATE INDEX IF NOT EXISTS idx_students_sex ON students(gender);"
        ]
        for index in indexes:
            self.execute(index)

    def drop_tables(self):
        """Удаляет таблицы перед тестами."""
        self.execute("DROP TABLE IF EXISTS students CASCADE;")
        self.execute("DROP TABLE IF EXISTS rooms CASCADE;")