from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_inline_keyboard = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🎁 Получить кешбек за отзыв", callback_data="get_cashback"),
    InlineKeyboardButton("💬 Разобраться с вашей ситуацией", callback_data="solve_problem")
)

bank_keyboard = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🟢 Сбербанк", callback_data="bank_sber"),
    InlineKeyboardButton("🟡 Т-Банк", callback_data="bank_tinkoff"),
    InlineKeyboardButton("🔵 ВТБ", callback_data="bank_vtb"),
    InlineKeyboardButton("🔴 Альфа-Банк", callback_data="bank_alfa"),
    InlineKeyboardButton("⚪️ Другой", callback_data="bank_other")
)

back_keyboard = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🔙 Назад", callback_data="back")
)

back_to_main_keyboard = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")
)

complaint_types = ["📦 Упаковка", "🛠️ Качество товара", "🚚 Доставка", "❓ Другое"]

def get_cashback_status_keyboard(application_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Выплатить кешбэк", callback_data=f"setcashback:реализовано:{application_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"setcashback:не_реализовано:{application_id}")
    )

def get_status_keyboard(application_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("✅ Удовлетворить заявку", callback_data=f"set_status=закрыто_app={application_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"set_status=не реализовано_app={application_id}")
    )
