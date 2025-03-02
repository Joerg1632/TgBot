import requests

# Базовый URL для API Wildberries
BASE_URL = "https://suppliers-api.wildberries.ru"

def get_headers(api_key):
    """
    Возвращает заголовки для запросов к API Wildberries.
    """
    return {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }

def get_orders(api_key, date_from, date_to):
    """
    Получает список заказов за указанный период.
    """
    url = f"{BASE_URL}/api/v1/orders"
    params = {
        'dateFrom': date_from,  # Дата начала периода (в формате ГГГГ-ММ-ДД)
        'dateTo': date_to       # Дата окончания периода (в формате ГГГГ-ММ-ДД)
    }
    headers = get_headers(api_key)

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as e:
        return None, f"Ошибка при получении заказов: {e}"

def get_product_info(api_key, nm_id):
    """
    Получает информацию о товаре по его артикулу (nmId).
    """
    url = f"{BASE_URL}/api/v1/products/{nm_id}"
    headers = get_headers(api_key)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as e:
        return None, f"Ошибка при получении информации о товаре: {e}"

def get_feedbacks(api_key, nm_id, take=5):
    """
    Получает отзывы на товар по его артикулу (nmId).
    """
    url = f"{BASE_URL}/api/v1/feedbacks"
    params = {
        'imtId': nm_id,  # Артикул товара
        'take': take      # Количество отзывов
    }
    headers = get_headers(api_key)

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as e:
        return None, f"Ошибка при получении отзывов: {e}"