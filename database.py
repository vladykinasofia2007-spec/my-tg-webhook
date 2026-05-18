import sqlite3


def init_db():
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()

    # Создаем таблицу расписания
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT NOT NULL,
            pair_time TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    """)

    # Заполняем тестовыми данными, если таблица пустая
    cursor.execute("SELECT COUNT(*) FROM schedule")
    if cursor.fetchone()[0] == 0:
        test_data = [
            ("Понедельник", "09:30", "Физика (Лекция)"),
            ("Понедельник", "11:10", "История России (Практика)"),
            ("Вторник", "11:10", "Философия (Лекция"),
            ("Вторник", "15:10", "Математический анализ (Практика)")
            ("Вторник", "17:00", "Математический анализ (Практика)")
            ("Среда", "9:30", "Физика (Лабораторная)")
        ]
        cursor.executemany("INSERT INTO schedule (day_of_week, pair_time, subject) VALUES (?, ?, ?)", test_data)
        conn.commit()
    conn.close()


def get_schedule_by_day(day: str):
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("SELECT pair_time, subject FROM schedule WHERE day_of_week = ?", (day,))
    rows = cursor.fetchall()
    conn.close()
    return rows


if name == "__main__":
    init_db()
    print("База данных SQLite успешно создана и заполнена!")
