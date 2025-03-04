import requests

BASE_URL = "https://marketplace-api.wildberries.ru/api/v3"

def get_order_by_id(api_key, order_id):
    url = f"{BASE_URL}/orders"
    headers = {"Authorization": api_key}
    params = {
        "limit": 1000,
        "next": 0,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return None, f"Ошибка при получении данных о заказе: {response.status_code}"

    orders = response.json().get("orders", [])
    for order in orders:
        if str(order['id']) == str(order_id):
            return order, None

    return None, "Заказ не найден\nУважаемый пользователь, к сожалению, мы не смогли найти заказ по указанным данным.\n\nПроверьте правильность информации и" \
            "попробуйте еще раз. Если проблема сохраняется, свяжитесь с нашей поддержкой для помощи."

def get_order_status(api_key, order_id):
    url = f"{BASE_URL}/orders/status"
    headers = {"Authorization": api_key}
    payload = {"orders": [int(order_id)]}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return None, f"Ошибка получения статуса: {response.status_code}"

    statuses = response.json().get("orders", [])
    if not statuses:
        return None, "Статус не найден"

    return statuses[0], None

def get_product_info(nm_id):
    url = "https://card.wb.ru/cards/v2/detail"
    params = {"nm": nm_id}

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, "Ошибка получения товара"

    products = response.json().get("data", {}).get("products", [])
    if not products:
        return None, "Товар не найден"

    product = products[0]
    return {
        "name": product['name'],
        "brand": product['brand'],
        "link": f"https://www.wildberries.ru/catalog/{nm_id}/detail.aspx"
    }, None

def get_feedbacks(nm_id):
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
    params = {
        "nmId": nm_id,
        "take": 50,
        "skip": 0,
        "isAnswered": "false",
        "order": "dateDesc"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, "Ошибка получения отзывов"

    return response.json().get("data", {}).get("feedbacks", []), None

def find_review_for_sku(feedbacks, skus):
    skus = [str(sku) for sku in skus]  # Приводим к строкам для надежности
    for feedback in feedbacks:
        if str(feedback.get('lastOrderShkId')) in skus:
            return feedback
    return None
