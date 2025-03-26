from beanie import Document, PydanticObjectId

from typing import Annotated, Literal
from pydantic import Field, field_serializer

from datetime import datetime


class Messages(Document):
    content: Annotated[str, Field(max_length=1000)]
    sender: Annotated[str, Field(max_length=100)]
    created: Annotated[datetime, Field(default_factory=datetime.now)]
    recipient: Annotated[str, Field(max_length=100, description="Chat ID of the chat the message belongs to")]
    response_to: Annotated[str | None, Field(max_length=100, description="Message ID of the message this message is a response to")] = None
    
    @field_serializer("id")
    def convert_pydantic_object_id_to_string(self, id:PydanticObjectId) -> str:
        return str(id)