from bson.errors import InvalidId

from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And

from fastapi import APIRouter, Security, status, HTTPException, Query
from fastapi.responses import JSONResponse

from typing import Annotated, Literal
from pydantic import ValidationError, Field

from models.request.councilor import NewCouncilor
from schemas.councilor import Councilor

from schemas.users import Users

from security.helpers import get_password_hash, get_current_active_user

router = APIRouter(
    prefix='/api/v1/councilor',
    tags=['Councilor']
)
current_date = datetime.now()

@router.post("")
async def create_councilor(request: NewCouncilor):
    new_councilor = Councilor(
        f_name=request.f_name,
        l_name=request.l_name,
        email=request.email,
        notifications=[],
        g_chats=[],
        bio="",
        permissions=["councilor", "me"],
        password=get_password_hash(request.password)
    )
    
    response = await new_councilor.save()
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Councilor created successfully",
            "data": response.model_dump(exclude=["password", "permissions"])
        }
    )
    

@router.get("")
async def get_councilors(current_user: Annotated[Users, Security(get_current_active_user, scopes=["user"])]):
    #* Retrieve all councilors
    
    councilors_in_db = await Councilor.find_all().to_list()
    councilors = [councilor.model_dump(exclude=["password", "permissions"]) for councilor in councilors_in_db]
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "data": councilors
        }
    )
    