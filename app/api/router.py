from fastapi import APIRouter

from app.api.endpoints import user, auth, category, transaction

api_router = APIRouter()

api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(category.router, prefix="/categories", tags=["Categories"])
api_router.include_router(transaction.router, prefix="/transactions", tags=["Transactions"])
