"""
handlers.py

Хендлеры сообщений от пользователя. Здесь обрабатываются все текстовые команды и вводы данных.
"""

from aiogram import types, Dispatcher, Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID, WB_API_KEY
from keyboards import main_inline_keyboard, bank_keyboard
from utils import find_cashback_by_shk_id
from wb_api import get_order_with_full_product_info
from state import user_data
from pyzbar.pyzbar import decode
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import io
from datetime import datetime, timezone
from cashback_history import is_cashback_paid

async def send_welcome(message: types.Message):
    """
    Приветствует пользователя. Администратору отправляет особое приветствие.
    """
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    # if str(user_id) == ADMIN_ID:
    #     await message.answer(
    #         "👋 Добро пожаловать, Администратор!\n\n"
    #         "✅ Вы можете управлять заявками, отвечать пользователям и отслеживать обращения. "
    #         "Я уведомлю вас о новых сообщениях автоматически. Ожидайте заявок!"
    #     )
    # else:
    await message.answer(
        f"Здравствуйте, {user_name}! 👋\n\n"
        "Я ваш виртуальный помощник, который поможет вам получить кэшбэк за отзыв или решить проблемы с заказом. Выберите действие:",
        reply_markup=main_inline_keyboard
    )

async def extract_barcode_from_image(photo):
    """
    Извлекает EAN-13 штрихкод из фото с комбинированной обработкой.
    """
    bot = photo.bot  # Получаем объект бота из photo
    file = await bot.get_file(photo.file_id)
    image_bytes = await bot.download_file(file.file_path)
    image_data = image_bytes.read()

    image = Image.open(io.BytesIO(image_data))

    def preprocess_image(image, contrast_factor=1.5, sharpness_factor=2.0, method=1):
        image = image.convert('L')  # Перевод в ЧБ
        if method == 1:
            image = ImageOps.autocontrast(image)  # Авто-контраст
            image = image.filter(ImageFilter.MedianFilter(size=3))  # Фильтр шума
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast_factor)  # Контраст
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(sharpness_factor)  # Резкость

    # Перебираем разные комбинации обработки
    for contrast in [1.5, 2.0, 2.5]:
        for method in [1, 2]:  # 1 - сложная обработка, 2 - просто контраст
            processed_image = preprocess_image(image, contrast_factor=contrast, method=method)
            decoded_objects = decode(processed_image)
            ean13_codes = [obj.data.decode('utf-8') for obj in decoded_objects if obj.type == 'EAN13']
            if ean13_codes:
                return ean13_codes[0]  # Если нашли - возвращаем сразу

    # Если не помогла обработка - пробуем оригинал
    decoded_objects = decode(image)
    ean13_codes = [obj.data.decode('utf-8') for obj in decoded_objects if obj.type == 'EAN13']
    return ean13_codes[0] if ean13_codes else None

async def forward_question_to_admin(message: types.Message, bot: Bot):
    """
    Пересылает сообщение от пользователя админу по сценарию "заказ не найден".
    """
    user_id = message.from_user.id
    user_question = message.text

    if user_data.get(user_id, {}).get('step') == 'ask_support':
        await bot.send_message(
            ADMIN_ID,
            f"🔥 Новый вопрос от пользователя @{message.from_user.username}:\n\n{user_question}",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("📩 Ответить пользователю", callback_data=f"reply_user:{user_id}")
            )
        )
        await message.answer("✅ Ваш вопрос отправлен в поддержку! Ожидайте ответа.")
        user_data[user_id]['step'] = None


