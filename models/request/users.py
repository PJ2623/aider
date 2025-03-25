import re

from fastapi.exceptions import HTTPException
from fastapi import status

from pydantic import Field, BaseModel, field_validator, model_validator
from typing import Literal, Annotated, Self


class Date_Of_Birth(BaseModel):
    day: int = Field(..., title="Day")
    month: int = Field(..., title="Month")
    year: int = Field(..., title="Year")

class NewUser(BaseModel):
    username: str = Field(..., title="Username")
    email: str = Field(..., title="Email")
    f_name: str = Field(..., title="First Name")
    l_name: str = Field(..., title="Last Name")
    addictions: Annotated[
        Literal[
            "alcohol",
            "marijuana",
            "cocain",
            "prescription-drugs",
            "tobacco-and-nicotine",
            "explicit-content"],
        Field(..., title="Addictions")
    ] = Field(["alcohol","marijuana", "cocain", "prescription-drugs", "tobacco-and-nicotine", "explicit-content"], title="Addictions")
    date_of_birth: Date_Of_Birth = Field(..., title="Date of Birth")
    password: str = Field(..., title="Password")
    confirm_password: str = Field(..., title="Confirm Password")
    

    # * Validate the password to ensure it has at least one uppercase letter,
    # * one special character, one lowercase letter, and one number
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Password must contain at least one uppercase letter'
            )
        if not re.search(r'[a-z]', v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Password must contain at least one lowercase letter'
            )
        if not re.search(r'\d', v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one number"
            )
        if not re.search(r'[@$!%*?&#]', v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password must contain at least one special character"
            )
        return v
    
    # * Check if password and verify password fields match
    @model_validator(mode='after')
    def check_password_match(self) -> Self:
        password = self.password
        verify_password = self.confirm_password

        if password is not None and verify_password is not None and password != verify_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Passwords do not match"
            )
        return self
        
    # * Check if first name and last name in password
    @model_validator(mode='after')
    def check_first_name_last_name_in_password(self) -> Self:
        first_name = self.first_name
        last_name = self.last_name
        password = self.password

        if first_name in password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password contains first name"
            )
        if last_name in password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Password contains last name"
            )
        return self