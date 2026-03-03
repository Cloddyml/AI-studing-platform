from datetime import datetime

from pydantic import BaseModel


class RefreshTokenAddDTO(BaseModel):
    user_id: int
    hashed_token: str
    expires_at: datetime


class RefreshTokenDTO(BaseModel):
    id: int
    user_id: int
    hashed_token: str
    expires_at: datetime
    revoked: bool
    created_at: datetime
