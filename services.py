from aiogram import Bot, types
from config import ADMIN_ID
from state import user_data
from utils import generate_application_id
from keyboards import get_cashback_status_keyboard, main_inline_keyboard
from datetime import datetime, timezone

async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name
    await message.reply(
        f"Здравствуйте, {user_name}! 👋\n\n"
        "Я ваш виртуальный помощник, который поможет вам получить кэшбэк за отзыв или решить проблемы с заказом.",
        reply_markup=main_inline_keyboard
    )

async def send_cashback_to_admin(user_id, bot: Bot):
    data = user_data[user_id]
    application_id = generate_application_id()

    data.update({
        "application_id": application_id,
        "application_type": "cashback",
        "status": "в работе",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id
    })

    product = data['product']
    review = data['review']
    order = data['order']

    sale_date = datetime.fromisoformat(order['createdAt']).replace(tzinfo=timezone.utc)
    days_passed = (datetime.now(timezone.utc) - sale_date).days
    can_pay = "ДА" if days_passed >= 14 else "НЕТ"

    text = (
        f"📋 Заявка на кешбэк №{application_id}\n"
        f"📦 Номер заказа: {order['id']}\n"
        f"🏷️ Товар: {product['name']} ({product['brand']})\n"
        f"⭐️ Оценка клиента: {review['productValuation']}⭐️\n"
        f"🛒 Дата продажи: {sale_date.date()}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏦 Банк: {data['bank']}\n"
        f"💸 Начислить кешбэк: {can_pay}\n"
    )

    msg = await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    data['admin_message_id'] = msg.message_id
    user_data[user_id] = data

    await bot.send_message(ADMIN_ID, "Выберите решение по кешбэку:", reply_markup=get_cashback_status_keyboard(application_id))
