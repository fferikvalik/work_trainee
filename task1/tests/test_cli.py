import unittest
import subprocess
import json
import xml.etree.ElementTree as ET
import os
import logging
from unittest.mock import Mock, patch
from typing import List, Dict

# Настройка логирования для тестов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Путь к тестовым данным
TEST_DATA_DIR = "tests/data"
os.makedirs(TEST_DATA_DIR, exist_ok=True)

# Тестовые данные
TEST_ROOMS = [{"id": 1, "name": "Room1"}, {"id": 2, "name": "Room2"}]
TEST_STUDENTS = [
    {"id": 1, "name": "Student1", "birth_date": "2000-01-01", "gender": "M", "room_id": 1},
    {"id": 2, "name": "Student2", "birth_date": "2001-01-01", "gender": "F", "room_id": 1}
]

class TestProjectStructure(unittest.TestCase):
    """Тесты структуры проекта."""
    def test_structure(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        expected_files = [
            os.path.join(base_dir, "task1/db/postgres.py"),
            os.path.join(base_dir, "task1/etl/loader.py"),
            os.path.join(base_dir, "task1/etl/inserter.py"),
            os.path.join(base_dir, "task1/queries/analytics.py"),
            os.path.join(base_dir, "task1/cli/main.py"),
            os.path.join(base_dir, "task1/tests/test_cli.py"),
        ]
        expected_dirs = [
            os.path.join(base_dir, "task1"),
            os.path.join(base_dir, "task2"),
        ]
        for file in expected_files:
            self.assertTrue(os.path.exists(file), f"Файл {file} отсутствует")
        for dir in expected_dirs:
            self.assertTrue(os.path.exists(dir), f"Директория {dir} отсутствует")

class TestPostgresDB(unittest.TestCase):
    """Тесты класса PostgresDB."""
    @patch('psycopg2.connect')
    def test_connect_context(self, mock_connect):
        """Проверяем работу контекстного менеджера."""
        from db.postgres import PostgresDB
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        db = PostgresDB()
        with db:
            pass
        self.assertTrue(mock_conn.close.called)

    @patch('psycopg2.connect')
    def test_execute_fetch(self, mock_connect):
        """Проверяем выполнение запроса с возвратом данных."""
        from db.postgres import PostgresDB
        mock_conn = Mock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{"key": "value"}]
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        db = PostgresDB()
        result = db.execute("SELECT 1;", fetch=True)
        self.assertEqual(result, [{"key": "value"}])
        mock_cursor.execute.assert_called_once()

class TestSchemaCreator(unittest.TestCase):
    """Тесты класса SchemaCreator."""
    @patch('db.postgres.PostgresDB.execute')
    def test_create_tables(self, mock_execute):
        """Проверяем создание таблиц."""
        from etl.inserter import SchemaCreator
        from db.postgres import PostgresDB
        db = PostgresDB()
        creator = SchemaCreator(db)
        creator.create_tables()
        self.assertEqual(mock_execute.call_count, 2)  # rooms и students

class TestDataLoader(unittest.TestCase):
    """Тесты класса DataLoader."""
    @patch('etl.loader.ParserFactory.get_parser')
    @patch('db.postgres.PostgresDB.execute')
    def test_load(self, mock_execute, mock_parser):
        """Проверяем загрузку данных."""
        from etl.loader import DataLoader
        from etl.inserter import SchemaCreator
        from db.postgres import PostgresDB
        mock_parser_instance = Mock()
        mock_parser_instance.parse.side_effect = [TEST_ROOMS, TEST_STUDENTS]
        mock_parser.return_value = mock_parser_instance
        db = PostgresDB()
        loader = DataLoader(db, SchemaCreator(db))
        loader.load("tests/data/rooms.json", "tests/data/students.json")
        # Ожидаем 7 вызовов: 2 таблицы + 2 вставки + 3 индекса
        self.assertEqual(mock_execute.call_count, 7)
        mock_execute.assert_any_call(
            "INSERT INTO rooms (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            params=[(r["id"], r["name"]) for r in TEST_ROOMS],
            fetch=False
        )
        mock_execute.assert_any_call(
            "INSERT INTO students (id, name, birth_date, gender, room_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            params=[(s["id"], s["name"], s["birth_date"], s["gender"], s["room_id"]) for s in TEST_STUDENTS],
            fetch=False
        )

class TestAnalytics(unittest.TestCase):
    """Тесты класса Analytics."""
    @patch('db.postgres.PostgresDB.execute')
    def test_analytics_methods(self, mock_execute):
        """Проверяем выполнение всех аналитических запросов."""
        from queries.analytics import Analytics
        from db.postgres import PostgresDB
        mock_execute.return_value = [{"id": 1, "name": "Room1", "value": 5}]
        db = PostgresDB()
        analytics = Analytics(db)
        for method in [analytics.rooms_counts, analytics.lowest_avg_age,
                      analytics.max_age_diff, analytics.mixed_gender]:
            result = method()
            self.assertEqual(len(result), 1)
            self.assertIn("id", result[0])
            self.assertIn("name", result[0])

class TestCLI(unittest.TestCase):
    """Тесты CLI через subprocess."""
    @classmethod
    def setUpClass(cls):
        from db.postgres import PostgresDB
        db = PostgresDB()
        db.drop_tables()  # Сбрасываем таблицы перед тестами
        cls.rooms_file = os.path.join(TEST_DATA_DIR, "rooms.json")
        cls.students_file = os.path.join(TEST_DATA_DIR, "students.json")
        with open(cls.rooms_file, "w", encoding="utf-8") as f:
            json.dump(TEST_ROOMS, f)
        with open(cls.students_file, "w", encoding="utf-8") as f:
            json.dump(TEST_STUDENTS, f)
        cls.base_cmd = [
            "python", "-m", "cli.main",
            "--rooms", cls.rooms_file,
            "--students", cls.students_file,
        ]

    def test_json_stdout(self):
        """Проверяем вывод JSON в stdout без --output."""
        cmd = self.base_cmd + ["--format", "json"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        for section in ("counts", "lowest_avg_age", "max_age_diff", "mixed_gender"):
            self.assertIn(section, data)
            self.assertIsInstance(data[section], list)

    def test_xml_stdout(self):
        """Проверяем вывод XML в stdout без --output."""
        cmd = self.base_cmd + ["--format", "xml"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        root = ET.fromstring(proc.stdout)
        self.assertEqual(root.tag, "reports")
        tags = {child.tag for child in root}
        self.assertTrue({"counts", "lowest_avg_age", "max_age_diff", "mixed_gender"}.issubset(tags))

    def test_output_file_json(self):
        """Проверяем запись в файл JSON (--output)."""
        out = os.path.join(TEST_DATA_DIR, "test_output.json")
        if os.path.exists(out):
            os.remove(out)
        cmd = self.base_cmd + ["--format", "json", "--output", out]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.exists(out))
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("counts", data)
        os.remove(out)

    def test_output_file_xml(self):
        """Проверяем запись в файл XML (--output)."""
        out = os.path.join(TEST_DATA_DIR, "test_output.xml")
        if os.path.exists(out):
            os.remove(out)
        cmd = self.base_cmd + ["--format", "xml", "--output", out]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.exists(out))
        tree = ET.parse(out)
        self.assertEqual(tree.getroot().tag, "reports")
        os.remove(out)

    def test_invalid_file(self):
        """Проверяем обработку некорректного пути к файлу."""
        cmd = ["python", "-m", "cli.main", "--rooms", "nonexistent.json", "--students", self.students_file]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("FileNotFoundError", proc.stderr)

if __name__ == "__main__":
    unittest.main()