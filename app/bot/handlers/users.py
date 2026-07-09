from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.api_client import api_client
from app.bot.storage import clear_session
from app.bot.keyboards.menus import get_user_settings_submenu
from app.bot.handlers.auth import get_login_keyboard
from app.bot.helpers import get_valid_session, get_message

router = Router()


class UpdateEmailStates(StatesGroup):
    waiting_email = State()


class UpdatePasswordStates(StatesGroup):
    waiting_password = State()


@router.message(F.text == "👤 User Settings")
async def user_settings_menu_handler(message: Message):
    session = await get_valid_session(message)

    if not session:
        return

    await message.answer("👤 User settings:", reply_markup=get_user_settings_submenu())


@router.callback_query(F.data == "user_menu:profile")
async def profile_callback(callback: CallbackQuery):
    session = await get_valid_session(callback)

    if not session:
        return

    result = await api_client.get_me(session["token"], session["user_id"])

    if not result:
        text = "❌ Failed to load profile."
    else:
        text = (
            f"👤 Your profile:\n\n"
            f"📧 Email: {result['email']}\n"
            f"📅 Member since: {result['createdAt'][:10]}"
        )

    msg = get_message(callback)
    if msg:
        await msg.edit_text(text)

    await callback.answer()


@router.callback_query(F.data == "user_menu:email")
async def change_email_callback(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)

    if not session:
        return

    msg = get_message(callback)
    if msg:
        await msg.edit_text("📧 Enter new email:")

    await state.set_state(UpdateEmailStates.waiting_email)
    await callback.answer()


@router.message(UpdateEmailStates.waiting_email)
async def change_email_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    session = await get_valid_session(message)

    if not session:
        return

    result, status_code = await api_client.update_email(session["token"], session["user_id"], message.text)

    if result:
        await message.answer("✅ Email updated successfully!")
    elif status_code == 409:
        await message.answer("⚠️ This email is already taken.")
    else:
        await message.answer("❌ Failed to update email.")

    await state.clear()


@router.callback_query(F.data == "user_menu:password")
async def change_password_callback(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)

    if not session:
        return

    msg = get_message(callback)
    if msg:
        await msg.edit_text("🔒 Enter new password (min 6 characters):")

    await state.set_state(UpdatePasswordStates.waiting_password)
    await callback.answer()


@router.message(UpdatePasswordStates.waiting_password)
async def change_password_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    session = await get_valid_session(message)

    if not session:
        return

    if len(message.text) < 6:
        await message.answer("⚠️ Password must be at least 6 characters.")
        return

    result = await api_client.update_password(session["token"], session["user_id"], message.text)

    if result:
        await message.answer("✅ Password updated successfully!")
    else:
        await message.answer("❌ Failed to update password.")

    await state.clear()


@router.callback_query(F.data == "user_menu:delete")
async def delete_account_confirm(callback: CallbackQuery):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="confirm_delete_account"),
            InlineKeyboardButton(text="❌ No", callback_data="cancel_delete_account"),
        ]
    ])

    msg = get_message(callback)
    if msg:
        await msg.edit_text(
            "🗑️ Are you sure you want to delete your account? This action cannot be undone.",
            reply_markup=keyboard,
        )

    await callback.answer()


@router.callback_query(F.data == "confirm_delete_account")
async def delete_account_callback(callback: CallbackQuery):
    session = await get_valid_session(callback)

    if not session:
        return

    success = await api_client.delete_account(session["token"], session["user_id"])

    msg = get_message(callback)
    if msg:
        if success:
            if callback.from_user:
                clear_session(callback.from_user.id)
            await msg.edit_text("✅ Account deleted. We're sad to see you go!")
            await msg.answer(
                "👋 Use the buttons below to sign in or register again.",
                reply_markup=get_login_keyboard(),
            )
        else:
            await msg.edit_text("❌ Failed to delete account.")

    await callback.answer()


@router.callback_query(F.data == "cancel_delete_account")
async def cancel_delete_account_callback(callback: CallbackQuery):
    msg = get_message(callback)
    if msg:
        await msg.edit_text("✅ Deletion cancelled.")

    await callback.answer()
