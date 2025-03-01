import sqlite3

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('requests.db')
    return conn

def add_complaint(data):
    # Подключаемся к базе данных
    conn = get_db_connection()
    cursor = conn.cursor()

    # Добавляем жалобу в таблицу
    cursor.execute('''
        INSERT INTO complaints (order_number, product_name, problem_type, description, user_name, user_phone, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('barcode'),  # номер заказа
          data.get('product_info', {}).get('name', ''),  # название товара
          data.get('complaint_type'),  # тип проблемы
          data.get('description', ''),  # описание проблемы
          data.get('contact_info', '').split()[0],  # ФИО (предположим, что первое слово — это имя)
          data.get('contact_info', '').split()[1],  # телефон
          'В работе'))  # статус по умолчанию

    # Получаем ID последней вставленной записи
    complaint_id = cursor.lastrowid

    conn.commit()
    conn.close()

    # Возвращаем ID новой заявки
    return complaint_id


# Функция для добавления заявки на кешбэк
def add_cashback(order_number, product_name, review_rating, review_date, user_name, user_phone, bank_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cashbacks (order_number, product_name, review_rating, review_date, user_name, user_phone, bank_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (order_number, product_name, review_rating, review_date, user_name, user_phone, bank_name))
    conn.commit()
    conn.close()

# Функция для получения всех заявок (жалоб)
def get_all_complaints():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM complaints')
    complaints = cursor.fetchall()
    conn.close()
    return complaints

# Функция для получения всех заявок на кешбэк
def get_all_cashbacks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cashbacks')
    cashbacks = cursor.fetchall()
    conn.close()
    return cashbacks

# Функция для обновления статуса заявки
def update_status(table, request_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE {table} SET status = ? WHERE id = ?
    ''', (status, request_id))
    conn.commit()
    conn.close()
