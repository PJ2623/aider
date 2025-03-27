from datetime import datetime

from beanie import Document, PydanticObjectId

from typing import Annotated, Literal
from pydantic import Field, BaseModel


class NewArticles(BaseModel):
    title: str = Field(..., title="Title of the post", max_length=100)
    content: str = Field(..., title="Content of the post", max_length=1000)
    created: datetime = Field(datetime.now, title="Date the post was created")