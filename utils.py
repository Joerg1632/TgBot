"""
utils.py

Вспомогательные функции для генерации номеров заявок и поиска данных.
"""

import time
from state import user_data

def generate_application_id():
    """
    Генерация уникального номера заявки на основе времени.
    """
    return str(int(time.time()))

def check_cashback_payment(shk_id):
    """
    Проверяет, был ли уже выплачен кэшбэк за данный штрих-код.
    Ищет среди всех заявок всех пользователей.
    """
    for user_id, data in user_data.items():
        if data.get('order_id') == shk_id and data.get('status') == 'реализовано':
            return True

        for order in data.get('previous_orders', []):
            if order.get('order_id') == shk_id and order.get('status') == 'реализовано':
                return True
    return False

def find_user_by_application_id(application_id, user_data):
    """
    Поиск заявки по application_id (ищет среди текущих и прошлых заявок).
    """
    for user_id, data in user_data.items():
        if data.get('application_id') == application_id:
            return user_id, data

        for old_data in data.get("previous_orders", []):
            if old_data.get('application_id') == application_id:
                return user_id, old_data 
    return None, None


def find_cashback_by_shk_id(user_id, shk_id):
    """
    Проверяет, есть ли уже заявка на кэшбэк по указанному штрих-коду (shk_id).
    Проверяет как активную заявку, так и прошлые заявки.
    """
    if user_id not in user_data:
        return None

    if user_data[user_id].get("order_id") == shk_id:
        return user_data[user_id]

    for prev_order in user_data[user_id].get("previous_orders", []):
        if prev_order.get("order_id") == shk_id:
            return prev_order

    return None


def generate_admin_application_text(data):
    """
    Формирование текста заявки для отправки администратору.
    """
    product = data['product']
    description = data.get('description', 'Описание отсутствует')
    return (
        f"⚠️ Обращение №{data['application_id']}\n"
        f"📦 Номер заказа: {data['order_id']}\n"
        f"📛 Проблема: {data['problem_type']}\n"
        f"📝 Описание: {description}\n"
        f"📅 Дата создания: {data['created_at']}\n"
        f"🔖 Статус: *{data['status']}*\n\n"
        f"🏷️ Товар: {product['name']}\n"
        f"🏷️ Бренд: {product['brand']}\n"
        f"💰 Цена: {product['price']} р\n"
        f"🔗 [Ссылка на товар]({product['link']})\n"
        f"📲 [Связаться с клиентом](tg://user?id={data['user_id']})\n"
    )