async def send_admin_reply(message: types.Message, bot: Bot):
    """
    Отправляет ответ администратора пользователю по сценарию "заказ не найден".
    """
    if user_data.get(ADMIN_ID, {}).get('step') != 'admin_reply':
        await message.answer("⚠ Ошибка! Сначала нажмите кнопку 'Ответить пользователю'.")
        return

    target_user = user_data[ADMIN_ID].get('target_user')
    if not target_user:
        await message.answer("⚠ Ошибка! Не найден ID пользователя для ответа.")
        return

    reply_text = message.text

    try:
        chat = await bot.get_chat(target_user)  # Получаем информацию о пользователе
        user_name = chat.username or chat.full_name or f"ID {target_user}"

        await bot.send_message(target_user, f"📩 Ответ от поддержки:\n\n{reply_text}")
        await message.answer(f"✅ Ответ отправлен @{user_name}.")

        user_data[ADMIN_ID] = {}  # Сбрасываем состояние
    except Exception as e:
        print(f"Ошибка при отправке ответа пользователю {target_user}: {e}")
        await message.answer("⚠ Ошибка при отправке ответа.")


async def process_order_for_cashback(message: types.Message):
    """
    Обработка ввода штрих-кода (ShkId) для проверки отзыва и получения кешбэка.
    """
    user_id = message.from_user.id

    if message.text:  # Если сообщение — текст
        shk_id = message.text.strip()
    elif message.photo:  # Если сообщение — фото
        shk_id = await extract_barcode_from_image(message.photo[-1])
        print(shk_id)
        if not shk_id:
            await message.answer(
                "❌ Не удалось распознать штрихкод. Пожалуйста, отправьте более четкое фото. "
                "Вы можете повторить ввод или обратиться в поддержку.",
                reply_markup=InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_cash"),
                    InlineKeyboardButton("✉️ Написать в поддержку", callback_data="order_not_found"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
                )
            )
            return

    # Проверяем, был ли уже выплачен кэшбэк за этот отзыв
    if is_cashback_paid(shk_id):
        await message.answer(
            "⚠️ Кэшбэк за этот отзыв уже был выплачен ранее.\n"
            "Вы не можете получить кэшбэк повторно за один и тот же отзыв.",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    existing_cashback = find_cashback_by_shk_id(user_id, shk_id)
    if existing_cashback:
        await message.answer(
            "❗ У вас уже есть заявка на этот заказ.\n"
            "Вы можете проверить статус заявки или обратиться в поддержку.",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("📩 Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return
 

    feedbacks, error = get_order_with_full_product_info(WB_API_KEY, shk_id)
    if error or feedbacks is None:
        await message.answer(
            "❗️ Отзыв не найден.\nПожалуйста, оставьте отзыв на Wildberries, а затем вернитесь сюда.\n\n"
            "Вот как правильно оставить отзыв:\n\n"
            "1️⃣ Достоинства\nПоделитесь тем, что вам понравилось в товаре! Это может быть качество, функциональность или что-то другое. Ваша положительная оценка поможет нам улучшать сервис! 🌟\n\n"
            "2️⃣ Недостатки\nУкажите, что можно улучшить: размер, управление, упаковка и т.д. Ваше мнение важно для нас! 👍\n\n"
            "3️⃣ Комментарий\nРасскажите о своём опыте использования: почему выбрали этот товар, оправдал ли он ожидания, кому бы порекомендовали. Это поможет другим покупателям сделать лучший выбор! 💬\n\n"
            "📚 Пример отзыва:\nДостоинства: Приятный материал, удобные режимы.\nНедостатки: Немного сложно привыкнуть к управлению.\nКомментарий: Отличная покупка, рекомендую!\n\n",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("📩 Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )   
        )
        return

    review = feedbacks.get("review", {})
    
    # Проверка на наличие текста отзыва
    if not review.get('text') and not review.get('pros') and not review.get('cons'):
        await message.answer(
            "❗️ Текст отзыва отсутствует.\nПожалуйста, убедитесь, что вы оставили текстовый отзыв на Wildberries, а затем попробуйте снова.",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return
    
    product_info = feedbacks["product_info"]

    product = {
        'name': product_info['name'],
        'brand': product_info['brand'],
        'link': product_info['link']
    }

    user_data[message.from_user.id] = {
        'step': 'phone_number',
        'order_id': shk_id,
        'order': feedbacks,
        'order_date': review['lastOrderCreatedAt'],
        'product': product,
        'review': review
    }

    await message.answer(
        "✅ Ваш отзыв подтвержден!\n\n"
        "Для продолжения оформления заявки на выплату кэшбэка нажмите кнопку ниже",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("💸 Оставить заявку на кэшбэк", callback_data="start_cashback_request")
        )
    )


async def process_order_for_problem(message: types.Message):
    """
    Обработка ввода номера заказа при подаче жалобы.
    """
    user_id = message.from_user.id

    if message.text:  # Если сообщение — текст
        shk_id = message.text.strip()
    elif message.photo:  # Если сообщение — фото
        shk_id = await extract_barcode_from_image(message.photo[-1])  # Берем фото наивысшего качества
        print(shk_id)
        if not shk_id:
            await message.answer(
                "❌ Не удалось распознать штрихкод. Пожалуйста, отправьте более четкое фото. "
                "Вы можете повторить ввод или обратиться в поддержку.",
                reply_markup=InlineKeyboardMarkup(row_width=1).add(
                    InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_cash"),
                    InlineKeyboardButton("✉️ Написать в поддержку", callback_data="order_not_found"),
                    InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
                )
            )
            return

    # Проверяем, есть ли уже заявка по этому штрихкоду
    existing_cashback = find_cashback_by_shk_id(user_id, shk_id)
    if existing_cashback:
        await message.answer(
            "❗ У вас уже есть заявка на этот заказ.\n"
            "Вы можете проверить статус заявки или обратиться в поддержку.",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("📩 Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    # Получаем информацию о заказе
    feedbacks, error = get_order_with_full_product_info(WB_API_KEY, shk_id)
    if error or feedbacks is None:
        await message.answer(
            "❗ Заказ не найден.\n"
            "Уважаемый пользователь, к сожалению, мы не смогли найти заказ по указанным данным.\n\n"
            "Проверьте правильность информации и попробуйте еще раз.\n"
            "Если проблема сохраняется, свяжитесь с нашей поддержкой для помощи:",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_cash"),
                InlineKeyboardButton("✉️ Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    # Проверяем наличие необходимых данных в feedbacks
    if 'review' not in feedbacks or 'product_info' not in feedbacks:
        await message.answer(
            "❗ Ошибка при обработке данных заказа.\n"
            "Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой.",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_cash"),
                InlineKeyboardButton("✉️ Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    # Обработка даты заказа
    try:
        # Универсальная обработка даты
        order_date_str = feedbacks['review']['lastOrderCreatedAt'].replace('Z', '+00:00')
        if '.' in order_date_str:
            # Добавляем недостающие нули в дробную часть, если нужно
            parts = order_date_str.split('.')
            if len(parts) == 2:
                fractional_part, timezone_part = parts[1].split('+')
                fractional_part = fractional_part.ljust(6, '0')  # Добавляем нули до 6 цифр
                order_date_str = f"{parts[0]}.{fractional_part}+{timezone_part}"
        sale_date = datetime.fromisoformat(order_date_str).replace(tzinfo=timezone.utc)
    except (ValueError, KeyError) as e:
        await message.answer(
            "❗ Ошибка при обработке даты заказа.\n"
            "Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой.",
            reply_markup=InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton("🔄 Повторить ввод", callback_data="retry_order_input_cash"),
                InlineKeyboardButton("✉️ Написать в поддержку", callback_data="order_not_found"),
                InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
            )
        )
        return

    # Вычисляем количество прошедших дней
    days_since_sale = (datetime.now(timezone.utc) - sale_date).days

    # Получаем информацию о товаре
    product = feedbacks['product_info']

    # Сохраняем данные пользователя
    user_data[user_id] = {
        'step': 'choose_problem',
        'order_id': shk_id,
        'product': product,
        'days_since_sale': days_since_sale
    }

    # Формируем текст сообщения
    text = (
        f"📋 Информация о покупке\n"
        f"├📦 Товар: {product.get('name', 'Не указан')}\n"
        f"├📂 Категория: {product.get('category', 'Не указана')}\n"
        f"└🏷️ Бренд: {product.get('brand', 'Не указан')}\n\n"
        f"💰 Стоимость:\n"
        f"├🏷️ Изначальная цена: {product.get('old_price', 'Не указана')} р\n"
        f"├💥 Скидка: {product.get('discount', 'Не указана')}%\n"
        f"└💰 Итоговая цена со скидкой: {product.get('price', 'Не указана')} р\n\n"
        f"🔗 [Ссылка на товар]({product.get('link', '')})"
    )

    # Отправляем сообщение пользователю
    await message.answer(
        f"{text}\n\nВсе верно? Если да — нажмите «Продолжить».",
        reply_markup=InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("✅ Продолжить", callback_data="confirm_product"),
            InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
        )
    )


async def collect_problem_data(message: types.Message):
    """
    Собирает текстовое описание проблемы и фото, прикреплённые пользователем.
    """
    user_id = message.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    data = user_data[user_id]

    if 'description' not in data:
        data['description'] = ''
    if 'photos' not in data:
        data['photos'] = []

    if message.text:
        data['description'] += message.text.strip() + '\n'

    if message.photo:
        if len(data['photos']) < 5:
            data['photos'].append(message.photo[-1].file_id)
            if message.caption:
                data['description'] += message.caption.strip() + '\n'

    user_data[user_id] = data

    await message.answer(
        "✅ Данные добавлены. Можете отправить ещё или нажмите «Завершить заявку».",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Завершить заявку", callback_data="finish_problem_report")
        )
    )


async def collect_phone(message: types.Message):
    """
    Сохраняет введённый пользователем номер телефона.
    """
    user_data[message.from_user.id]['phone'] = message.text.strip()
    user_data[message.from_user.id]['step'] = 'problem_description'
    await message.answer("📝 Опишите проблему. Вы также можете прикрепить до 5 фотографий:")


async def collect_name(message: types.Message):
    """
    Сохраняет ФИО пользователя.
    """
    user_data[message.from_user.id]['name'] = message.text.strip()
    user_data[message.from_user.id]['step'] = 'enter_phone'
    await message.answer("📱 Теперь укажите ваш номер телефона для обратной связи:")


async def process_phone_number(message: types.Message):
    """
    Сохраняет номер телефона при заявке на кэшбэк и переводит на ввод ФИО.
    """
    user_data[message.from_user.id]['phone'] = message.text.strip()
    user_data[message.from_user.id]['step'] = 'enter_name_cashback'  # Новый шаг для кэшбэка
    await message.answer("👤 Пожалуйста, введите ваше ФИО (полное имя):")

async def collect_name_cashback(message: types.Message):
    """
    Сохраняет ФИО пользователя для заявки на кэшбэк и переводит на выбор банка.
    """
    user_data[message.from_user.id]['name'] = message.text.strip()
    user_data[message.from_user.id]['step'] = 'choose_bank'
    await message.answer("🏦 Выберите ваш банк:", reply_markup=bank_keyboard)


def register_message_handlers(dp: Dispatcher, bot: Bot):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(process_order_for_cashback, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'enter_order', content_types=['photo', 'text'])
    dp.register_message_handler(process_phone_number, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'phone_number')
    dp.register_message_handler(collect_name_cashback, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'enter_name_cashback')  
    dp.register_message_handler(process_order_for_problem, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'problem_order',  content_types=['photo', 'text'])
    dp.register_message_handler(collect_name, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'enter_name')
    dp.register_message_handler(collect_phone, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'enter_phone')
    dp.register_message_handler(collect_problem_data, lambda m: user_data.get(m.from_user.id, {}).get('step') == 'problem_description', content_types=types.ContentType.ANY)
    dp.register_message_handler(lambda msg: forward_question_to_admin(msg, bot), lambda m: user_data.get(m.from_user.id, {}).get('step') == 'ask_support')
    dp.register_message_handler(lambda msg: send_admin_reply(msg, bot), lambda m: user_data.get(ADMIN_ID, {}).get('step') == 'admin_reply')