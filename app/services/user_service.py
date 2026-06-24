from app.exceptions.base import ConflictException, NotFoundException, UnauthorizedException
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password


class UserService:
    def __init__(self, session, repo):
        self._session = session
        self._repo = repo

    async def create_user(self, payload: UserCreate):
        existing_user = await self._repo.get_by_email(payload.email)

        if existing_user:
            raise ConflictException("User already exists")

        user_data = {
            "email": payload.email,
            "password_hash": hash_password(payload.password),
            "is_active": True,
        }

        user = await self._repo.create(user_data)

        await self._session.commit()

        return user

    async def get_user_by_id(self, user_id: int):
        user = await self._repo.get(user_id)

        if not user:
            raise NotFoundException("User not found")

        return user

    async def get_all_users(self, offset: int = 0, limit: int = 100):
        users = await self._repo.get_many(offset=offset, limit=limit)

        return {"users": users, "total": len(users)}

    async def update_user(self, user_id: int, payload: UserUpdate, current_user_id: int):
        if user_id != current_user_id:
            raise UnauthorizedException("You can only update your own account")

        user = await self._repo.get(user_id)

        if not user:
            raise NotFoundException("User not found")

        update_data = {}

        if payload.email is not None:
            existing = await self._repo.get_by_email(payload.email)
            if existing and existing.id != user_id:
                raise ConflictException("Email already taken")
            update_data["email"] = payload.email

        if payload.password is not None:
            update_data["password_hash"] = hash_password(payload.password)

        user = await self._repo.update(user_id, update_data)

        await self._session.commit()

        return user

    async def delete_user(self, user_id: int, current_user_id: int):
        if user_id != current_user_id:
            raise UnauthorizedException("You can only delete your own account")

        user = await self._repo.get(user_id)

        if not user:
            raise NotFoundException("User not found")

        await self._repo.delete(user_id)

        await self._session.commit()

    async def authenticate_user(self, email: str, password: str):
        user = await self._repo.get_by_email(email)

        if not user:
            raise UnauthorizedException("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedException("User is inactive")

        return user
