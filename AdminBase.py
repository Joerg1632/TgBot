from DataBase import get_all_complaints, get_all_cashbacks, update_status, get_db_connection

def get_all_requests():
    """
    Возвращает все жалобы и заявки на кэшбэк.
    """
    complaints = get_all_complaints()
    cashbacks = get_all_cashbacks()
    return complaints, cashbacks

def update_request_status(table, request_id, status):
    """
    Обновляет статус заявки.
    """
    update_status(table, request_id, status)

def get_request_details(table, request_id):
    """
    Возвращает детали заявки по её ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM {table} WHERE id = ?', (request_id,))
    request = cursor.fetchone()
    conn.close()
    return request