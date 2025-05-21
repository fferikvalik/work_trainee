# etl/inserter.py
from db.postgres import PostgresDB, DatabaseError
import logging
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchemaCreator:
    """Класс для создания схемы базы данных.
    Следует принципам SRP (ответственность за создание схемы) и OCP (расширяемость через конфигурацию).
    """
    def __init__(self, db: PostgresDB) -> None:
        """Инициализация с внедрением зависимости от базы данных.
        Args:
            db: Экземпляр базы данных (PostgresDB).
        """
        self.db = db
        # Конфигурация схемы таблиц
        self.schema_definitions = {
            "rooms": """
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL
                );
            """,
            "students": """
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    birth_date DATE NOT NULL,
                    gender CHAR(1) NOT NULL CHECK (gender IN ('M', 'F')),
                    room_id INTEGER NOT NULL REFERENCES rooms(id)
                );
            """
        }

    def drop_tables(self) -> None:
        """Удаляет таблицы для очистки базы перед созданием."""
        try:
            self.db.execute("DROP TABLE IF EXISTS students CASCADE;")
            self.db.execute("DROP TABLE IF EXISTS rooms CASCADE;")
            logger.info("Таблицы успешно удалены")
        except DatabaseError as e:
            logger.error(f"Ошибка при удалении таблиц: {e}")
            raise

    def create_table(self, table_name: str) -> None:
        """Создаёт одну таблицу по её имени.
        Args:
            table_name: Название таблицы (ключ в schema_definitions).
        """
        if table_name not in self.schema_definitions:
            raise ValueError(f"Схема для таблицы {table_name} не определена")
        try:
            self.db.execute(self.schema_definitions[table_name])
            logger.info(f"Таблица {table_name} успешно создана")
        except DatabaseError as e:
            logger.error(f"Ошибка при создании таблицы {table_name}: {e}")
            raise

    def create_tables(self) -> None:
        """Создаёт все таблицы, определённые в schema_definitions."""
        # Сначала создаём rooms, так как students ссылается на неё
        self.create_table("rooms")
        self.create_table("students")

if __name__ == "__main__":
    # Пример использования
    from db.postgres import PostgresDB
    db = PostgresDB()
    creator = SchemaCreator(db)
    creator.create_tables()