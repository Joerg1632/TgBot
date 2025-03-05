import time

def generate_application_id():
    return str(int(time.time()))

def find_user_by_application_id(application_id, user_data):
    for user_id, data in user_data.items():
        if data.get('application_id') == application_id:
            return user_id, data
    return None, None

def generate_admin_application_text(data):
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