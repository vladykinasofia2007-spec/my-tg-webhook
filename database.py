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
    #Таблица с ID всех пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()
    #Функция для добавления нового пользователя в базу
    def add_user(chat_id: int):
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)",(chat_id,))
        conn.commit()
        conn.close()

    def get_all_users():
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    def get_schedule_by_day(day: str, current_parity: str):
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT pair_time, subject, parity
            FROM schedule
            WHERE day_of_week = ? AND (parity = ? OR parity = 'Обе')
            ORDER BY pair_time
        """, (day, current_parity))
        rows = cursor.fetchall()
        conn.close()
        return rows        
    
    # Расписание ГУАП с учетом четности недель
    test_data = [
        # Вторник
        ("Вторник", "11:10", "Философия (Лекция)", "Нечетная"),
        ("Вторник", "15:10", "Математический анализ (Практика)", "Нечетная"),
        ("Вторник", "17:00", "Математический анализ (Практика)", "Нечетная"),
        # Понедельник 
        ("Понедельник", "09:30", "Физика (Лекция)", "Обе"),
        ("Понедельник", "11:10", "Основы программирования (Лабораторная)", "Четная"),
        ("Понедельник", "11:10", "История России (Практика)", "Нечетная"),
        ("Понедельник", "13:00", "Основы программирования (Лекция)", "Обе"),
        # Среда
        ("Среда", "9:30", "Физика (Лабораторная)", "Четная"),
        ("Среда", "11:10", "История России (Лекция)", "Обе"),
        ("Среда", "13:00", "Философия (Практика)", "Четная"),
        ("Среда", "15:10", "Дискретная математика (Практика)", "Нечетная"),
        #Четверг
        ("Четверг", "15:10", "Математический анализ (Лекция)", "Обе"),
        ("Четверг", "17:00", "Физическая культура (Практика)", "Обе"),
        #Пятница
        ("Пятница", "11:10", "Дискретная математика (Лекция)", "Обе"),
        ("Пятница", "17:00", "Иностранный язык (Практика)", "Обе"),
        #Суббота
        ("Суббота", "15:10", "Основы программирования (Практика)", "Четная"),
        ("Суббота", "17:00", "Основы программирования (Практика)", "Четная"),
        ("Суббота", "18:40", "Учебная практика (Практика)", "Четная"),
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
