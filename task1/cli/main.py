# cli/main.py

import argparse
import json
import xml.etree.ElementTree as ET
from decimal import Decimal
from db.postgres import PostgresDB
from etl.loader import DataLoader
from queries.analytics import Analytics

def to_json(data):
    # default=str конвертирует Decimal и другие нетиповые объекты в строки
    return json.dumps(data, ensure_ascii=False, indent=2, default=str)

def to_xml(data_dict):
    root = ET.Element('reports')
    for key, rows in data_dict.items():
        parent = ET.SubElement(root, key)
        for row in rows:
            item = ET.SubElement(parent, 'item')
            for k, v in row.items():
                child = ET.SubElement(item, k)
                child.text = str(v)
    return ET.tostring(root, encoding='unicode')

def normalize_row(row: dict) -> dict:
    """Конвертирует Decimal→float для JSON, если нужно."""
    from decimal import Decimal
    normalized = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            normalized[k] = float(v)
        else:
            normalized[k] = v
    return normalized

def normalize_reports(reports: dict) -> dict:
    return {
        name: [normalize_row(r) for r in rows]
        for name, rows in reports.items()
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--students', required=True, help="Путь к файлу студентов (.json или .csv)")
    parser.add_argument('--rooms',    required=True, help="Путь к файлу комнат    (.json или .csv)")
    parser.add_argument('--format',   choices=['json','xml'], default='json', help="Выходной формат")
    args = parser.parse_args()

    db = PostgresDB()
    loader = DataLoader()
    loader.load(args.rooms, args.students, db)

    analytics = Analytics(db)
    reports = {
        'counts':           analytics.rooms_counts(),
        'lowest_avg_age':   analytics.lowest_avg_age(),
        'max_age_diff':     analytics.max_age_diff(),
        'mixed_gender':     analytics.mixed_gender(),
    }

    if args.format == 'json':
        # если нужны настоящие числа, раскомментировать:
        # reports = normalize_reports(reports)
        print(to_json(reports))
    else:
        print(to_xml(reports))

if __name__ == '__main__':
    main()
