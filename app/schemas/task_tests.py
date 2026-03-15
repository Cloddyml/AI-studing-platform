from pydantic import BaseModel


class TaskTestDTO(BaseModel):
    id: int
    task_id: int
    test_code: str
    is_hidden: bool
    order_index: int
