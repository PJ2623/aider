from bson.errors import InvalidId

from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And

from fastapi import APIRouter, Security, status, HTTPException, Query
from fastapi.responses import JSONResponse

from typing import Annotated, Literal
from pydantic import ValidationError, Field

from schemas.users import Users
from models.request.users import NewUser

from security.helpers import get_password_hash


router = APIRouter(
    prefix='/api/v1/users',
    tags=['Users']
)
current_date = datetime.now()

@router.post("")
async def create_user(request: NewUser) -> JSONResponse:
    """Create a new user

    Args:
        request (NewUser): The request body

    Returns:
        JSONResponse: The response body
    """
    addictions = [addiction.value for addiction in request.addictions]
    
    new_user = Users(
        username=request.username,
        email=request.email,
        f_name=request.f_name,
        l_name=request.l_name,
        date_of_birth=request.date_of_birth.model_dump(),
        addictions=addictions,
        permissions=["user", "me"],
        password=get_password_hash(request.password),
        account_type=request.account_type
    )
    
    response = await new_user.save()
    return JSONResponse(
        content={
            "message": "Account created successfully",
            "data": response.model_dump(exclude=["permissions", "password"])
        },
        status_code=status.HTTP_201_CREATED
    )