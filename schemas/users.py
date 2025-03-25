from beanie import Document, PydanticObjectId

from typing import Annotated, Literal
from pydantic import Field, field_serializer, BaseModel


class Date_Of_Birth(BaseModel):
    day: int = Field(..., title="Day")
    month: int = Field(..., title="Month")
    year: int = Field(..., title="Year")

class Users(Document):
    username: str = Field(..., title="Username")
    email: str = Field(..., title="Email")
    f_name: str = Field(..., title="First Name")
    l_name: str = Field(..., title="Last Name")
    notifications: list[Annotated[PydanticObjectId, Field(..., title="Notification ID")]] = Field([], title="Notifications")
    posts: list[Annotated[PydanticObjectId, Field(..., title="Post ID")]] = Field([], title="Posts")
    addictions: list[Annotated[str, Field(..., title="Addiction ID")]] = Field([], title="Addictions")
    date_of_birth: Date_Of_Birth = Field(..., title="Date of Birth")
    g_chats: list[Annotated[PydanticObjectId, Field(..., title="Group Chat ID")]] = Field([], title="Group Chats")
    c_chats: list[Annotated[PydanticObjectId, Field(..., title="Councilor Chat ID")]] = Field([], title="Councilor Chats")
        
    @field_serializer("id")
    def convert_pydantic_object_id_to_string(self, id:PydanticObjectId) -> str:
        return str(id)