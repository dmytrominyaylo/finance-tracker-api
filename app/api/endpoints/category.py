from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import DBSession, CurrentUserId
from app.exceptions.base import NotFoundException
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryList, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter()


def get_category_repository(session: DBSession) -> CategoryRepository:
    return CategoryRepository(session)

CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_category_repository)]


def get_category_service(session: DBSession, repo: CategoryRepositoryDep) -> CategoryService:
    return CategoryService(session, repo)

CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


@router.post(
    "/",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    payload: CategoryCreate,
    service: CategoryServiceDep,
    current_user_id: CurrentUserId,
):
    return await service.create_category(payload, current_user_id)


@router.get(
    "/",
    response_model=CategoryList,
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    service: CategoryServiceDep,
    current_user_id: CurrentUserId,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return await service.get_all_categories(current_user_id, offset=offset, limit=limit)


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
)
async def get_category(
    category_id: int,
    service: CategoryServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.get_category_by_id(category_id, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    service: CategoryServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.update_category(category_id, payload, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: int,
    service: CategoryServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        await service.delete_category(category_id, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )
