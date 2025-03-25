from datetime import datetime

from beanie import Document, PydanticObjectId

from typing import Annotated, Literal
from pydantic import Field, BaseModel

current_date = datetime.now()

class NewPost(BaseModel):
    title: str = Field(..., title="Title of the post", max_length=100)
    content: str = Field(..., title="Content of the post", max_length=1000)
    creator: str = Field(..., title="Creator of the post")