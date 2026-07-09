from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.api_client import api_client
from app.bot.helpers import (
    get_valid_session,
    get_message,
    fetch_or_notify_empty,
    get_categories_or_notify_empty,
    extract_category_name,
    get_confirmation_keyboard,
    handle_mass_delete_result,
)
from app.bot.keyboards.categories import get_categories_keyboard
from app.bot.keyboards.menus import get_transactions_submenu, get_delete_mode_keyboard, get_multiselect_keyboard

router = Router()


class TransactionStates(StatesGroup):
    waiting_category = State()
    waiting_amount = State()
    waiting_type = State()
    waiting_description = State()
    selecting_many = State()


def _tx_label(t: dict) -> str:
    return f"{t['amount']} — {t['description']} ({t['transactionDate']})"


@router.message(F.text == "💸 Transactions")
async def transactions_menu_handler(message: Message):
    if await get_valid_session(message):
        await message.answer("💸 Transactions menu:", reply_markup=get_transactions_submenu())


@router.callback_query(F.data == "transactions_menu:list")
async def transactions_list_callback(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    result = await api_client.get_transactions(session["token"])
    if not result or result["total"] == 0:
        text = "📋 You don't have any transactions yet."
    else:
        text = "📋 Your transactions:\n\n"
        for t in result["transactions"]:
            text += f"{'🟢' if t['type'] == 'income' else '🔴'} {_tx_label(t)}\n"

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(text)
    await callback.answer()


@router.callback_query(F.data == "transactions_menu:add")
async def transactions_add_callback(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)
    if not session:
        return

    categories = await get_categories_or_notify_empty(callback, session["token"])
    if not categories:
        return

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            "📂 Choose a category:",
            reply_markup=get_categories_keyboard(categories,
            "tx_category")
        )

    await state.set_state(TransactionStates.waiting_category)
    await callback.answer()


@router.callback_query(TransactionStates.waiting_category, F.data.startswith("tx_category:"))
async def category_chosen_handler(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        return

    category_id = int(callback.data.split(":")[1])
    category_name = extract_category_name(callback, "Transaction Category")

    await state.update_data(category_id=category_id, category_name=category_name)
    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(f"📂 Category: **{category_name}**\n💵 Enter amount:")

    await state.set_state(TransactionStates.waiting_amount)
    await callback.answer()


@router.message(TransactionStates.waiting_amount)
async def amount_handler(message: Message, state: FSMContext):
    try:
        amount = float(message.text) if message.text else 0.0
    except (ValueError, TypeError):
        await message.answer("⚠️ Please enter a valid amount (e.g. 100.50).")
        return

    await state.update_data(amount=amount)
    data = await state.get_data()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Income", callback_data="tx_type:income")],
        [InlineKeyboardButton(text="🔴 Expense", callback_data="tx_type:expense")],
    ])
    await message.answer(
        f"📂 Category: **{data['category_name']}**\n💵 Amount: **{amount}**\n\n📊 Choose type:",
        reply_markup=keyboard
    )

    await state.set_state(TransactionStates.waiting_type)


@router.callback_query(TransactionStates.waiting_type, F.data.startswith("tx_type:"))
async def type_chosen_handler(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        return

    tx_type = callback.data.split(":")[1]
    await state.update_data(type=tx_type)
    data = await state.get_data()

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            f"📂 Category: **{data['category_name']}**\n"
            f"💵 Amount: **{data['amount']}**\n"
            f"📊 Type: **{'🟢 Income' if tx_type == 'income' else '🔴 Expense'}**\n\n"
            f"📝 Enter description:"
        )
    await state.set_state(TransactionStates.waiting_description)
    await callback.answer()


@router.message(TransactionStates.waiting_description)
async def description_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    session = await get_valid_session(message)
    if not session:
        return

    result = await api_client.create_transaction(
        token=session["token"],
        category_id=data["category_id"],
        amount=data["amount"],
        transaction_type=data["type"],
        description=message.text or "",
        transaction_date=str(date.today()),
    )
    if result:
        await message.answer(
            f"✅ Transaction created!\n"
            f"📂 Category: **{data['category_name']}**\n"
            f"{'🟢' if data['type'] == 'income' else '🔴'} **{data['amount']}** — {message.text}"
        )
    else:
        await message.answer("❌ Failed to create transaction.")
    await state.clear()


@router.callback_query(F.data == "transactions_menu:delete")
async def transactions_delete_callback(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    txs = await fetch_or_notify_empty(
        callback,
        api_client.get_transactions,
        session["token"],
        "📋 You don't have any transactions yet."
    )
    if not txs:
        return

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            "🗑️ How do you want to delete?",
            reply_markup=get_delete_mode_keyboard("tx")
        )

    await callback.answer()


