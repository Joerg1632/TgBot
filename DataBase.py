import sqlite3

def get_db_connection():
    """
    Подключается к базе данных.
    """
    conn = sqlite3.connect('requests.db')
    return conn

def init_db():
    """
    Инициализирует базу данных, создает таблицы, если их нет.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица для жалоб
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

    # Таблица для кэшбэков
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

    conn.commit()
    conn.close()

def add_complaint(data):
    """
    Добавляет жалобу в базу данных.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO complaints (order_number, product_name, problem_type, description, user_name, user_phone, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('order_number'),
        data.get('product_name'),
        data.get('problem_type'),
        data.get('description'),
        data.get('user_name'),
        data.get('user_phone'),
        'В работе'
    ))

    complaint_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return complaint_id

def add_cashback(data):
    """
    Добавляет заявку на кэшбэк в базу данных.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO cashbacks (order_number, product_name, review_rating, review_date, user_name, user_phone, bank_name, cashback_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('order_number'),
        data.get('product_name'),
        data.get('review_rating'),
        data.get('review_date'),
        data.get('user_name'),
        data.get('user_phone'),
        data.get('bank_name'),
        'В работе'
    ))

    cashback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cashback_id

def get_all_complaints():
    """
    Возвращает все жалобы из базы данных.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM complaints')
    complaints = cursor.fetchall()
    conn.close()
    return complaints

def get_all_cashbacks():
    """
    Возвращает все заявки на кэшбэк из базы данных.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cashbacks')
    cashbacks = cursor.fetchall()
    conn.close()
    return cashbacks

def update_status(table, request_id, status):
    """
    Обновляет статус заявки.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE {table} SET status = ? WHERE id = ?
    ''', (status, request_id))
    conn.commit()
    conn.close()