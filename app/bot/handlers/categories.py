from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.api_client import api_client
from app.bot.helpers import get_valid_session, get_message, get_categories_or_notify_empty
from app.bot.keyboards.menus import (
    get_categories_submenu,
    get_emoji_picker,
    get_name_suggestion_keyboard,
    get_delete_mode_keyboard,
    get_multiselect_keyboard,
    CATEGORY_EMOJI_NAMES,
)

router = Router()


class CategoryStates(StatesGroup):
    waiting_custom_emoji = State()
    waiting_name = State()
    selecting_many = State()


@router.message(F.text == "📂 Categories")
async def categories_menu_handler(message: Message):
    session = await get_valid_session(message)
    if not session:
        return

    await message.answer("📂 Categories menu:", reply_markup=get_categories_submenu())


@router.callback_query(F.data == "categories_menu:list")
async def categories_list_callback(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    result = await api_client.get_categories(session["token"])

    if not result or result["total"] == 0:
        text = "📂 You don't have any categories yet."
    else:
        text = "📂 Your categories:\n\n"
        for category in result["categories"]:
            text += f"• {category['name']}\n"

    msg = get_message(callback)
    if msg:
        await msg.edit_text(text)

    await callback.answer()


@router.callback_query(F.data == "categories_menu:add")
async def categories_add_callback(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    msg = get_message(callback)
    if msg:
        await msg.edit_text("🎨 Choose an icon for your category:", reply_markup=get_emoji_picker())

    await callback.answer()


@router.callback_query(F.data.startswith("category_emoji:"))
async def category_emoji_chosen_handler(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        return

    choice = callback.data.split(":")[1]
    msg = get_message(callback)

    if choice == "custom":
        if msg:
            await msg.edit_text("✏️ Type your own emoji:")
        await state.set_state(CategoryStates.waiting_custom_emoji)
        await callback.answer()
        return

    if choice == "skip":
        if msg:
            await msg.edit_text("📝 Enter category name:")
        await state.set_state(CategoryStates.waiting_name)
        await callback.answer()
        return

    emoji = choice
    suggested_name = CATEGORY_EMOJI_NAMES.get(emoji, "")
    await state.update_data(emoji=emoji)

    if msg:
        await msg.edit_text(
            f"{emoji} How about naming it {suggested_name}?",
            reply_markup=get_name_suggestion_keyboard(emoji, suggested_name),
        )

    await callback.answer()


@router.callback_query(F.data.startswith("use_suggested:"))
async def use_suggested_name_handler(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        return

    emoji = callback.data.split(":")[1]
    suggested_name = CATEGORY_EMOJI_NAMES.get(emoji, "")
    full_name = f"{emoji} {suggested_name}".strip()

    session = await get_valid_session(callback)
    if not session:
        return

    result, status_code = await api_client.create_category(session["token"], full_name)

    msg = get_message(callback)
    if msg:
        if result:
            await msg.edit_text(f"✅ Category {full_name} created!")
        elif status_code == 409:
            await msg.edit_text("⚠️ A category with this name already exists.")
        else:
            await msg.edit_text("❌ Failed to create category.")

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "type_own_name")
async def type_own_name_handler(callback: CallbackQuery, state: FSMContext):
    msg = get_message(callback)
    if msg:
        await msg.edit_text("📝 Enter category name:")

    await state.set_state(CategoryStates.waiting_name)
    await callback.answer()


@router.message(CategoryStates.waiting_custom_emoji)
async def custom_emoji_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    await state.update_data(emoji=message.text)
    await message.answer("📝 Enter category name:")
    await state.set_state(CategoryStates.waiting_name)


@router.message(CategoryStates.waiting_name)
async def category_name_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    session = await get_valid_session(message)
    if not session:
        return

    data = await state.get_data()
    emoji = data.get("emoji", "")
    full_name = f"{emoji} {message.text}".strip() if emoji else message.text

    result, status_code = await api_client.create_category(session["token"], full_name)

    if result:
        await message.answer(f"✅ Category {full_name} created!")
    elif status_code == 409:
        await message.answer("⚠️ A category with this name already exists.")
    else:
        await message.answer("❌ Failed to create category.")

    await state.clear()


@router.callback_query(F.data == "categories_menu:delete")
async def categories_delete_callback(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    categories = await get_categories_or_notify_empty(callback, session["token"])
    if categories is None:
        return

    msg = get_message(callback)
    if msg:
        await msg.edit_text("🗑️ How do you want to delete?", reply_markup=get_delete_mode_keyboard("category"))

    await callback.answer()


@router.callback_query(F.data == "category_del_mode:one")
async def category_del_mode_one(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    categories = await get_categories_or_notify_empty(callback, session["token"])
    if categories is None:
        return

    buttons = [
        [InlineKeyboardButton(text=c["name"], callback_data=f"delete_category:{c['id']}")]
        for c in categories
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    msg = get_message(callback)
    if msg:
        await msg.edit_text("🗑️ Choose a category to delete:", reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data.startswith("delete_category:"))
async def delete_category_confirm(callback: CallbackQuery):
    if not callback.data:
        return

    category_id = callback.data.split(":")[1]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data=f"confirm_delete_category:{category_id}"),
            InlineKeyboardButton(text="❌ No", callback_data="cancel_delete_category"),
        ]
    ])

    msg = get_message(callback)
    if msg:
        await msg.edit_text("🗑️ Are you sure you want to delete this category?", reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_category:"))
async def delete_category_callback(callback: CallbackQuery):
    if not callback.data:
        return

    category_id = int(callback.data.split(":")[1])
    session = await get_valid_session(callback)
    if not session:
        return

    category_name = f"ID: {category_id}"
    result = await api_client.get_categories(session["token"])
    if result and "categories" in result:
        for c in result["categories"]:
            if c["id"] == category_id:
                category_name = c["name"]
                break

    success = await api_client.delete_category(session["token"], category_id)

    msg = get_message(callback)
    if msg:
        if success:
            await msg.edit_text(f"✅ Category {category_name} deleted!")
        else:
            await msg.edit_text("❌ Failed to delete category. It may be used in transactions or budgets.")

    await callback.answer()


@router.callback_query(F.data == "cancel_delete_category")
async def cancel_delete_category_callback(callback: CallbackQuery):
    msg = get_message(callback)
    if msg:
        await msg.edit_text("✅ Deletion cancelled.")

    await callback.answer()


@router.callback_query(F.data == "category_del_mode:many")
async def category_del_mode_many(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)
    if not session:
        return

    categories = await get_categories_or_notify_empty(callback, session["token"])
    if categories is None:
        return

    await state.update_data(categories=categories, selected_ids=set())
    await state.set_state(CategoryStates.selecting_many)

    keyboard = get_multiselect_keyboard(categories, "category", "name", "id", set())

    msg = get_message(callback)
    if msg:
        await msg.edit_text("🗑️ Select categories to delete:", reply_markup=keyboard)

    await callback.answer()


@router.callback_query(CategoryStates.selecting_many, F.data.startswith("category_toggle:"))
async def category_toggle_selection(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        return

    item_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    selected_ids: set = data.get("selected_ids", set())

    if item_id in selected_ids:
        selected_ids.discard(item_id)
    else:
        selected_ids.add(item_id)

    await state.update_data(selected_ids=selected_ids)

    keyboard = get_multiselect_keyboard(data["categories"], "category", "name", "id", selected_ids)

    msg = get_message(callback)
    if msg:
        await msg.edit_reply_markup(reply_markup=keyboard)

    await callback.answer()


@router.callback_query(CategoryStates.selecting_many, F.data == "category_confirm_many")
async def category_confirm_many(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_ids: set = data.get("selected_ids", set())

    if not selected_ids:
        await callback.answer("⚠️ No categories selected.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="category_delete_many_confirmed"),
            InlineKeyboardButton(text="❌ No", callback_data="category_cancel_many"),
        ]
    ])

    msg = get_message(callback)
    if msg:
        await msg.edit_text(f"🗑️ Delete {len(selected_ids)} selected categories?", reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "category_delete_many_confirmed")
async def category_delete_many_confirmed(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)
    if not session:
        return

    data = await state.get_data()
    selected_ids: set = data.get("selected_ids", set())

    category_map = {c["id"]: c["name"] for c in data.get("categories", [])}

    deleted_names = []
    failed_names = []
    deleted = 0

    for category_id in selected_ids:
        name = category_map.get(category_id, f"ID: {category_id}")
        success = await api_client.delete_category(session["token"], category_id)

        if success:
            deleted += 1
            deleted_names.append(f"{name}")
        else:
            failed_names.append(f"{name}")

    msg = get_message(callback)
    if msg:
        text = "📊 **Result:**\n"
        if deleted > 0:
            text += f"✅ Deleted ({deleted}/{len(selected_ids)}): {', '.join(deleted_names)}.\n"
        if failed_names:
            text += f"⚠️ Cannot delete: {', '.join(failed_names)} (they are used in transactions or budgets)."

        await msg.edit_text(text)

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "category_cancel_many")
async def category_cancel_many(callback: CallbackQuery, state: FSMContext):
    msg = get_message(callback)
    if msg:
        await msg.edit_text("✅ Deletion cancelled.")

    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "category_del_mode:all")
async def category_del_mode_all(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    categories = await get_categories_or_notify_empty(callback, session["token"])
    if categories is None:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes, delete all", callback_data="category_delete_all_confirmed"),
            InlineKeyboardButton(text="❌ No", callback_data="cancel_delete_category"),
        ]
    ])

    msg = get_message(callback)
    if msg:
        await msg.edit_text(f"🗑️ Delete ALL {len(categories)} categories? This cannot be undone.",
                            reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "category_delete_all_confirmed")
async def category_delete_all_confirmed(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    result = await api_client.get_categories(session["token"])
    if not result:
        await callback.answer("❌ Failed to load categories.")
        return

    deleted_names = []
    failed_names = []
    deleted = 0

    for category in result["categories"]:
        name = category["name"]
        success = await api_client.delete_category(session["token"], category["id"])

        if success:
            deleted += 1
            deleted_names.append(f"{name}")
        else:
            failed_names.append(f"{name}")

    msg = get_message(callback)
    if msg:
        text = "📊 **Full Reset Result:**\n"
        if deleted > 0:
            text += f"✅ Successfully deleted ({deleted}/{result['total']}): {', '.join(deleted_names)}.\n"
        if failed_names:
            text += f"⚠️ Cannot delete: {', '.join(failed_names)} (they are used in transactions or budgets)."

        await msg.edit_text(text)

    await callback.answer()
