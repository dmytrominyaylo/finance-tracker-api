from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

MENU_BUTTONS = {
    "💰 Balance",
    "📂 Categories",
    "💸 Transactions",
    "📊 Budgets",
    "👤 User Settings",
    "🚪 Sign out",
    "🔐 Sign in",
    "📝 Sign up",
}


class CancelFSMOnMenuButtonMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        state = data.get("state")

        if isinstance(state, FSMContext) and event.text in MENU_BUTTONS:
            current_state = await state.get_state()
            if current_state is not None:
                await state.clear()
                await event.answer("❌ Action cancelled.")
                return None

        return await handler(event, data)
