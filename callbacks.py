from aiogram import types, Dispatcher, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from services import send_welcome
from state import user_data
from utils import generate_application_id, find_user_by_application_id
from keyboards import main_inline_keyboard, back_keyboard, back_to_main_keyboard, complaint_types, get_cashback_status_keyboard
from datetime import datetime, timezone

async def handle_menu(callback: types.CallbackQuery):
    if callback.data == "get_cashback":
        user_data[callback.from_user.id] = {'step': 'enter_order'}
        await callback.message.edit_text(
            "Чтобы получить кешбек, введите номер вашего заказа с упаковки! 👇",
            reply_markup=back_keyboard
        )
    elif callback.data == "solve_problem":
        user_data[callback.from_user.id] = {'step': 'problem_order'}
        await callback.message.edit_text(
            "✍️ Введите номер вашего заказа, который указан на упаковке товара. Это поможет нам разобраться с вашей проблемой. 📦",
            reply_markup=back_keyboard
        )
    await callback.answer()

async def handle_back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Я ваш виртуальный помощник, который поможет вам получить кэшбэк за отзыв или решить проблемы с заказом. Выберите действие:",
        reply_markup=main_inline_keyboard
    )
    user_data.pop(callback.from_user.id, None)
    await callback.answer()

async def confirm_product(callback: types.CallbackQuery):
    user_data[callback.from_user.id]['step'] = 'choose_problem'

    await callback.message.edit_text(
        "📋 Выберите, с чем у вас возникла проблема:",
        reply_markup=InlineKeyboardMarkup().add(
            *[InlineKeyboardButton(pt, callback_data=f"problem_{pt}") for pt in complaint_types]
        )
    )
    await callback.answer()

async def retry_order_input_problem(callback: types.CallbackQuery):
    user_data[callback.from_user.id] = {'step': 'problem_order'}
    await callback.message.edit_text(
        "✍️ Введите номер вашего заказа, который указан на упаковке товара. Это поможет нам разобраться с вашей проблемой. 📦",
        reply_markup=back_to_main_keyboard
    )
    await callback.answer()

async def retry_order_input_cash(callback: types.CallbackQuery):
    user_data[callback.from_user.id] = {'step': 'problem_order'}
    await callback.message.edit_text(
        "Чтобы получить кешбек, введите номер вашего заказа с упаковки! 👇",
        reply_markup=back_to_main_keyboard
    )
    await callback.answer()

async def process_problem_type(callback: types.CallbackQuery):
    user_data[callback.from_user.id]['problem_type'] = callback.data.replace("problem_", "")
    user_data[callback.from_user.id]['step'] = 'enter_name'
    await callback.message.answer("📛 Пожалуйста, введите ваше ФИО:")
    await callback.answer()


async def send_cashback_to_admin(user_id, bot):
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
        f"🗓️ Дата отзыва: {review['createdDate']}\n"
        f"🛒 Дата продажи: {sale_date.date()}\n"
        f"📅 Дней с момента продажи: {days_passed}\n"
        f"💬 Отзыв: {review.get('text', 'Отзыв без текста')}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏦 Банк: {data['bank']}\n"
        f"💸 Начислить кешбэк: {can_pay}\n"
        f"📲 [Связаться с клиентом](tg://user?id={user_id})"
    )

    message = await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")
    data['admin_message_id'] = message.message_id

    user_data[user_id] = data

    await bot.send_message(ADMIN_ID, "Выберите решение по кешбэку:", reply_markup=get_cashback_status_keyboard(application_id))


async def finalize_problem_report(callback: types.CallbackQuery, bot:Bot):
    user_id = callback.from_user.id
    data = user_data.get(user_id)

    if not data:
        await callback.answer("Ошибка: заявка не найдена.")
        return

    application_id = generate_application_id()
    data.update({
        'application_id': application_id,
        'status': 'в работе',
        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'user_id': user_id
    })

    await callback.message.answer(
        f"✅ Заявка принята!\n"
        f"📄 Номер обращения: {application_id}\n"
        f"⏳ Ожидаемое время ответа: в течение 24 часов"
    )

    await send_problem_report_to_admin(user_id,bot)
    await callback.answer()

async def change_application_status(callback: types.CallbackQuery, bot):
    _, status, application_id = callback.data.split(":")
    user_id, data = find_user_by_application_id(application_id, user_data)

    if not data:
        await callback.answer("Заявка не найдена.")
        return

    data['status'] = status
    user_data[user_id] = data

    new_text = (
        f"⚠️ Обращение №{data['application_id']}\n"
        f"📦 Номер заказа: {data['order_id']}\n"
        f"📛 Проблема: {data['problem_type']}\n"
        f"📝 Описание: {data['description'].strip() or 'Описание не указано'}\n"
        f"📅 Дата создания: {data['created_at']}\n\n"
        f"🏷️ Товар: {data['product']['name']}\n"
        f"🏷️ Бренд: {data['product']['brand']}\n"
        f"💰 Цена: {data['product']['price']} р\n"
        f"🔗 [Ссылка на товар]({data['product']['link']})\n"
        f"📲 [Связаться с клиентом](tg://user?id={user_id})\n"
        f"🔖 Статус: *{status}*"
    )

    await bot.edit_message_text(new_text, ADMIN_ID, data['admin_message_id'], parse_mode="Markdown", disable_web_page_preview=True)

    status_messages = {
        "закрыто": "✅ Ваша заявка закрыта и решена.",
        "не_реализовано": "❌ Ваша заявка закрыта без решения."
    }
    await bot.send_message(user_id, f"ℹ️ Статус вашей заявки №{application_id} изменен:\n{status_messages[status]}")
    await callback.answer("Статус обновлён.")


