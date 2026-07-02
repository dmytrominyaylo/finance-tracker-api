user_sessions: dict[int, dict] = {}


def save_session(telegram_id: int, token: str, user_id: int):
    user_sessions[telegram_id] = {"token": token, "user_id": user_id}


def get_session(telegram_id: int) -> dict | None:
    return user_sessions.get(telegram_id)


def clear_session(telegram_id: int):
    user_sessions.pop(telegram_id, None)
