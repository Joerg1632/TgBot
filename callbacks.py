"""
callbacks.py

Модуль для обработки callback-запросов (inline-кнопки).
Здесь описаны все сценарии, связанные с меню, выбором банков, статусов заявок и т.д.
"""

from aiogram import types, Dispatcher, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
import copy
from state import user_data
from utils import generate_application_id, find_user_by_application_id
from keyboards import main_inline_keyboard, back_to_main_keyboard, complaint_types, get_cashback_status_keyboard, get_navigation_keyboard
from datetime import datetime, timezone
from cashback_history import save_paid_cashback
async def handle_menu(callback: types.CallbackQuery):
    """
    Обработка выбора в главном меню.
    - 'get_cashback' - запустить сценарий кэшбэка
    - 'solve_problem' - запустить сценарий подачи жалобы
    """
    user_id = callback.from_user.id
    if callback.data == "get_cashback":
        user_data[callback.from_user.id] = {'step': 'enter_order'}
        await callback.message.edit_text(
            "💸 Чтобы получить кэшбэк, укажите номер вашего заказа, который указан на упаковке, или просто отправьте фото штрих-кода 📸\n\nГлавное, чтобы изображение было четким! 👇",
            reply_markup=get_navigation_keyboard(user_id)
        )
    elif callback.data == "solve_problem":
        user_data[callback.from_user.id] = {'step': 'problem_order'}
        await callback.message.edit_text(
            "✍️ Введите номер вашего заказа, который указан на упаковке товара или отправьте фото штрих-кода 📸\n\nЭто поможет нам разобраться с вашей проблемой🛠️",
            reply_markup=get_navigation_keyboard(user_id)
        )
    await callback.answer()


async def handle_back_to_main(callback: types.CallbackQuery):
    """
    Возврат в главное меню, сброс состояния.
    """
    await callback.message.edit_text(
        "Я ваш виртуальный помощник, который поможет вам получить кэшбэк за отзыв или решить проблемы с заказом. Выберите действие:",
        reply_markup=main_inline_keyboard
    )
    user_data.pop(callback.from_user.id, None)
    await callback.answer()


async def confirm_product(callback: types.CallbackQuery):
    """
    Подтверждение информации о товаре при подаче жалобы.
    """
    user_data[callback.from_user.id]['step'] = 'choose_problem'

    await callback.message.edit_text(
        "📋 Выберите, с чем у вас возникла проблема:",
        reply_markup=InlineKeyboardMarkup().add(
            *[InlineKeyboardButton(pt, callback_data=f"problem_{pt}") for pt in complaint_types]
        )
    )
    await callback.answer()


async def retry_order_input_problem(callback: types.CallbackQuery):
    """
    Возврат к вводу номера заказа в сценарии жалобы.
    """
    user_data[callback.from_user.id] = {'step': 'problem_order'}
    await callback.message.edit_text(
        "✍️ Введите номер вашего заказа, который указан на упаковке товара или отправьте фото штрих-кода 📸\n\nЭто поможет нам разобраться с вашей проблемой🛠️",
        reply_markup=back_to_main_keyboard
    )
    await callback.answer()


async def retry_order_input_cash(callback: types.CallbackQuery):
    """
    Возврат к вводу номера заказа в сценарии кэшбэка.
    """
    user_data[callback.from_user.id] = {'step': 'enter_order'}
    await callback.message.edit_text(
        "💸 Чтобы получить кэшбэк, укажите номер вашего заказа, который указан на упаковке, или просто отправьте фото штрих-кода 📸\n\nГлавное, чтобы изображение было четким! 👇",
        reply_markup=back_to_main_keyboard
    )
    await callback.answer()

async def handle_help_callback(callback: types.CallbackQuery):
    """
    Обрабатывает callback-кнопку "Написать в поддержку".
    """
    user_id = callback.from_user.id

    # Определяем, откуда пользователь пришёл
    previous_step = user_data.get(user_id, {}).get('step', 'choose_problem')

    back_order_keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_previous")
    )

    await callback.message.answer(
        "❗ Если у вас есть вопросы, напишите их прямо здесь 👇, и мы передадим их в поддержку!",
        reply_markup=back_order_keyboard
    )

    # Сохраняем предыдущий шаг перед входом в поддержку
    user_data[user_id] = {
        'step': 'ask_support',
        'previous_step': previous_step
    }
    await callback.answer()


