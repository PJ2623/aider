import re, enum

from fastapi.exceptions import HTTPException
from fastapi import status

from pydantic import Field, BaseModel, field_validator, model_validator, EmailStr
from typing import Literal, Annotated, Self

from datetime import datetime


class NewMessage(BaseModel):
    content: Annotated[str, Field(max_length=1000)]
    sender: Annotated[str, Field(max_length=100, description="Sender of the message's ID")]
    recipient: Annotated[str, Field(max_length=100, description="Id of the person to receive the message")]
    response_to: Annotated[str | None, Field(max_length=100, description="Message ID of the message this message is a response to")] = None