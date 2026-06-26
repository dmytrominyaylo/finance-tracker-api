import pytest
from unittest.mock import AsyncMock, MagicMock

from app.exceptions.base import ConflictException
from app.schemas.user import UserCreate
from app.services.user_service import UserService


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_by_email = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    return repo


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def user_service(mock_session, mock_repo):
    return UserService(mock_session, mock_repo)


async def test_create_user_success(user_service, mock_repo):
    payload = UserCreate(email="test@gmail.com", password="password123")
    mock_repo.create.return_value = MagicMock(
        id=1,
        email="test@gmail.com",
        is_active=True,
    )

    user = await user_service.create_user(payload)

    assert user.email == "test@gmail.com"
    assert user.is_active is True
    mock_repo.create.assert_called_once()


async def test_create_user_conflict(user_service, mock_repo):
    payload = UserCreate(email="test@gmail.com", password="password123")
    mock_repo.get_by_email.return_value = MagicMock(id=1, email="test@gmail.com")

    with pytest.raises(ConflictException):
        await user_service.create_user(payload)


async def test_authenticate_user_success(user_service, mock_repo):
    from app.utils.security import hash_password
    hashed = hash_password("password123")
    mock_repo.get_by_email.return_value = MagicMock(
        id=1,
        email="test@gmail.com",
        password_hash=hashed,
        is_active=True,
    )

    user = await user_service.authenticate_user("test@gmail.com", "password123")

    assert user.email == "test@gmail.com"


async def test_authenticate_user_invalid_password(user_service, mock_repo):
    from app.utils.security import hash_password
    hashed = hash_password("password123")
    mock_repo.get_by_email.return_value = MagicMock(
        id=1,
        email="test@gmail.com",
        password_hash=hashed,
        is_active=True,
    )

    from app.exceptions.base import UnauthorizedException
    with pytest.raises(UnauthorizedException):
        await user_service.authenticate_user("test@gmail.com", "wrongpassword")


async def test_authenticate_user_not_found(user_service, mock_repo):
    mock_repo.get_by_email.return_value = None

    from app.exceptions.base import UnauthorizedException
    with pytest.raises(UnauthorizedException):
        await user_service.authenticate_user("notexist@gmail.com", "password123")
