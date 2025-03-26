from bson.errors import InvalidId

from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And

from fastapi import APIRouter, Security, status, HTTPException, Query
from fastapi.responses import JSONResponse

from typing import Annotated, Literal
from pydantic import ValidationError, Field

from schemas.messages import Messages
from schemas.users import Users
from schemas.councilor import Councilor
from models.request.messages import NewMessage

from security.helpers import get_current_active_user


router = APIRouter(
    prefix='/api/v1/messages',
    tags=['Messages']
)
current_date = datetime.now()

@router.post("")
async def create_message(request: NewMessage):
    
    recipient = Users.get(PydanticObjectId(request.recipient))
    
    if not recipient:
        recipient = Councilor.get(PydanticObjectId(request.recipient))
    
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    new_message = Messages(
        content=request.content,
        sender=request.sender,
        recipient=request.recipient,
        response_to=request.response_to
    )
    
    try:
        await new_message.insert()
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ID")
    except ValidationError:
        raise HTTPException(status_code=400, detail="Invalid data")
    
    
@router.get("")
async def get_messages(recipient: str, current_user: Annotated[Users, Security(get_current_active_user, scopes=["user"])],sender: str = None):
    
    #* Get all messages in a group chat
    if not sender and recipient:
        messages = await Messages.find_all(
            Messages.recipient == recipient
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": messages
            }
        )
    
    #* Get all messages between two users
    if sender and (PydanticObjectId(sender) == current_user.id) and recipient:    
        messages = await Messages.find_all(
            And(
                Messages.sender == sender,
                Messages.recipient == recipient
            )
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": messages
            }
        )
        
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid request"
    )