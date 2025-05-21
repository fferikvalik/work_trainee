# queries/analytics.py
from db.postgres import PostgresDB, DatabaseError
import logging
from typing import List, Dict, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Analytics:
    """Класс для выполнения аналитических запросов к базе данных.
    Следует принципу SRP (ответственность за аналитику) и OCP (расширяемость через новые методы).
    """
    def __init__(self, db: PostgresDB) -> None:
        """Инициализация с внедрением зависимости от базы данных.
        Args:
            db: Экземпляр базы данных (PostgresDB).
        """
        self.db = db

    def rooms_counts(self) -> List[Dict[str, Any]]:
        """Возвращает список комнат и количество студентов в каждой.
        Returns:
            Список словарей с полями id, name, student_count.
        """
        query = """
            SELECT r.id, r.name, COUNT(s.id) AS student_count
            FROM rooms r LEFT JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name;
        """
        try:
            result = self.db.execute(query, fetch=True)
            logger.info("Успешно выполнен запрос rooms_counts")
            return result
        except DatabaseError as e:
            logger.error(f"Ошибка при выполнении rooms_counts: {e}")
            raise

    def lowest_avg_age(self) -> List[Dict[str, Any]]:
        """Возвращает 5 комнат с самым маленьким средним возрастом студентов.
        Returns:
            Список словарей с полями id, name, avg_age.
        """
        query = """
            SELECT r.id, r.name, AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birth_date))) AS avg_age
            FROM rooms r JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name ORDER BY avg_age ASC LIMIT 5;
        """
        try:
            result = self.db.execute(query, fetch=True)
            logger.info("Успешно выполнен запрос lowest_avg_age")
            return result
        except DatabaseError as e:
            logger.error(f"Ошибка при выполнении lowest_avg_age: {e}")
            raise

    def max_age_diff(self) -> List[Dict[str, Any]]:
        """Возвращает 5 комнат с самой большой разницей в возрасте студентов.
        Returns:
            Список словарей с полями id, name, age_diff_years.
        """
        query = """
            SELECT r.id, r.name, 
                   EXTRACT(YEAR FROM AGE(MAX(s.birth_date), MIN(s.birth_date))) AS age_diff_years
            FROM rooms r JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name ORDER BY age_diff_years DESC LIMIT 5;
        """
        try:
            result = self.db.execute(query, fetch=True)
            logger.info("Успешно выполнен запрос max_age_diff")
            return result
        except DatabaseError as e:
            logger.error(f"Ошибка при выполнении max_age_diff: {e}")
            raise

    def mixed_gender(self) -> List[Dict[str, Any]]:
        """Возвращает список комнат с разнополыми студентами.
        Returns:
            Список словарей с полями id, name.
        """
        query = """
            SELECT r.id, r.name FROM rooms r JOIN students s ON s.room_id = r.id
            GROUP BY r.id, r.name HAVING COUNT(DISTINCT s.gender) > 1;
        """
        try:
            result = self.db.execute(query, fetch=True)
            logger.info("Успешно выполнен запрос mixed_gender")
            return result
        except DatabaseError as e:
            logger.error(f"Ошибка при выполнении mixed_gender: {e}")
            raise

if __name__ == "__main__":
    # Пример использования
    from db.postgres import PostgresDB
    db = PostgresDB()
    analytics = Analytics(db)
    print(analytics.rooms_counts())