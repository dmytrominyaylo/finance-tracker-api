from aiogram import Router, F
from aiogram.types import Message

from app.bot.api_client import api_client
from app.bot.helpers import get_valid_session

router = Router()


@router.message(F.text == "💰 Balance")
async def balance_handler(message: Message):
    session = await get_valid_session(message)

    if not session:
        return

    tx_result = await api_client.get_transactions(session["token"])
    cat_result = await api_client.get_categories(session["token"])

    if not tx_result or tx_result["total"] == 0:
        await message.answer("💰 Your balance: 0.00\n\nNo transactions yet.")
        return

    transactions = tx_result["transactions"]
    categories = {c["id"]: c["name"] for c in cat_result["categories"]} if cat_result else {}

    income = sum(float(t["amount"]) for t in transactions if t["type"] == "income")
    expense = sum(float(t["amount"]) for t in transactions if t["type"] == "expense")
    balance = income - expense

    text = (
        f"💰 Your balance: {balance:.2f}\n\n"
        f"🟢 Income: {income:.2f}\n"
        f"🔴 Expense: {expense:.2f}\n"
    )

    category_income: dict[int, float] = {}
    category_expenses: dict[int, float] = {}

    for t in transactions:
        cat_id = t["categoryId"]
        amount = float(t["amount"])
        if t["type"] == "income":
            category_income[cat_id] = category_income.get(cat_id, 0) + amount
        else:
            category_expenses[cat_id] = category_expenses.get(cat_id, 0) + amount

    if category_income:
        text += "\n🟢 Income by category:\n"
        for cat_id, amount in sorted(category_income.items(), key=lambda x: -x[1]):
            cat_name = categories.get(cat_id, "Unknown")
            text += f"  • {cat_name}: {amount:.2f}\n"

    if category_expenses:
        text += "\n🔴 Expenses by category:\n"
        for cat_id, amount in sorted(category_expenses.items(), key=lambda x: -x[1]):
            cat_name = categories.get(cat_id, "Unknown")
            text += f"  • {cat_name}: {amount:.2f}\n"

    await message.answer(text)
