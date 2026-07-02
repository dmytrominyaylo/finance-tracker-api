from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_categories_submenu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📋 List", callback_data="categories_menu:list")],
        [InlineKeyboardButton(text="➕ Add", callback_data="categories_menu:add")],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data="categories_menu:delete")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_transactions_submenu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📋 List", callback_data="transactions_menu:list")],
        [InlineKeyboardButton(text="➕ Add", callback_data="transactions_menu:add")],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data="transactions_menu:delete")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_budgets_submenu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📋 List", callback_data="budgets_menu:list")],
        [InlineKeyboardButton(text="➕ Add", callback_data="budgets_menu:add")],
        [InlineKeyboardButton(text="🗑️ Delete", callback_data="budgets_menu:delete")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_user_settings_submenu() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="👤 Profile", callback_data="user_menu:profile")],
        [InlineKeyboardButton(text="📧 Change email", callback_data="user_menu:email")],
        [InlineKeyboardButton(text="🔑 Change password", callback_data="user_menu:password")],
        [InlineKeyboardButton(text="🗑️ Delete account", callback_data="user_menu:delete")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


CATEGORY_EMOJI_NAMES = {
    "🍔": "Food",
    "🚗": "Transport",
    "🏠": "Housing",
    "💊": "Health",
    "🎮": "Games",
    "👕": "Clothes",
    "📚": "Education",
    "💡": "Utilities",
    "🎁": "Gifts",
    "💰": "Salary",
    "✈️": "Travel",
    "🐾": "Pets",
    "🎬": "Entertainment",
    "☕": "Coffee",
    "🏋️": "Sport",
    "📱": "Phone",
    "🎵": "Music",
    "🚬": "Cigarettes",
    "🍺": "Alcohol",
    "💄": "Cosmetics",
}


def get_emoji_picker() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i, emoji in enumerate(CATEGORY_EMOJI_NAMES, 1):
        row.append(InlineKeyboardButton(text=emoji, callback_data=f"category_emoji:{emoji}"))
        if i % 5 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="✏️ Type custom emoji", callback_data="category_emoji:custom")])
    buttons.append([InlineKeyboardButton(text="⏭️ Skip", callback_data="category_emoji:skip")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_name_suggestion_keyboard(emoji: str, suggested_name: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"✅ Use '{suggested_name}'", callback_data=f"use_suggested:{emoji}")],
        [InlineKeyboardButton(text="✏️ Type my own", callback_data="type_own_name")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="categories_menu:add")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_delete_mode_keyboard(entity: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🗑️ Delete one", callback_data=f"{entity}_del_mode:one")],
        [InlineKeyboardButton(text="🗑️ Delete several", callback_data=f"{entity}_del_mode:many")],
        [InlineKeyboardButton(text="🗑️ Delete all", callback_data=f"{entity}_del_mode:all")],
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_multiselect_keyboard(
    items: list[dict],
    entity: str,
    label_key: str,
    id_key: str,
    selected_ids: set[int],
) -> InlineKeyboardMarkup:
    buttons = []

    for item in items:
        item_id = item[id_key]
        label = item[label_key]
        checkbox = "☑️" if item_id in selected_ids else "⬜️"
        buttons.append([
            InlineKeyboardButton(text=f"{checkbox} {label}", callback_data=f"{entity}_toggle:{item_id}")
        ])

    buttons.append([
        InlineKeyboardButton(text=f"✅ Confirm ({len(selected_ids)})", callback_data=f"{entity}_confirm_many"),
        InlineKeyboardButton(text="❌ Cancel", callback_data=f"{entity}_cancel_many"),
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