async def admin_reply_to_user(callback: types.CallbackQuery, bot: Bot):
    """
    Позволяет админу отправить ответ пользователю, нажав кнопку по сценарию "заказ не найден".
    """
    user_id = int(callback.data.split(":")[1])

    user = await bot.get_chat(user_id)
    user_name = user.username or f"ID {user_id}"

    user_data[ADMIN_ID] = {'step': 'admin_reply', 'target_user': user_id}

    await callback.message.answer(f"✍️ Введите ответ для @{user_name}:")
    await callback.answer()


async def handle_back_to_previous(callback: types.CallbackQuery):
    """
    Обрабатывает кнопку "🔙 Назад", возвращая пользователя на предыдущий шаг.
    """
    user_id = callback.from_user.id
    previous_step = user_data.get(user_id, {}).get('previous_step', 'problem_order')

    if previous_step == 'problem_order':
        await callback.message.answer(
            "❗ Заказ не найден.\nУважаемый пользователь, к сожалению, мы не смогли найти заказ по указанным данным." +
            "\n\nПроверьте правильность информации и попробуйте еще раз.\nЕсли проблема сохраняется, свяжитесь с нашей поддержкой для помощи:",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_problem"),
                InlineKeyboardButton("✉️ Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
    elif previous_step == 'enter_order':
        await callback.message.answer(
            f"❗ Заказ не найден.\nУважаемый пользователь, к сожалению, мы не смогли найти заказ по указанным данным." +
            "\n\nПроверьте правильность информации и попробуйте еще раз.\nЕсли проблема сохраняется, свяжитесь с нашей поддержкой для помощи:",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_cash"),
                InlineKeyboardButton("✉️ Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )

    # Убираем состояние "ask_support", возвращая пользователя на прошлый шаг
    user_data[user_id]['step'] = previous_step
    await callback.answer()


async def process_problem_type(callback: types.CallbackQuery):
    """
    Сохранить тип проблемы и перейти к вводу ФИО.
    """
    user_data[callback.from_user.id]['problem_type'] = callback.data.replace("problem_", "")
    user_data[callback.from_user.id]['step'] = 'enter_name'
    await callback.message.answer("📛 Пожалуйста, введите ваше ФИО:")
    await callback.answer()


async def send_cashback_to_admin(user_id, bot):
    """
    Отправка информации о заявке на кэшбэк администратору.
    """
    # Проверяем, есть ли данные пользователя
    if user_id not in user_data:
        raise ValueError(f"Данные для пользователя {user_id} не найдены.")

    data = user_data[user_id]

    # Генерация ID заявки
    application_id = generate_application_id()
    data.update({
        "application_id": application_id,
        "application_type": "cashback",
        "status": "в работе",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id
    })

    # Проверяем наличие необходимых данных
    if 'product' not in data or 'review' not in data or 'order_date' not in data:
        raise ValueError("Недостаточно данных для создания заявки.")

    product = data['product']
    review = data['review']

    # Обработка даты заказа
    try:
        # Универсальная обработка даты
        order_date_str = data['order_date'].replace('Z', '+00:00')
        if '.' in order_date_str:
            # Добавляем недостающие нули в дробную часть, если нужно
            parts = order_date_str.split('.')
            if len(parts) == 2:
                fractional_part, timezone_part = parts[1].split('+')
                fractional_part = fractional_part.ljust(6, '0')  # Добавляем нули до 6 цифр
                order_date_str = f"{parts[0]}.{fractional_part}+{timezone_part}"
        sale_date = datetime.fromisoformat(order_date_str).replace(tzinfo=timezone.utc)
    except ValueError as e:
        raise ValueError(f"Ошибка при обработке даты заказа: {e}")

    # Вычисляем количество прошедших дней
    days_passed = (datetime.now(timezone.utc) - sale_date).days
    can_pay = "ДА" if days_passed >= 14 else "НЕТ"

    # Формируем текст сообщения
    text = (
        f"📋 Заявка на кэшбэк №{application_id}\n"
        f"👤 ФИО: {data.get('name', 'Не указано')}\n"  # Добавлено ФИО
        f"📦 Номер заказа: {data.get('order_id', 'Не указан')}\n"
        f"🏷️ Товар: {product.get('name', 'Не указан')} ({product.get('brand', 'Не указан')})\n"
        f"⭐️ Оценка клиента: {review.get('productValuation', 'Не указана')}⭐️\n"
        f"🗓️ Дата отзыва: {review.get('createdDate', 'Не указана')}\n"
        f"🛒 Дата продажи: {sale_date.date()}\n"
        f"📅 Дней с момента продажи: {days_passed}\n"
        f"💬 Отзыв: \n"
        f"   📌 Плюсы: {review.get('pros', 'Плюсы не указаны')}\n"
        f"   📌 Минусы: {review.get('cons', 'Минусы не указаны')}\n"
        f"   📌 Комментарий: {review.get('text', 'Комментарий не указан')}\n"
        f"📱 Телефон: {data.get('phone', 'Не указан')}\n"
        f"🏦 Банк: {data.get('bank', 'Не указан')}\n"
        f"💸 Начислить кэшбэк: {can_pay}\n"
        f"📲 [Связаться с клиентом](tg://user?id={user_id})"
    )

    # Отправляем сообщение администратору
    message = await bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

    # Сохраняем ID сообщения администратора
    data['admin_message_id'] = message.message_id

    # Архивируем предыдущие заявки, если они есть
    if "previous_orders" not in data:
        data["previous_orders"] = []

    # Добавляем текущую заявку в архив
    data["previous_orders"].append(data.copy())

    # Обновляем данные пользователя
    user_data[user_id] = data

    # Отправляем клавиатуру для выбора решения
    await bot.send_message(ADMIN_ID, "Выберите решение по кэшбэку:", reply_markup=get_cashback_status_keyboard(application_id))


async def finalize_problem_report(callback: types.CallbackQuery, bot:Bot):
    """
    Завершает заявку по проблеме, присваивает ей номер и отправляет админу.
    """
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
        f"⏳ Ожидаемое время ответа: в течение 24 часов",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
        )
    )

    await send_problem_report_to_admin(user_id,bot)
    await callback.answer()
    


async def change_application_status(callback: types.CallbackQuery, bot):
    """
    Администратор меняет статус заявки по проблеме.
    """
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
        "не_реализовано": "❌ Ваша заявка закрыта без решения.",
        "реализовано": "✅ Ваша заявка успешно реализована."
    }
    await bot.send_message(user_id, f"ℹ️ Статус вашей заявки №{application_id} изменен:\n{status_messages[status]}")
    await callback.answer("Статус обновлён.", reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
        ))


