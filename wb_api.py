import requests

# Функция получения данных о заказе по его номеру (orderId)
def get_product_by_order_id(api_key, order_id):
    url = f"https://suppliers-api.wildberries.ru/api/v3/orders/{order_id}"
    headers = {"Authorization": api_key}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None, f"Ошибка получения данных о заказе: {response.status_code} - {response.text}"

    data = response.json()
    if not data.get("orders"):
        return None, "Заказ не найден"

    order = data['orders'][0]
    nm_id = order['skus'][0]['nmId']

    product_info, error = get_product_info(nm_id)
    if error:
        return None, error

    product_info['order_date'] = order['createdAt']  # Дата заказа
    product_info['imtId'] = order['skus'][0]['imtId']  # добавляем imtId сразу
    return product_info, None


# Функция получения информации о товаре по nmId
def get_product_info(nm_id):
    url = "https://card.wb.ru/cards/v2/detail"
    params = {"nm": nm_id}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None, f"Ошибка получения данных о товаре: {response.status_code}"

    data = response.json()

    if not data.get('data', {}).get('products'):
        return None, "Товар не найден в Wildberries"

    product = data['data']['products'][0]

    return {
        "nmId": nm_id,
        "name": product['name'],
        "category": product.get('subjName', 'Неизвестно'),
        "brand": product['brand'],
        "price": product['salePriceU'] / 100,
        "old_price": product['priceU'] / 100,
        "discount": product['sale'],
        "link": f"https://www.wildberries.ru/catalog/{nm_id}/detail.aspx"
    }, None


def get_feedbacks(imt_id):
    url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
    params = {
        "imtId": imt_id,  # теперь передаем корректный параметр
        "take": 5,
        "isAnswered": "false"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None, f"Ошибка получения отзывов: {response.status_code}"

    data = response.json()
    return data.get("feedbacks", []), None

