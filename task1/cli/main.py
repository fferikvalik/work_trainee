# cli/main.py

import argparse
import json
import xml.etree.ElementTree as ET
from decimal import Decimal

from db.postgres import PostgresDB
from etl.loader import DataLoader
from queries.analytics import Analytics

def to_json(data):
    """
    Сериализация в JSON с обработкой нетиповых объектов (Decimal → str).
    """
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)

def to_xml(data_dict):
    """
    Преобразование словаря отчетов в XML-строку.
    """
    root = ET.Element('reports')
    for section, rows in data_dict.items():
        parent = ET.SubElement(root, section)
        for row in rows:
            item = ET.SubElement(parent, 'item')
            for key, val in row.items():
                child = ET.SubElement(item, key)
                child.text = str(val)
    return ET.tostring(root, encoding='unicode')

def main():
    parser = argparse.ArgumentParser(description="ETL и аналитика для комнат и студентов")
    parser.add_argument('--students', required=True,
                        help="Путь к файлу со студентами (.json или .csv)")
    parser.add_argument('--rooms',    required=True,
                        help="Путь к файлу с комнатами (.json или .csv)")
    parser.add_argument('--format',   choices=['json', 'xml'], default='json',
                        help="Формат выходного отчета")
    parser.add_argument('--output',   help="Путь к выходному файлу (по умолчанию — печать в консоль)")
    args = parser.parse_args()

    # Подключаемся к БД и загружаем данные
    db = PostgresDB()
    loader = DataLoader()
    loader.load(args.rooms, args.students, db)

    # Генерируем отчеты
    analytics = Analytics(db)
    reports = {
        'counts':           analytics.rooms_counts(),
        'lowest_avg_age':   analytics.lowest_avg_age(),
        'max_age_diff':     analytics.max_age_diff(),
        'mixed_gender':     analytics.mixed_gender(),
    }

    # Формируем строку-вывод
    if args.format == 'json':
        output_str = to_json(reports)
    else:
        output_str = to_xml(reports)

    # Запись в файл или вывод в консоль
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_str)
        print(f"Результат записан в файл: {args.output}")
    else:
        print(output_str)

if __name__ == '__main__':
    main()
