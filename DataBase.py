import sqlite3

# Подключаемся к базе данных (если базы нет, она будет создана)
conn = sqlite3.connect('requests.db')  # Создание базы данных в текущей директории
cursor = conn.cursor()

# Создаем таблицу для жалоб
cursor.execute('''
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL,
    product_name TEXT NOT NULL,
    problem_type TEXT NOT NULL,
    description TEXT,
    user_name TEXT,
    user_phone TEXT,
    status TEXT DEFAULT 'В работе',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Создаем таблицу для кешбэков
cursor.execute('''
CREATE TABLE IF NOT EXISTS cashbacks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL,
    product_name TEXT NOT NULL,
    review_rating INTEGER NOT NULL,
    review_date TIMESTAMP NOT NULL,
    user_name TEXT,
    user_phone TEXT,
    bank_name TEXT,
    cashback_status TEXT DEFAULT 'В работе',
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()
