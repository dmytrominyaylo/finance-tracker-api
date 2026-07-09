from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import DBSession
from app.exceptions.base import UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.schemas.token import Token
from app.services.user_service import UserService
from app.utils.jwt import create_access_token

router = APIRouter()


def get_user_repository(session: DBSession) -> UserRepository:
    return UserRepository(session)


def get_user_service(session: DBSession) -> UserService:
    repo = get_user_repository(session)
    return UserService(session, repo)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
async def login(
    email: str,
    password: str,
    service: UserService = Depends(get_user_service),
):
    try:
        user = await service.authenticate_user(email, password)
        access_token = create_access_token(user.id)
        return Token(access_token=access_token)
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.detail,
        )
