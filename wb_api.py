import requests

BASE_URL = "https://marketplace-api.wildberries.ru/api/v3"
CONTENT_API_URL = "https://content-api.wildberries.ru/content/v2/get/cards/list"
OBJECTS_API_URL = "https://content-api.wildberries.ru/content/v2/object/all"
PRICES_API_URL = "https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter"

def get_order_by_id(api_key, order_id):
    url = f"{BASE_URL}/orders"
    headers = {"Authorization": api_key}
    next_cursor = 0

    while True:
        params = {"limit": 1000, "next": next_cursor}
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return None, f"Ошибка при получении данных о заказе: {response.status_code}"

        data = response.json()
        orders = data.get("orders", [])
        if not orders:
            break  # Заказы кончились

        for order in orders:
            if str(order['id']) == str(order_id):
                return order, None

        next_cursor = data.get("next")  # Получаем следующую страницу
        if not next_cursor:
            break  # Достигли конца списка заказов

    return None, (
        "Заказ не найден\n"
        "Уважаемый пользователь, к сожалению, мы не смогли найти заказ по указанным данным.\n\n"
        "Проверьте правильность информации и попробуйте еще раз. "
        "Если проблема сохраняется, свяжитесь с нашей поддержкой для помощи."
    )

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


def get_feedbacks(nm_id):
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"

    all_feedbacks = []

    for answered in [False, True]:
        params = {
            "nmId": nm_id,
            "take": 2500,                     # половина на каждую группу
            "skip": 0,
            "isAnswered": str(answered).lower(),  # "true" или "false"
            "order": "dateDesc"
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return None, f"Ошибка получения отзывов (answered={answered}): {response.status_code}"

        feedbacks = response.json().get("data", {}).get("feedbacks", [])
        all_feedbacks.extend(feedbacks)

    return all_feedbacks, None


def find_review_for_sku(feedbacks, skus):
    skus = {int(sku) for sku in skus}  # Приводим все к числам для надежности
    for feedback in feedbacks:
        if feedback.get('lastOrderShkId') in skus:
            return feedback
    return None

# Для проблем
def get_order_with_full_product_info(api_key, order_id):
    order, error = get_order_by_id(api_key, order_id)
    if error:
        return None, error

    nm_id = order['nmId']

    card_info, error = get_product_card(api_key, nm_id)
    if error:
        return None, error

    product_info_list, error = get_product_prices(nm_id)
    if error:
        return None, error

    category_info_list, error = get_category_info()
    if error:
        return None, error

    card_info_list = [card_info]

    product_info = None
    for product in product_info_list:
        if product.get('nmID') == nm_id:
            product_info = product
            break

    if product_info is None:
        return None, "Product not found in product_info_list"

    size_info = product_info['sizes'][0]  # Берем первую размерную позицию

    subject_id = None
    for card in card_info_list:
        if card.get('nmID') == nm_id:
            subject_id = card.get('subjectID')
            break

    if subject_id is None:
        return None, "Subject ID not found in card_info_list"

    category_name = None
    parent_name = None
    for category in category_info_list:
        if category.get('subjectID') == subject_id:
            category_name = category.get('subjectName')
            parent_name = category.get('parentName')
            break

    if not category_name or not parent_name:
        return None, "Category or parent name not found for subjectID"

    full_product_info = {
        "name": card_info_list[0].get('title', 'Нет названия'),
        "brand": card_info_list[0].get('brand', 'Нет бренда'),
        "category": f"{parent_name} / {category_name}",
        "price": size_info['discountedPrice'],
        "old_price": size_info['price'],
        "discount": product_info['discount'],
        "link": f"https://www.wildberries.ru/catalog/{nm_id}/detail.aspx"
    }

    order['product_info'] = full_product_info
    return order, None

def get_product_prices(nm_id):
    response = requests.get(PRICES_API_URL, params={"filterNmID": nm_id, "limit": 1})
    if response.status_code != 200:
        return None, f"Ошибка получения цен: {response.status_code}"

    product_list = response.json().get("data", {}).get("listGoods", [])
    if not product_list:
        return None, "Цены не найдены"

    return product_list, None

def get_category_info():
    response = requests.get(OBJECTS_API_URL)
    if response.status_code != 200:
        return None, f"Ошибка получения категорий: {response.status_code}"

    return response.json().get("data", []), None

def get_product_card(api_key, nm_id):
    headers = {"Authorization": api_key}
    response = requests.post(CONTENT_API_URL, json={"settings": {"cursor": {"nmID": [nm_id]}}}, headers=headers)
    if response.status_code != 200:
        return None, f"Ошибка получения карточки товара: {response.status_code}"

    cards = response.json().get("cards", [])
    if not cards:
        return None, "Карточка товара не найдена"

    return cards[0], None
