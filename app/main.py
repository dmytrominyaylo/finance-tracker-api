from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router

app = FastAPI(
    title="Finance Tracker API",
    version="1.0.0",
)

app.include_router(api_router, prefix="/api")


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_request: Request, _exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error"},
    )


@app.get("/")
async def root():
    return {"message": "Finance Tracker API is running"}
