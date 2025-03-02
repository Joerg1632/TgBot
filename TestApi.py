import requests

url = "https://suppliers-api.wildberries.ru/api/v1/orders"
params = {
    'dateFrom': '2023-10-01',  # Дата начала периода
    'dateTo': '2023-10-31'      # Дата окончания периода
}
response = requests.get(url, headers=headers, params=params)
print(response.json())