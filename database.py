import sqlite3

def init_db():
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    
    # Удаляем старую таблицу, чтобы пересоздать её с новым столбцом parity
    cursor.execute("DROP TABLE IF EXISTS schedule")
    
    # Создаем таблицу с новым текстовым полем parity
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day_of_week TEXT NOT NULL,
            pair_time TEXT NOT NULL,
            subject TEXT NOT NULL,
            parity TEXT NOT NULL
        )
    """)
    
    # Расписание ГУАП с учетом четности недель
    test_data = [
        # Вторник
        ("Вторник", "15:10", "Математический анализ (Практика)", "Четная"),
        ("Вторник", "17:00", "Математический анализ (Практика)", "Нечетная"),
        # Понедельник (пара идет каждую неделю)
        ("Понедельник", "09:30", "Информатика (Лекция)", "Обе"),
        # Среда
        ("Среда", "11:10", "Физика (Лабораторная)", "Четная")
    ]
    
    cursor.executemany("INSERT INTO schedule (day_of_week, pair_time, subject, parity) VALUES (?, ?, ?, ?)", test_data)
    conn.commit()
    conn.close()

# Изменяем функцию запроса: теперь она фильтрует пары по дню и по текущей четности
def get_schedule_by_day(day: str, current_parity: str):
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    
    # Выбираем пары, у которых неделя совпадает с текущей ИЛИ стоит "Обе"
    cursor.execute("""
        SELECT pair_time, subject, parity 
        FROM schedule 
        WHERE day_of_week = ? AND (parity = ? OR parity = 'Обе')
        ORDER BY pair_time
    """, (day, current_parity))
    
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("База данных SQLite успешно обновлена (добавлена чётность)!")
