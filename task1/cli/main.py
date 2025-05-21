# cli/main.py
import argparse
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import logging
from typing import Dict, List, Any, Callable
from decimal import Decimal

from db.postgres import PostgresDB, DatabaseError
from etl.loader import DataLoader
from etl.inserter import SchemaCreator
from queries.analytics import Analytics

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OutputFormatter:
    """Абстрактный базовый класс для форматирования вывода."""
    def format(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        raise NotImplementedError

class JSONFormatter(OutputFormatter):
    """Форматирование данных в JSON."""
    def format(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        return json.dumps(data, ensure_ascii=False, indent=2, default=str)

class XMLFormatter(OutputFormatter):
    """Форматирование данных в XML."""
    def format(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        root = ET.Element('reports')
        for section, rows in data.items():
            parent = ET.SubElement(root, section)
            for row in rows:
                item = ET.SubElement(parent, 'item')
                for key, val in row.items():
                    child = ET.SubElement(item, key)
                    child.text = str(val)
        # Форматируем XML с отступами
        rough_string = ET.tostring(root, encoding='unicode')
        parsed = minidom.parseString(rough_string)
        return parsed.toprettyxml(indent="  ", newl="").strip()

class FormatterFactory:
    """Фабрика для выбора форматирования вывода."""
    @staticmethod
    def get_formatter(format_type: str) -> OutputFormatter:
        if format_type == 'json':
            return JSONFormatter()
        elif format_type == 'xml':
            return XMLFormatter()
        else:
            raise ValueError(f"Неподдерживаемый формат: {format_type}")

class ETLRunner:
    """Класс для управления процессом ETL и аналитики.
    Следует принципам SRP (управление ETL) и OCP (расширяемость форматов вывода).
    """
    def __init__(self, db: PostgresDB, loader: DataLoader, analytics: Analytics) -> None:
        """Инициализация с внедрением зависимостей.
        Args:
            db: Экземпляр базы данных.
            loader: Экземпляр загрузчика данных.
            analytics: Экземпляр аналитики.
        """
        self.db = db
        self.loader = loader
        self.analytics = analytics

    def run(self, rooms_path: str, students_path: str, format_type: str, output_path: str = None) -> None:
        """Запускает процесс ETL и аналитики.
        Args:
            rooms_path: Путь к файлу комнат.
            students_path: Путь к файлу студентов.
            format_type: Формат вывода ('json' или 'xml').
            output_path: Путь к файлу для записи результата (опционально).
        """
        try:
            # Загружаем данные
            logger.info("Начало загрузки данных")
            self.loader.load(rooms_path, students_path)
            logger.info("Данные успешно загружены")

            # Генерируем отчёты
            logger.info("Начало генерации отчётов")
            reports = {
                'counts': self.analytics.rooms_counts(),
                'lowest_avg_age': self.analytics.lowest_avg_age(),
                'max_age_diff': self.analytics.max_age_diff(),
                'mixed_gender': self.analytics.mixed_gender(),
            }
            logger.info("Отчёты успешно сгенерированы")

            # Форматируем вывод
            formatter = FormatterFactory.get_formatter(format_type)
            output_str = formatter.format(reports)

            # Записываем или выводим результат
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(output_str)
                logger.info(f"Результат записан в файл: {output_path}")
            else:
                print(output_str)

        except (DatabaseError, FileNotFoundError, ValueError) as e:
            logger.error(f"Ошибка выполнения: {e}")
            raise
        finally:
            self.db.close()

def main():
    """Точка входа для CLI."""
    parser = argparse.ArgumentParser(description="ETL и аналитика для комнат и студентов")
    parser.add_argument('--students', required=True,
                        help="Путь к файлу со студентами (.json или .csv)")
    parser.add_argument('--rooms', required=True,
                        help="Путь к файлу с комнатами (.json или .csv)")
    parser.add_argument('--format', choices=['json', 'xml'], default='json',
                        help="Формат выходного отчета")
    parser.add_argument('--output', help="Путь к выходному файлу (по умолчанию — печать в консоль)")
    args = parser.parse_args()

    # Создаём зависимости
    db = PostgresDB()
    schema_creator = SchemaCreator(db)
    loader = DataLoader(db, schema_creator)
    analytics = Analytics(db)

    # Запускаем процесс
    runner = ETLRunner(db, loader, analytics)
    runner.run(args.rooms, args.students, args.format, args.output)

if __name__ == '__main__':
    main()