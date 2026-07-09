from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.api.dependencies import DBSession, CurrentUserId
from app.exceptions.base import NotFoundException
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionList, TransactionUpdate
from app.services.transaction_service import TransactionService

router = APIRouter()


def get_transaction_repository(session: DBSession) -> TransactionRepository:
    return TransactionRepository(session)

TransactionRepositoryDep = Annotated[TransactionRepository, Depends(get_transaction_repository)]


def get_category_repository(session: DBSession) -> CategoryRepository:
    return CategoryRepository(session)

CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_category_repository)]


def get_transaction_service(
        session: DBSession,
        repo: TransactionRepositoryDep,
        category_repo: CategoryRepositoryDep
) -> TransactionService:
    return TransactionService(session, repo, category_repo)

TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]


@router.post(
    "/",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    payload: TransactionCreate,
    service: TransactionServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.create_transaction(payload, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.get(
    "/",
    response_model=TransactionList,
    status_code=status.HTTP_200_OK,
)
async def get_all_transactions(
    service: TransactionServiceDep,
    current_user_id: CurrentUserId,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return await service.get_all_transactions(current_user_id, offset=offset, limit=limit)


@router.get(
    "/{transaction_id}",
    response_model=TransactionRead,
    status_code=status.HTTP_200_OK,
)
async def get_transaction(
    transaction_id: int,
    service: TransactionServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.get_transaction_by_id(transaction_id, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.patch(
    "/{transaction_id}",
    response_model=TransactionRead,
    status_code=status.HTTP_200_OK,
)
async def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    service: TransactionServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        return await service.update_transaction(transaction_id, payload, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transaction(
    transaction_id: int,
    service: TransactionServiceDep,
    current_user_id: CurrentUserId,
):
    try:
        await service.delete_transaction(transaction_id, current_user_id)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.detail,
        )
