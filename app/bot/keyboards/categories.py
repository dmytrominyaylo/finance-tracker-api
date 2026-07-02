from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_categories_keyboard(categories: list[dict], callback_prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=c["name"], callback_data=f"{callback_prefix}:{c['id']}")]
        for c in categories
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_transactions_delete_keyboard(transactions: list[dict]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=f"{t['amount']} — {t['description']} ({t['transactionDate']})",
            callback_data=f"delete_tx:{t['id']}",
        )]
        for t in transactions
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