async def change_cashback_status(callback: types.CallbackQuery, bot):
    _, status, application_id = callback.data.split(":")
    user_id, data = find_user_by_application_id(application_id,user_data)

    if not data:
        await callback.answer("Заявка не найдена.")
        return

    data['status'] = status
    text = f"📋 Заявка на кешбэк (обновлено)\n\n{data['product']['name']}\n🔖 Статус: *{status}*"
    await bot.edit_message_text(text, ADMIN_ID, data['admin_message_id'], parse_mode="Markdown")

    messages = {
        "реализовано": "✅ Ваш кешбэк выплачен!",
        "не_реализовано": "❌ В кешбэке отказано. Свяжитесь с поддержкой, если есть вопросы."
    }
    await bot.send_message(user_id, f"ℹ️ Статус заявки на кешбэк: {messages[status]}")
    await callback.answer()

async def send_problem_report_to_admin(user_id, bot):
    data = user_data.get(user_id)
    product = data['product']

    main_text = (
        f"⚠️ Новая заявка\n"
        f"📄 Номер обращения: {data['application_id']}\n"
        f"📦 Номер заказа: {data['order_id']}\n"
        f"📛 Проблема: {data['problem_type']}\n"
        f"📝 Описание: {data['description'].strip() or 'Описание не указано'}\n"
        f"📅 Дата создания: {data['created_at']}\n"
        f"⏳ Дней с момента продажи: {data.get('days_since_sale', 'неизвестно')}\n\n"
        f"👤 ФИО: {data['name']}\n"
        f"📱 Телефон: {data['phone']}\n"
        f"🏷️ Товар: {product['name']}\n"
        f"🏷️ Бренд: {product['brand']}\n"
        f"💰 Цена: {product['price']} р\n"
        f"🔗 [Ссылка на товар]({product['link']})\n"
        f"📲 [Связаться с клиентом](tg://user?id={user_id})"
    )

    sent_message = await bot.send_message(ADMIN_ID, main_text, parse_mode="Markdown", disable_web_page_preview=True)

    if data.get('photos'):
        media_group = [types.InputMediaPhoto(photo) for photo in data['photos']]
        await bot.send_media_group(ADMIN_ID, media_group)

    data['admin_message_id'] = sent_message.message_id
    user_data[user_id] = data

    status_keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Закрыть с решением", callback_data=f"setstatus:реализовано:{data['application_id']}"),
        InlineKeyboardButton("❌ Отклонить (не решено)", callback_data=f"setstatus:не_реализовано:{data['application_id']}")
    )

    await bot.send_message(ADMIN_ID, "Выберите статус обращения:", reply_markup=status_keyboard)

async def process_bank_choice(callback: types.CallbackQuery, bot : Bot):
    if callback.from_user.id not in user_data:
        await callback.message.answer("❗️ Ошибка: ваши данные не найдены, сценарий сброшен. Начните заново.")
        await send_welcome(callback.message)
        return

    bank = callback.data.replace("bank_", "")
    bank_names = {
        "sber": "Сбербанк",
        "tinkoff": "Т-Банк",
        "vtb": "ВТБ",
        "alfa": "Альфа-Банк",
        "other": "Другой"
    }
    user_data[callback.from_user.id]['bank'] = bank_names[bank]

    await send_cashback_to_admin(callback.from_user.id, bot)
    await callback.message.answer("✅ Заявка отправлена администратору! Ожидайте обратной связи.")
    await callback.answer()

async def handle_cashback_request_start(callback: types.CallbackQuery):

    user_data[callback.from_user.id]['step'] = 'phone_number'

    await callback.message.edit_text("📱 Для начисления кешбека нам нужен ваш номер телефона.\nПожалуйста, поделитесь номером или введите его вручную - выберите, как вам удобнее! 👇")
    await callback.answer()

def register_callback_handlers(dp: Dispatcher, bot: Bot):
    dp.register_callback_query_handler(handle_menu, lambda c: c.data in ["get_cashback", "solve_problem"])
    dp.register_callback_query_handler(handle_back_to_main, lambda c: c.data == "back_to_main")
    dp.register_callback_query_handler(confirm_product, lambda c: c.data == "confirm_product")
    dp.register_callback_query_handler(process_problem_type, lambda c: c.data.startswith("problem_"))
    dp.register_callback_query_handler(handle_cashback_request_start, lambda c: c.data == "start_cashback_request")

    dp.register_callback_query_handler(make_finalize_problem_report(bot), lambda c: c.data == "finish_problem_report")
    dp.register_callback_query_handler(make_process_bank_choice(bot), lambda c: c.data.startswith("bank_"))
    dp.register_callback_query_handler(make_change_cashback_status(bot), lambda c: c.data.startswith("setcashback:"))
    dp.register_callback_query_handler(make_change_application_status(bot), lambda c: c.data.startswith("setstatus:"))

def make_finalize_problem_report(bot: Bot):
    async def wrapper(callback: types.CallbackQuery):
        await finalize_problem_report(callback, bot)
    return wrapper

def make_process_bank_choice(bot: Bot):
    async def wrapper(callback: types.CallbackQuery):
        await process_bank_choice(callback, bot)
    return wrapper

def make_change_cashback_status(bot: Bot):
    async def wrapper(callback: types.CallbackQuery):
        await change_cashback_status(callback, bot)
    return wrapper

def make_change_application_status(bot: Bot):
    async def wrapper(callback: types.CallbackQuery):
        await change_application_status(callback, bot)
    return wrapper
