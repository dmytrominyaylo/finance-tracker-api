from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="💰 Balance")],
        [KeyboardButton(text="📂 Categories"), KeyboardButton(text="💸 Transactions")],
        [KeyboardButton(text="📊 Budgets"), KeyboardButton(text="👤 User Settings")],
        [KeyboardButton(text="🚪 Sign out")],
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
