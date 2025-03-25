from beanie import Document, PydanticObjectId

from typing import Annotated, Literal
from pydantic import Field, field_serializer


class Chats(Document):
    pass
    
    @field_serializer("id")
    def convert_pydantic_object_id_to_string(self, id:PydanticObjectId) -> str:
        return str(id)