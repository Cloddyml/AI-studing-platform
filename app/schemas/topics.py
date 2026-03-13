from pydantic import BaseModel


class TopicDTO(BaseModel):
    id: int
    slug: str
    title: str
    order_index: int


class TopicDetailDTO(TopicDTO):
    content: str | None
