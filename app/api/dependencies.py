from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionMaker
from app.utils.jwt import decode_access_token

async def get_session_dep() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionMaker() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_session_dep)]

http_bearer = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> int:
    try:
        payload = decode_access_token(credentials.credentials)
        return payload.subject
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
