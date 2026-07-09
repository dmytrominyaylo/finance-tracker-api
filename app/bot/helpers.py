from typing import Union, Callable, Awaitable
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.bot.storage import get_session
from app.bot.api_client import api_client


async def get_valid_session(event: Union[Message, CallbackQuery]) -> dict | None:
    user = event.from_user

    if not user:
        return None

    session = get_session(user.id)

    if not session:
        await event.answer("⚠️ Please Sign in first.")
        return None

    return session


def get_message(callback: CallbackQuery) -> Message | None:
    if isinstance(callback.message, Message):
        return callback.message
    return None


async def fetch_or_notify_empty(
    callback: CallbackQuery,
    fetch_fn: Callable[[str], Awaitable[dict | None]],
    token: str,
    empty_text: str,
) -> list[dict] | None:
    result = await fetch_fn(token)
    msg = get_message(callback)

    if not result or result["total"] == 0:
        if msg:
            await msg.edit_text(empty_text)
        await callback.answer()
        return None

    key = list(result.keys())
    key.remove("total")
    return result[key[0]]


async def get_categories_or_notify_empty(callback: CallbackQuery, token: str) -> list[dict] | None:
    result = await api_client.get_categories(token)
    msg = get_message(callback)

    if not result or result["total"] == 0:
        if msg:
            await msg.edit_text("📂 You don't have any categories yet.")
        await callback.answer()
        return None

    return result["categories"]


def extract_category_name(callback: CallbackQuery, default: str = "Selected Category") -> str:
    msg = get_message(callback)
    if msg and msg.reply_markup:
        for row in msg.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data == callback.data:
                    return btn.text
    return default


def get_confirmation_keyboard(yes_data: str, no_data: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data=yes_data),
            InlineKeyboardButton(text="❌ No", callback_data=no_data),
        ]
    ])


async def handle_mass_delete_result(
    callback: CallbackQuery,
    state: FSMContext,
    selected_ids: set,
    items_map: dict,
    delete_func: Callable[[str, int], Awaitable[bool]],
    token: str,
    title: str = "Delete",
):
    deleted_names = []
    failed_names = []
    deleted = 0

    for item_id in selected_ids:
        label = items_map.get(item_id, f"ID: {item_id}")
        success = await delete_func(token, item_id)

        if success:
            deleted += 1
            deleted_names.append(label)
        else:
            failed_names.append(label)

    msg = get_message(callback)
    if isinstance(msg, Message):
        text = f"📊 **{title} Result:**\n"
        if deleted > 0:
            text += "✅ Deleted (" + str(deleted) + "/" + str(len(selected_ids)) + "):\n"
            text += "\n".join(f"• {d}" for d in deleted_names) + "\n"
        if failed_names:
            text += "⚠️ Cannot delete (" + str(len(failed_names)) + "):\n"
            text += "\n".join(f"• {f}" for f in failed_names) + "\n(failed or locked items)."

        await msg.edit_text(text)

    await state.clear()
    await callback.answer()
