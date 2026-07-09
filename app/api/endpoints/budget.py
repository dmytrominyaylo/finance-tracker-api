from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import DBSession, CurrentUserId
from app.exceptions.base import NotFoundException
from app.repositories.category_repository import CategoryRepository
from app.repositories.budget_repository import BudgetRepository
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetList, BudgetUpdate
from app.services.budget_service import BudgetService

router = APIRouter()


def get_budget_repository(session: DBSession) -> BudgetRepository:
    return BudgetRepository(session)

BudgetRepositoryDep = Annotated[BudgetRepository, Depends(get_budget_repository)]


def get_category_repository(session: DBSession) -> CategoryRepository:
    return CategoryRepository(session)

CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_category_repository)]


def get_budget_service(
        session: DBSession,
        repo: BudgetRepositoryDep,
        category_repo: CategoryRepositoryDep
) -> BudgetService:
    return BudgetService(session, repo, category_repo)

BudgetServiceDep = Annotated[BudgetService, Depends(get_budget_service)]


@router.post(
    "/",
    response_model=BudgetRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_budget(
    payload: BudgetCreate,
    service: BudgetServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.create_budget(payload, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.get(
    "/",
    response_model=BudgetList,
    status_code=status.HTTP_200_OK,
)
async def get_all_budgets(
    service: BudgetServiceDep,
    current_user_id: CurrentUserId,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return await service.get_all_budgets(current_user_id, offset=offset, limit=limit)


@router.get(
    "/{budget_id}",
    response_model=BudgetRead,
    status_code=status.HTTP_200_OK,
)
async def get_budget(
    budget_id: int,
    service: BudgetServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.get_budget_by_id(budget_id, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.patch(
    "/{budget_id}",
    response_model=BudgetRead,
    status_code=status.HTTP_200_OK,
)
async def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    service: BudgetServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.update_budget(budget_id, payload, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_budget(
    budget_id: int,
    service: BudgetServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        await service.delete_budget(budget_id, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )
