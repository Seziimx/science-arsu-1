import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Таблица факультетов
c.execute("""
CREATE TABLE IF NOT EXISTS faculties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

# Добавляем факультеты
faculties = [
    "Шетел тілдері факультеті",
    "Физика-математика факультеті",
    "Техникалық факультет",
    "Экономика және құқық факультеті",
    "Жаратылыстану факультеті",
    "Тарих факультеті",
    "Педагогика факультеті",
    "Филология факультеті",
    "Кәсіби-шығармашылық факультеті",
    "Сырттай оқыту факультеті"
]

for faculty in faculties:
    c.execute("INSERT INTO faculties (name) VALUES (?)", (faculty,))

conn.commit()
conn.close()