async def change_cashback_status(callback: types.CallbackQuery, bot):
    """
    Администратор меняет статус заявки на кэшбэк.
    """
    _, status, application_id = callback.data.split(":")

    user_id, data = find_user_by_application_id(application_id, user_data)

    if not data:
        await callback.answer("Заявка не найдена.")
        return

    data['status'] = status
    
    # Если кэшбэк выплачен - сохраняем в историю
    if status == "реализовано":
        save_paid_cashback(data['order_id'])
    text = f"📋 Заявка на кэшбэк (обновлено)\n\n{data['product']['name']}\n🔖 Статус: *{status}*"

    # Обновляем сообщение у админа
    await bot.edit_message_text(text, ADMIN_ID, data['admin_message_id'], parse_mode="Markdown")

    messages = {
        "реализовано": "✅ Ваш кэшбэк выплачен!",
        "не_реализовано": "❌ В кэшбэке отказано. Свяжитесь с поддержкой, если есть вопросы."
    }
    await bot.send_message(user_id, f"ℹ️ Статус заявки на кэшбэк: {messages[status]}")

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



async def process_bank_choice(callback: types.CallbackQuery, bot: Bot):
    """
    Отправка финальной заявки по кэшбэку администратору и предложение ввести новый штрихкод.
    """
    bank = callback.data.replace("bank_", "")
    bank_names = {
        "sber": "Сбербанк",
        "tinkoff": "Т-Банк",
        "vtb": "ВТБ",
        "alfa": "Альфа-Банк",
        "other": "Другой"
    }
    user_id = callback.from_user.id
    user_data[user_id]['bank'] = bank_names[bank]

    await send_cashback_to_admin(user_id, bot)

    print("До:")
    print(user_data[user_id].get("previous_orders", []))

    # ✅ Создаём копию текущей заявки (без ссылок на вложенные структуры)
    old_order = copy.deepcopy(user_data[user_id])
    old_order.pop("previous_orders", None)

    # ✅ Проверяем, добавлена ли заявка в архив
    if "previous_orders" not in user_data[user_id]:
        user_data[user_id]["previous_orders"] = []

    # ✅ Если заявка ещё не добавлена, добавляем
    if user_data[user_id]["previous_orders"] and user_data[user_id]["previous_orders"][-1] == old_order:
        print("⏭️ Заявка уже есть в архиве, не дублируем!")
    else:
        user_data[user_id]["previous_orders"].append(old_order)

    print("После:")
    print(user_data[user_id]["previous_orders"])

    # ✅ Перезаписываем user_data[user_id], но оставляем previous_orders
    previous_orders_copy = user_data[user_id]["previous_orders"]  # Сохраняем прошлые заявки

    user_data[user_id] = {
        'step': "enter_order",
        'previous_step': "bank_choice",
        'previous_orders': previous_orders_copy  # Используем уже обновлённый архив заявок
    }

    print("После обновления previous_orders:")
    print(user_data[user_id]["previous_orders"])  # Проверяем, что заявка не дублируется

    await callback.message.answer(
        "✅ Заявка отправлена администратору! Ожидайте обратной связи.\n\n"
        "Хотите получить кэшбэк за другой товар? Введите номер заказа с упаковки или перейдите в главное меню! 👇",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
        )
    )
    await callback.answer()



