from app.schemas.base import BasePydanticModel


class Token(BasePydanticModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BasePydanticModel):
    subject: int
