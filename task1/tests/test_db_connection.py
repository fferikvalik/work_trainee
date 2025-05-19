# tests/test_db_connection.py

import unittest
from db.postgres import PostgresDB

class TestDBConnection(unittest.TestCase):
    def setUp(self):
        # Путь к вашему .env (если он не в корне, укажите относительный путь)
        self.db = PostgresDB(env_path=".env")
    
    def tearDown(self):
        self.db.close()

    def test_connect_and_select(self):
        # Попытка подключиться
        try:
            self.db.connect()
        except Exception as e:
            self.fail(f"Не удалось установить соединение с БД: {e}")

        # Выполняем простой запрос SELECT 1
        rows = self.db.execute("SELECT 1 AS result;", fetch=True)
        self.assertIsInstance(rows, list, "Ожидаем список словарей")
        self.assertGreater(len(rows), 0, "Ожидаем как минимум одну строку")
        self.assertEqual(rows[0].get("result"), 1, "Ожидаем, что SELECT 1 вернёт 1")

if __name__ == "__main__":
    unittest.main()