async def handle_cashback_request_start(callback: types.CallbackQuery):
    """
    Выбор банка для выплаты кэшбэка.
    """
    user_data[callback.from_user.id]['step'] = 'phone_number'

    await callback.message.edit_text("📱 Для начисления кэшбэка нам нужен ваш номер телефона.\nПожалуйста, поделитесь номером или введите его вручную - выберите, как вам удобнее! 👇")
    await callback.answer()



def register_callback_handlers(dp: Dispatcher, bot: Bot):
    """
    Запуск процесса сбора данных для кэшбэка.
    """
    dp.register_callback_query_handler(handle_menu, lambda c: c.data in ["get_cashback", "solve_problem"])
    dp.register_callback_query_handler(handle_back_to_main, lambda c: c.data == "back_to_main")
    dp.register_callback_query_handler(confirm_product, lambda c: c.data == "confirm_product")
    dp.register_callback_query_handler(process_problem_type, lambda c: c.data.startswith("problem_"))
    dp.register_callback_query_handler(handle_cashback_request_start, lambda c: c.data == "start_cashback_request")
    dp.register_callback_query_handler(retry_order_input_problem, lambda c: c.data == "retry_order_input_problem")
    dp.register_callback_query_handler(retry_order_input_cash, lambda c: c.data == "retry_order_input_cash")
    dp.register_callback_query_handler(handle_help_callback, lambda c: c.data == "order_not_found")
    dp.register_callback_query_handler(handle_back_to_previous, lambda c: c.data == "back_to_previous")

    dp.register_callback_query_handler(make_admin_reply_to_user(bot), lambda c: c.data.startswith("reply_user:"))
    dp.register_callback_query_handler(make_finalize_problem_report(bot), lambda c: c.data == "finish_problem_report")
    dp.register_callback_query_handler(make_process_bank_choice(bot), lambda c: c.data.startswith("bank_"))
    dp.register_callback_query_handler(make_change_cashback_status(bot), lambda c: c.data.startswith("setcashback:"))
    dp.register_callback_query_handler(make_change_application_status(bot), lambda c: c.data.startswith("setstatus:"))

def make_admin_reply_to_user(bot: Bot):
    async def wrapper(callback: types.CallbackQuery):
        await admin_reply_to_user(callback, bot)
    return wrapper

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
