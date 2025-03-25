from bson.errors import InvalidId

from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And

from fastapi import APIRouter, Security, status, HTTPException, Query
from fastapi.responses import JSONResponse

from typing import Annotated, Literal
from pydantic import ValidationError, Field



router = APIRouter(
    prefix='/api/v1/articles',
    tags=['Articles']
)
current_date = datetime.now()

@router.post("")
async def create_article():
    pass