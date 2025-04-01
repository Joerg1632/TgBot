"""
keyboards.py

Клавиатуры, используемые в боте (inline-кнопки).
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from state import user_data
# Главное меню
main_inline_keyboard = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🎁 Получить кэшбэк за отзыв", callback_data="get_cashback"),
    InlineKeyboardButton("💬 Разобраться с вашей ситуацией", callback_data="solve_problem")
)

# Выбор банка
bank_keyboard = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🟢 Сбербанк", callback_data="bank_sber"),
    InlineKeyboardButton("🟡 Т-Банк", callback_data="bank_tinkoff"),
    InlineKeyboardButton("🔵 ВТБ", callback_data="bank_vtb"),
    InlineKeyboardButton("🔴 Альфа-Банк", callback_data="bank_alfa"),
    InlineKeyboardButton("⚪️ Другой", callback_data="bank_other")
)

# Кнопка назад
back_keyboard = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🔙 Назад", callback_data="back")
)


# Кнопка в главное меню
back_to_main_keyboard = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
)

# Типы жалоб для выбора
complaint_types = ["📦 Упаковка", "🛠️ Качество товара", "🚚 Доставка", "❓ Другое"]

# Клавиатура для изменения статуса кэшбэка
def get_cashback_status_keyboard(application_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Выплатить кэшбэк", callback_data=f"setcashback:реализовано:{application_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"setcashback:не_реализовано:{application_id}")
    )

# Клавиатура для изменения статуса проблемы
def get_status_keyboard(application_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("✅ Удовлетворить заявку", callback_data=f"set_status=закрыто_app={application_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"set_status=не реализовано_app={application_id}")
    )

def get_navigation_keyboard(user_id, extra_buttons=None):
    """
    Генерирует клавиатуру с кнопками "Назад" и "Поддержка",
    при необходимости добавляет дополнительные кнопки.
    """
    previous_step = user_data.get(user_id, {}).get('previous_step')
    keyboard = InlineKeyboardMarkup(row_width=1)

    # Добавляем переданные кнопки (например, "Повторить ввод")
    if extra_buttons:
        for btn in extra_buttons:
            keyboard.add(btn)

    # Кнопка "Назад" (если у пользователя есть предыдущий шаг)
    if previous_step:
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back_to_previous"))
    
    # Кнопка "Поддержка" (всегда доступна)
    keyboard.add(InlineKeyboardButton("📩 Написать в поддержку", callback_data="order_not_found"))
    keyboard.add(InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main"))

    return keyboard
