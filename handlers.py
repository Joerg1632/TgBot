from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID, WB_API_KEY
from keyboards import main_inline_keyboard,  bank_keyboard
from wb_api import get_order_by_id, get_order_with_full_product_info, get_feedbacks, find_review_for_sku, get_order_status
from state import user_data
from datetime import datetime, timezone

async def send_welcome(message: types.Message):
    user_name = message.from_user.first_name

    await message.reply(
        f"Здравствуйте, {user_name}! 👋\n\n"
        "Я ваш виртуальный помощник, который поможет вам получить кэшбэк за отзыв или решить проблемы с заказом. Выберите действие:",
        reply_markup=main_inline_keyboard
    )

async def process_order_for_cashback(message: types.Message):
    order_id = message.text.strip()

    order, error = get_order_by_id(WB_API_KEY, order_id)
    if error:
        await message.reply(
            f"❗ Заказ не найден.\nУважаемый пользователь, к сожалению, мы не смогли найти заказ по указанным данным." +
            "\n\nПроверьте правильность информации и попробуйте еще раз.\nЕсли проблема сохраняется, свяжитесь с нашей поддержкой для помощи:",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_cash"),
                InlineKeyboardButton("✉️ Написать в поддержку", url=f"tg://user?id={ADMIN_ID}"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    status, error = get_order_status(WB_API_KEY, order_id)
    if error:
        await message.reply(f"❌ Ошибка получения статуса: {error}")
        return

    if status['wbStatus'] != 'sold':
        await message.reply("⚠️ Этот заказ еще не завершен (не получен клиентом). Кешбэк пока невозможен.")
        return

    if error:
        await message.reply(f"❌ Ошибка получения товара: {error}")
        return

    feedbacks, error = get_feedbacks(order['nmId'])
    if error:
        await message.reply(f"❌ Ошибка получения отзывов: {error}")
        return

    review = find_review_for_sku(feedbacks, order['skus'])
    if not review:
        await message.reply(
            "❗️ Отзыв не найден.\nПожалуйста, оставьте отзыв на Wildberries, а затем вернитесь сюда.\n\n"
            "Вот как правильно оставить отзыв:\n\n"
            "1️⃣ Достоинства\nПоделитесь тем, что вам понравилось в товаре! Это может быть качество, функциональность или что-то другое. Ваша положительная оценка поможет нам улучшать сервис! 🌟\n\n"
            "2️⃣ Недостатки\nУкажите, что можно улучшить: размер, управление, упаковка и т.д. Ваше мнение важно для нас! 👍\n\n"
            "3️⃣ Комментарий\nРасскажите о своём опыте использования: почему выбрали этот товар, оправдал ли он ожидания, кому бы порекомендовали. Это поможет другим покупателям сделать лучший выбор! 💬\n\n"
            "📚 Пример отзыва:\nДостоинства: Приятный материал, удобные режимы.\nНедостатки: Немного сложно привыкнуть к управлению.\nКомментарий: Отличная покупка, рекомендую!\n\n"
            "✍️ Оставьте отзыв и нажмите \"Готово\", чтобы получить кешбек!\n\n",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("Оставить отзыв",
                                     url=f"https://www.wildberries.ru/catalog/{order['nmId']}/detail.aspx#comments")
            ).add(
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    # Теперь review точно есть
    product = {
        'name': review['productDetails']['productName'],
        'brand': review['productDetails']['brandName'],
        'link': f"https://www.wildberries.ru/catalog/{order['nmId']}/detail.aspx"
    }

    user_data[message.from_user.id] = {
        'step': 'phone_number',
        'order_id': order_id,
        'order': order,
        'order_date': order['createdAt'],
        'product': product,
        'review': review
    }

    await message.reply(
        "✅ Ваш отзыв подтвержден!\n\n"
        "Для продолжения оформления заявки на выплату кэшбека нажмите кнопку ниже",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("💸 Оставить заявку на кешбек", callback_data="start_cashback_request")
        )
    )


async def process_order_for_problem(message: types.Message):
    order_id = message.text.strip()

    order, error = get_order_with_full_product_info(WB_API_KEY, order_id)
    if error:
        await message.reply(
            "❗ Заказ не найден. Проверьте номер и попробуйте снова.",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_problem"),
                InlineKeyboardButton("✉️ Написать в поддержку", url=f"tg://user?id={ADMIN_ID}"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    sale_date = datetime.fromisoformat(order['createdAt']).replace(tzinfo=timezone.utc)
    days_since_sale = (datetime.now(timezone.utc) - sale_date).days

    product = order['product_info']

    user_data[message.from_user.id] = {
        'step': 'choose_problem',
        'order_id': order_id,
        'product': product,
        'days_since_sale': days_since_sale  # вот это теперь сохраняется
    }

    text = (
        f"📋 Информация о покупке\n"
        f"├📦 Товар: {product['name']}\n"
        f"├📂 Категория: {product['category']}\n"
        f"└🏷️ Бренд: {product['brand']}\n\n"
        f"💰 Стоимость:\n"
        f"├🏷️ Изначальная цена: {product['old_price']} р\n"
        f"├💥 Скидка: {product['discount']}%\n"
        f"└💰 Итоговая цена со скидкой: {product['price']} р\n\n"
        f"🔗 [Ссылка на товар]({product['link']})"
    )

    await message.reply(
        f"{text}\n\nВсе верно? Если да — нажмите «Продолжить».",
        reply_markup=InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("✅ Продолжить", callback_data="confirm_product")
        )
    )

async def collect_problem_data(message: types.Message):
    user_id = message.from_user.id

    # Создаем структуру, если её нет (или чего-то не хватает)
    if user_id not in user_data:
        user_data[user_id] = {}

    data = user_data[user_id]

    # Обязательно гарантируем, что description и photos есть
    if 'description' not in data:
        data['description'] = ''
    if 'photos' not in data:
        data['photos'] = []

    # Заполняем описание и фото
    if message.text:
        data['description'] += message.text.strip() + '\n'

    if message.photo:
        if len(data['photos']) < 5:
            data['photos'].append(message.photo[-1].file_id)
            if message.caption:
                data['description'] += message.caption.strip() + '\n'

    user_data[user_id] = data  # обновили данные

    await message.reply(
        "✅ Данные добавлены. Можете отправить ещё или нажмите «Завершить заявку».",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Завершить заявку", callback_data="finish_problem_report")
        )
    )

async def collect_phone(message: types.Message):
    user_data[message.from_user.id]['phone'] = message.text.strip()
    user_data[message.from_user.id]['step'] = 'problem_description'
    await message.reply("📝 Опишите проблему. Вы также можете прикрепить до 5 фотографий:")

async def collect_name(message: types.Message):
    user_data[message.from_user.id]['name'] = message.text.strip()
    user_data[message.from_user.id]['step'] = 'enter_phone'
    await message.reply("📱 Теперь укажите ваш номер телефона для обратной связи:")

async def process_phone_number(message: types.Message):
    user_data[message.from_user.id]['phone'] = message.text.strip()
    user_data[message.from_user.id]['step'] = 'choose_bank'
    await message.reply("🏦 Выберите ваш банк:", reply_markup=bank_keyboard)

def register_message_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(process_order_for_cashback, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'enter_order')
    dp.register_message_handler(process_phone_number, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'phone_number')
    dp.register_message_handler(process_order_for_problem, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'problem_order')
    dp.register_message_handler(collect_name, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'enter_name')
    dp.register_message_handler(collect_phone, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'enter_phone')
    dp.register_message_handler(collect_problem_data, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'problem_description', content_types=types.ContentType.ANY)