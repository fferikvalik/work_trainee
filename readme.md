# Task 1 — ETL и аналитика для комнат и студентов

Первое задание в рамках trainee-программы. Реализация ETL-процесса для загрузки данных о студентах и комнатах, выполнение аналитических SQL-запросов и экспорт результатов в JSON или XML.

---

## 📁 Структура

task1/
├── cli/ # Точка входа и CLI-интерфейс
│ └── main.py
├── db/ # Работа с PostgreSQL
│ └── postgres.py
├── etl/ # Загрузка данных
│ ├── inserter.py
│ └── loader.py
├── queries/ # SQL-запросы
│ └── analytics.py
├── data/ # Входные JSON/CSV файлы
│ ├── rooms.json
│ └── students.json
├── indexes.sql # SQL-индексы для ускорения аналитики
├── requirements.txt # Зависимости
├── .env # Переменные окружения (не коммитить!)
└── README.md


---

## 🚀 Функциональность

- Загрузка данных студентов и комнат из `.json` или `.csv` файлов.
- Сохранение данных в PostgreSQL (связь `many-to-one`: студенты → комнаты).
- Выполнение аналитических SQL-запросов:
  1. Кол-во студентов в каждой комнате.
  2. 5 комнат с самым низким средним возрастом студентов.
  3. 5 комнат с наибольшей разницей в возрасте студентов.
  4. Комнаты с разнополыми студентами.
- Вывод результата в формате `JSON` или `XML`.
- Соблюдение принципов ООП и SOLID.
- Без использования ORM (только чистый SQL).

---

## ⚙️ Установка

```bash
git clone <REPO_URL> work_trainee
cd work_trainee/task1
python3 -m venv .venv
source .venv/bin/activate      # Для macOS/Linux
# .venv\Scripts\activate.bat   # Для Windows
pip install -r requirements.txt
