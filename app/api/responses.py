from app.exceptions.http_excs import AIStudingHTTPException
from app.schemas.errors import ErrorResponse


def generate_responses(*exc_classes: type[AIStudingHTTPException]) -> dict:
    result: dict = {}
    for exc_cls in exc_classes:
        code = exc_cls.status_code
        entry = result.setdefault(
            code,
            {
                "model": ErrorResponse,
                "description": "",
                "content": {"application/json": {"examples": {}}},
            },
        )
        entry["content"]["application/json"]["examples"][exc_cls.__name__] = {
            "summary": exc_cls.detail,
            "value": {"detail": exc_cls.detail},
        }
        entry["description"] = exc_cls.detail
    return result
