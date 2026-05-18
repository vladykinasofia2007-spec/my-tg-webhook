import sqlite3

def init_db():
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    
    # Создаем таблицу, если её нет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT NOT NULL,
            pair_time TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    """)
    
    # Очищаем старые данные, чтобы при перезапусках они не дублировались
    cursor.execute("DELETE FROM schedule")
    
    # Твои реальные пары из ГУАП (каждый кортеж строго разделен запятой!)
    test_data = [
        ("Вторник", "15:10", "Математический анализ (Практика)"),
        ("Вторник", "17:00", "Математический анализ (Практика)"),
        ("Понедельник", "09:30", "Информатика (Лекция)"),
        ("Среда", "11:10", "Физика (Лабораторная)")
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

if __name__ == "__main__":
    init_db()
    print("База данных SQLite успешно создана!")
