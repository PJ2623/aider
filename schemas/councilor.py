from beanie import Document, PydanticObjectId

from typing import Annotated, Literal
from pydantic import Field, field_serializer


class Councilor(Document):
    f_name: str = Field(..., title="First Name")
    l_name: str = Field(..., title="Last Name")
    email: str = Field(..., title="Email")
    notifications: list[Annotated[PydanticObjectId, Field(..., title="Notification ID")]] = Field([], title="Notifications")
    g_chats: list[Annotated[PydanticObjectId, Field(..., title="Group Chat ID")]] = Field([], title="Group Chats")
    bio: str = Field("", title="Biography")
    permissions: list[Annotated[str, Field(..., title="Permission")]]
    password: str = Field(..., title="Password")
    active: bool = Field(True, title="Active")
    
    @field_serializer("id")
    def convert_pydantic_object_id_to_string(self, id:PydanticObjectId) -> str:
        return str(id)