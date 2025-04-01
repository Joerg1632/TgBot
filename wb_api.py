"""
wb_api.py

Методы для работы с Wildberries API — получение информации о заказах, товарах, отзывах и статусах.
"""

import requests
from utils import check_cashback_payment

BASE_URL = "https://marketplace-api.wildberries.ru/api/v3"
CONTENT_API_URL = "https://content-api.wildberries.ru/content/v2/get/cards/list"
OBJECTS_API_URL = "https://content-api.wildberries.ru/content/v2/object/all"
PRICES_API_URL = "https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter"
FEEDBACKS_API_URL = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
WB_ORDERS_API_URL = "https://marketplace-api.wildberries.ru/api/v3/orders"

def get_order_by_shk(api_key, shk_id):
    """
    Получает заказы с Wildberries и проверяет наличие штрихкода.
    """
    headers = {"Authorization": api_key}
    next_page = 0
    limit = 1000

    while True:
        params = {
            "limit": limit,
            "next": next_page
        }

        response = requests.get(WB_ORDERS_API_URL, headers=headers, params=params)
        if response.status_code != 200:
            return None, f"Ошибка при получении данных: {response.status_code}"

        data = response.json()
        orders = data.get("orders", [])

        if not orders:
            break  # Если заказов нет, завершаем цикл

        for order in orders:
            skus = order.get("skus", [])

            # Приводим все к строкам для корректного сравнения
            skus_str = [str(sku) for sku in skus]

            if str(shk_id) in skus_str:
                return order, None  # Если нашли — возвращаем заказ

        next_page = data.get("next", 0)  # Получаем `next`
        if next_page == 0:
            break  # Если `next_page` = 0, значит, страниц больше нет

    return None, "Заказ с таким штрихкодом не найден"


def get_feedback_by_shk(api_key, shk_id):
    """
    Получает единственный отзыв по штрих-коду товара (ShkId).
    Добавляет проверку, был ли уже выплачен кэшбэк за этот отзыв.
    """
    # Проверка на уже выплаченный кэшбэк
    if check_cashback_payment(shk_id):
        return None, "Кэшбэк за этот отзыв уже был выплачен ранее"

    headers = {"Authorization": api_key}
    try:
        shk_id = int(shk_id)
    except ValueError:
        return None, "❌ Некорректный формат штрихкода!"

    for answered in [False, True]:  # Проверяем как отвеченные, так и неотвеченные отзывы
        params = {
            "take": 5000,  # Берем максимум отзывов
            "skip": 0,
            "isAnswered": str(answered).lower(),
            "order": "dateDesc"
        }

        response = requests.get(FEEDBACKS_API_URL, headers=headers, params=params)
        if response.status_code != 200:
            return None, f"❌ Ошибка получения отзывов: {response.status_code}"

        feedbacks = response.json().get("data", {}).get("feedbacks", [])

        # Ищем отзыв с нужным `shkId`
        for feedback in feedbacks:
            if int(feedback.get('lastOrderShkId', 0)) == shk_id:
                return feedback, None  # Возвращаем первый найденный отзыв

    return None, "❌ Отзыв по этому штрихкоду не найден!"

#Для сценария обработки ошибок
def get_product_info(api_key, nm_id):
    """
    Получает информацию о товаре по его `nmId`: название, бренд, цена, категория.
    """
    headers = {"Authorization": api_key}

    payload = {
        "settings": {
            "cursor": {"limit": 1},  # Запрашиваем только 1 карточку
            "filter": {
                "textSearch": str(nm_id)  # Ищем карточку по nmID
            }
        }
    }

    # Получаем карточку товара
    response = requests.post(CONTENT_API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        return None, f"Ошибка получения карточки товара: {response.status_code}"

    cards = response.json().get("cards", [])
    if not cards:
        return None, "Карточка товара не найдена"

    card_info = cards[0]

    # Получаем цену
    params = {
        "filterNmID": nm_id,  # Поиск по артикулу WB
        "limit": 1  # Нам нужен один товар
    }
    response = requests.get(PRICES_API_URL, headers=headers, params=params)

    if response.status_code != 200:
        return None, f"Ошибка получения цены: {response.status_code}"

    data = response.json().get("data", {}).get("listGoods", [])
    product_price_info = data[0]  # Берем первый найденный товар
    # Получаем категории товаров
    params = {
        "limit": 1000,  # Максимум товаров, можно уменьшить если нужно
        "locale": "ru",  # Русский язык
    }
    response = requests.get(OBJECTS_API_URL, headers=headers, params=params)
    if response.status_code != 200:
        print(response.status_code)
        return None, f"Ошибка получения категорий: {response.status_code}"

    categories = response.json().get("data", [])
    subject_id = card_info.get("subjectID")
    category_info = next((c for c in categories if c.get("subjectID") == subject_id), {})

    sizes = product_price_info.get("sizes", [])
    size_info = sizes[0] if sizes else {}

    return {
        "name": card_info.get("title", "Нет названия"),
        "brand": card_info.get("brand", "Нет бренда"),
        "category": f"{category_info.get('parentName', 'Нет категории')} / {category_info.get('subjectName', 'Нет категории')}",
        "price": size_info.get("discountedPrice", "Нет цены"),
        "old_price": size_info.get("price", "Нет старой цены"),
        "discount": product_price_info.get("discount", "Нет скидки"),
        "link": f"https://www.wildberries.ru/catalog/{nm_id}/detail.aspx"
    }, None


def get_order_with_full_product_info(api_key, shk_id):
    """
    Получает информацию о заказе по штрих-коду (ShkId), включая товар и категорию.
    """
    feedback, error = get_feedback_by_shk(api_key, shk_id)
    if error:
        return None, error

    if not feedback:
        return None, "Отзывов по данному штрих-коду не найдено."
    nm_id = feedback["productDetails"]["nmId"]

    product_info, error = get_product_info(api_key, nm_id)
    print(feedback,product_info)
    if error:
        return None, error

    return {
        "review": feedback,
        "product_info": product_info
    }, None