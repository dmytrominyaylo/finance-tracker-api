from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import DBSession, CurrentUserId
from app.exceptions.base import ConflictException, NotFoundException, UnauthorizedException
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead, UserList, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


def get_user_repository(session: DBSession) -> UserRepository:
    return UserRepository(session)

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_user_service(session: DBSession, repo: UserRepositoryDep) -> UserService:
    return UserService(session, repo)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreate,
    service: UserServiceDep,
):
    try:
        return await service.create_user(payload)
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.detail,
        )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def get_user(
    user_id: int,
    service: UserServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.get_user_by_id(user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.get(
    "/",
    response_model=UserList,
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    service: UserServiceDep,
    current_user_id: CurrentUserId,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return await service.get_all_users(offset=offset, limit=limit)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.update_user(user_id, payload, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.detail,
        )
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail,
        )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    service: UserServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        await service.delete_user(user_id, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )
    except UnauthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail,
        )
