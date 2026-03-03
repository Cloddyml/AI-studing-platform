from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class StatusResponse(BaseModel):
    status: str = "OK"
