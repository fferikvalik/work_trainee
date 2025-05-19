# tests/test_cli.py

import unittest
import subprocess
import json
import xml.etree.ElementTree as ET
import os

class TestCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Путь к вашим тестовым данным
        cls.rooms_file   = os.path.abspath("data/rooms.json")
        cls.students_file= os.path.abspath("data/students.json")
        cls.base_cmd = [
            # Запускаем модуль cli.main из корня task1
            "python", "-m", "cli.main",
            "--rooms", cls.rooms_file,
            "--students", cls.students_file,
        ]

    def test_json_stdout(self):
        """Проверяем вывод JSON в stdout без --output."""
        cmd = self.base_cmd + ["--format", "json"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        # Успешный код выхода
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # Парсим JSON
        data = json.loads(proc.stdout)
        # Ожидаемые разделы отчётов
        for section in ("counts","lowest_avg_age","max_age_diff","mixed_gender"):
            self.assertIn(section, data)
            self.assertIsInstance(data[section], list)

    def test_xml_stdout(self):
        """Проверяем вывод XML в stdout без --output."""
        cmd = self.base_cmd + ["--format", "xml"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # Парсим XML
        root = ET.fromstring(proc.stdout)
        self.assertEqual(root.tag, "reports")
        # Должны быть 4 секции
        tags = {child.tag for child in root}
        self.assertTrue({"counts","lowest_avg_age","max_age_diff","mixed_gender"}.issubset(tags))

    def test_output_file_json(self):
        """Проверяем запись в файл JSON (--output)."""
        out = "test_output.json"
        if os.path.exists(out):
            os.remove(out)

        cmd = self.base_cmd + ["--format", "json", "--output", out]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        # Файл был создан
        self.assertTrue(os.path.exists(out))
        with open(out, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("counts", data)
        os.remove(out)

    def test_output_file_xml(self):
        """Проверяем запись в файл XML (--output)."""
        out = "test_output.xml"
        if os.path.exists(out):
            os.remove(out)

        cmd = self.base_cmd + ["--format", "xml", "--output", out]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(os.path.exists(out))
        tree = ET.parse(out)
        self.assertEqual(tree.getroot().tag, "reports")
        os.remove(out)

if __name__ == "__main__":
    unittest.main()
