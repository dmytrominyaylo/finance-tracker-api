from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from jose import jwt as jose_jwt

from app.bot.api_client import api_client
from app.bot.storage import save_session, get_session, clear_session
from app.bot.keyboards.main import get_main_menu
from app.bot.helpers import get_message

router = Router()


class LoginStates(StatesGroup):
    waiting_email = State()
    waiting_password = State()


class RegisterStates(StatesGroup):
    waiting_email = State()
    waiting_password = State()


def get_login_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="🔐 Sign in"), KeyboardButton(text="📝 Sign up")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


@router.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "👋 Welcome to Finance Tracker Bot!\n\n"
        "Tap one of the buttons below to get started.",
        reply_markup=get_login_keyboard(),
    )


@router.message(F.text == "🔐 Sign in")
async def login_handler(message: Message, state: FSMContext):
    await message.answer("📧 Enter your email:")
    await state.set_state(LoginStates.waiting_email)


@router.message(LoginStates.waiting_email)
async def email_handler(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("🔒 Enter your password:")
    await state.set_state(LoginStates.waiting_password)


@router.message(LoginStates.waiting_password)
async def password_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    email = data["email"]
    password = message.text

    result = await api_client.login(email, password)

    if result:
        token = result["accessToken"]
        payload = jose_jwt.get_unverified_claims(token)
        user_id = payload["subject"]

        if message.from_user:
            save_session(message.from_user.id, token, user_id)
            await message.answer(
                "✅ Login successful! Use the menu below.",
                reply_markup=get_main_menu(),
            )
    else:
        await message.answer(
            "❌ Invalid email or password. Try again.",
            reply_markup=get_login_keyboard(),
        )

    await state.clear()


@router.message(Command("menu"))
async def menu_handler(message: Message):
    if not message.from_user:
        return

    session = get_session(message.from_user.id)

    if not session:
        await message.answer("⚠️ Please Sign in first.", reply_markup=get_login_keyboard())
        return

    await message.answer("📋 Main menu:", reply_markup=get_main_menu())


@router.message(F.text == "🚪 Sign out")
async def logout_start(message: Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yes", callback_data="confirm_sign_out:yes"),
            InlineKeyboardButton(text="❌ No", callback_data="confirm_sign_out:no"),
        ]
    ])
    await message.answer("🚪 Are you sure you want to sign out?", reply_markup=keyboard)


@router.callback_query(F.data == "confirm_sign_out:yes")
async def logout_confirmed(callback: CallbackQuery):
    if not callback.from_user:
        return

    clear_session(callback.from_user.id)

    msg = get_message(callback)
    if msg:
        await msg.edit_text("👋 You've been signed out.")
        await msg.answer(
            "Use the buttons below to sign in again or sign up.",
            reply_markup=get_login_keyboard(),
        )

    await callback.answer()


@router.callback_query(F.data == "confirm_sign_out:no")
async def logout_cancelled(callback: CallbackQuery):
    msg = get_message(callback)
    if msg:
        await msg.edit_text("✅ Sign out cancelled.")

    await callback.answer()


@router.message(F.text == "📝 Sign up")
async def register_handler(message: Message, state: FSMContext):
    await message.answer("📧 Enter your email:")
    await state.set_state(RegisterStates.waiting_email)


@router.message(RegisterStates.waiting_email)
async def register_email_handler(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("🔒 Enter a password (min 6 characters):")
    await state.set_state(RegisterStates.waiting_password)


@router.message(RegisterStates.waiting_password)
async def register_password_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    if len(message.text) < 6:
        await message.answer("⚠️ Password must be at least 6 characters.")
        return

    data = await state.get_data()
    email = data["email"]
    password = message.text

    result, status_code = await api_client.register(email, password)

    if result:
        login_result = await api_client.login(email, password)

        if login_result and message.from_user:
            token = login_result["accessToken"]
            payload = jose_jwt.get_unverified_claims(token)
            user_id = payload["subject"]

            save_session(message.from_user.id, token, user_id)
            await message.answer(
                "✅ Registration successful! You're now signed in.",
                reply_markup=get_main_menu(),
            )
        else:
            await message.answer(
                "✅ Registration successful! Now tap Sign in to continue.",
                reply_markup=get_login_keyboard(),
            )
    elif status_code == 409:
        await message.answer(
            "⚠️ This email is already registered. Go to Sign in.",
            reply_markup=get_login_keyboard(),
        )
    else:
        await message.answer("❌ Registration failed. Try again.")

    await state.clear()