@router.callback_query(F.data == "tx_del_mode:one")
async def tx_del_mode_one(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    txs = await fetch_or_notify_empty(
        callback,
        api_client.get_transactions,
        session["token"],
        "📋 You don't have any transactions yet."
    )
    if not txs:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=_tx_label(t),
        callback_data=f"delete_tx:{t['id']}")] for t in txs]
    )
    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text("🗑️ Choose a transaction to delete:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("delete_tx:"))
async def delete_transaction_confirm(callback: CallbackQuery):
    if not callback.data:
        return

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            "🗑️ Are you sure you want to delete this transaction?",
            reply_markup=get_confirmation_keyboard(f"confirm_delete_tx:{callback.data.split(':')[1]}",
            "cancel_delete_tx")
        )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_tx:"))
async def delete_transaction_callback(callback: CallbackQuery):
    if not callback.data:
        return

    tx_id = int(callback.data.split(":")[1])
    session = await get_valid_session(callback)
    if not session:
        return

    label = f"ID: {tx_id}"
    res = await api_client.get_transactions(session["token"])
    if res:
        label = next((_tx_label(t) for t in res["transactions"] if t["id"] == tx_id), label)

    success = await api_client.delete_transaction(session["token"], tx_id)
    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            f"✅ Transaction {label} deleted!" if success else f"❌ Failed to delete transaction {label}."
        )

    await callback.answer()


@router.callback_query(F.data == "cancel_delete_tx")
async def cancel_delete_tx_callback(callback: CallbackQuery):
    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text("✅ Deletion cancelled.")
    await callback.answer()


@router.callback_query(F.data == "tx_del_mode:many")
async def tx_del_mode_many(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)
    if not session:
        return

    txs = await fetch_or_notify_empty(
        callback,
        api_client.get_transactions,
        session["token"],
        "📋 You don't have any transactions yet."
    )
    if not txs:
        return

    items = [{"id": t["id"], "label": _tx_label(t)} for t in txs]
    await state.update_data(items=items, selected_ids=set())
    await state.set_state(TransactionStates.selecting_many)

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            "🗑️ Select transactions to delete:",
            reply_markup=get_multiselect_keyboard(items, "tx", "label", "id", set())
        )

    await callback.answer()


@router.callback_query(TransactionStates.selecting_many, F.data.startswith("tx_toggle:"))
async def tx_toggle_selection(callback: CallbackQuery, state: FSMContext):
    if not callback.data:
        return

    item_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    selected = data.get("selected_ids", set())
    selected.discard(item_id) if item_id in selected else selected.add(item_id)

    await state.update_data(selected_ids=selected)
    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_reply_markup(
            reply_markup=get_multiselect_keyboard(data["items"], "tx", "label", "id", selected)
        )

    await callback.answer()


@router.callback_query(TransactionStates.selecting_many, F.data == "tx_confirm_many")
async def tx_confirm_many(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_ids", set())
    if not selected:
        await callback.answer("⚠️ No transactions selected.")
        return

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            f"🗑️ Delete {len(selected)} selected transactions?",
            reply_markup=get_confirmation_keyboard("tx_delete_many_confirmed", "tx_cancel_many")
        )

    await callback.answer()


@router.callback_query(F.data == "tx_delete_many_confirmed")
async def tx_delete_many_confirmed(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)
    if not session:
        return
    data = await state.get_data()
    tx_map = {i["id"]: i["label"] for i in data.get("items", [])}

    await handle_mass_delete_result(
        callback,
        state,
        data.get("selected_ids", set()), tx_map, api_client.delete_transaction, session["token"],
        "Mass Delete"
    )


@router.callback_query(F.data == "tx_cancel_many")
async def tx_cancel_many(callback: CallbackQuery, state: FSMContext):
    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text("✅ Deletion cancelled.")
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "tx_del_mode:all")
async def tx_del_mode_all(callback: CallbackQuery):
    session = await get_valid_session(callback)
    if not session:
        return

    txs = await fetch_or_notify_empty(
        callback,
        api_client.get_transactions,
        session["token"],
        "📋 You don't have any transactions yet."
    )
    if not txs:
        return

    msg = get_message(callback)
    if isinstance(msg, Message):
        await msg.edit_text(
            "🗑️ Delete ALL transactions? This cannot be undone.",
            reply_markup=get_confirmation_keyboard("tx_delete_all_confirmed", "cancel_delete_tx")
        )

    await callback.answer()


@router.callback_query(F.data == "tx_delete_all_confirmed")
async def tx_delete_all_confirmed(callback: CallbackQuery, state: FSMContext):
    session = await get_valid_session(callback)
    if not session:
        return
    res = await api_client.get_transactions(session["token"])
    if not res:
        return

    tx_map = {t["id"]: _tx_label(t) for t in res["transactions"]}
    await handle_mass_delete_result(
        callback,
        state,
        set(tx_map.keys()),
        tx_map,
        api_client.delete_transaction,
        session["token"],
        "Full Reset"
    )
