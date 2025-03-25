from datetime import datetime

from beanie import Document, PydanticObjectId

from typing import Annotated, Literal
from pydantic import Field, field_serializer

class Posts(Document):
    title: str = Field(..., title="Title of the post", max_length=100)
    content: str = Field(..., title="Content of the post", max_length=1000)
    creator: str = Field(..., title="Creator of the post")
    created_at: datetime = Field(default_factory=datetime.now, title="Date of creation")
    tags: list[str] = Field([], title="Tags of the post")
    
    @field_serializer("id")
    def convert_pydantic_object_id_to_string(self, id:PydanticObjectId) -> str:
        return str(id)
    
    @field_serializer("created_at")
    def convert_created_at_to_string(self, created_at: datetime) -> str:
        return str(created_at)