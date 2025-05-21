# task1/etl/loader.py
import json
import logging
from typing import List, Dict
from db.postgres import PostgresDB
from .inserter import SchemaCreator

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ParserFactory:
    """Фабрика парсеров для различных форматов."""
    @staticmethod
    def get_parser(file_path: str):
        """Возвращает парсер в зависимости от расширения файла."""
        if file_path.endswith('.json'):
            return JSONParser()
        raise ValueError(f"Неизвестный формат файла: {file_path}")

class JSONParser:
    """Парсер для JSON-файлов."""
    def parse(self, file_path: str) -> List[Dict]:
        """Парсит JSON-файл и возвращает список словарей."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError as e:
            logger.error(f"Ошибка чтения файла: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON: {e}")
            raise

class DataLoader:
    """Класс для загрузки данных в базу данных."""
    def __init__(self, db: PostgresDB, schema_creator: SchemaCreator):
        self.db = db
        self.schema_creator = schema_creator

    def parse_rooms(self, rooms_path: str) -> List[Dict]:
        """Парсит данные комнат из файла."""
        parser = ParserFactory.get_parser(rooms_path)
        return parser.parse(rooms_path)

    def parse_students(self, students_path: str) -> List[Dict]:
        """Парсит данные студентов из файла."""
        parser = ParserFactory.get_parser(students_path)
        return parser.parse(students_path)

    def load(self, rooms_path: str, students_path: str):
        """Загружает данные в базу данных."""
        logger.info("Начало загрузки данных")
        self.schema_creator.create_tables()

        # Парсинг и загрузка комнат
        rooms = self.parse_rooms(rooms_path)
        logger.info(f"Загружено {len(rooms)} комнат из {rooms_path}")
        room_values = [(room["id"], room["name"]) for room in rooms]
        self.db.execute(
            "INSERT INTO rooms (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            params=room_values,
            fetch=False
        )
        logger.info(f"Вставлено {len(rooms)} комнат в базу данных")

        # Парсинг и загрузка студентов
        students = self.parse_students(students_path)
        logger.info(f"Загружено {len(students)} студентов из {students_path}")
        student_values = [
            (stu["id"], stu["name"], stu["birth_date"], stu["gender"], stu["room_id"])
            for stu in students
        ]
        self.db.execute(
            "INSERT INTO students (id, name, birth_date, gender, room_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            params=student_values,
            fetch=False
        )
        logger.info(f"Вставлено {len(students)} студентов в базу данных")

        self.db.create_indexes()