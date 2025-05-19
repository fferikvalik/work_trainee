# etl/loader.py

import json
import csv
from typing import List, Dict

class DataLoader:
    @staticmethod
    def parse_rooms(path: str) -> List[Dict]:
        """Поддерживает JSON и CSV форматы для файлов комнат."""
        if path.endswith('.json'):
            with open(path, encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    raise ValueError(f"Файл {path} пустой")
                return json.loads(content)
        elif path.endswith('.csv'):
            rooms = []
            with open(path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rooms.append({
                        'id': int(row['id']),
                        'name': row['name']
                    })
            return rooms
        else:
            raise ValueError(f"Unsupported file format for rooms: {path}")

    @staticmethod
    def parse_students(path: str) -> List[Dict]:
        """Поддерживает JSON и CSV форматы для файлов студентов."""
        if path.endswith('.json'):
            with open(path, encoding='utf-8') as f:
                content = f.read()
                if not content.strip():
                    raise ValueError(f"Файл {path} пустой")
                return json.loads(content)
        elif path.endswith('.csv'):
            students = []
            with open(path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    students.append({
                        'id': int(row['id']),
                        'name': row['name'],
                        'birth_date': row['birth_date'],
                        'gender': row['gender'],
                        'room_id': int(row['room_id'])
                    })
            return students
        else:
            raise ValueError(f"Unsupported file format for students: {path}")

    def load(self, rooms_path: str, students_path: str, db):
        # Сначала создаём схему
        from etl.inserter import SchemaCreator
        SchemaCreator(db).create_tables()

        # Вставляем комнаты
        rooms = self.parse_rooms(rooms_path)
        for room in rooms:
            db.execute(
                "INSERT INTO rooms (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;",
                (room['id'], room['name'])
            )

        # Вставляем студентов
        students = self.parse_students(students_path)
        for stu in students:
            db.execute(
                "INSERT INTO students (id, name, birth_date, gender, room_id) "
                "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
                (stu['id'], stu['name'], stu['birth_date'], stu['gender'], stu['room_id'])
            )
