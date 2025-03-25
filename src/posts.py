from bson.errors import InvalidId

from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import Push

from fastapi import APIRouter, Security, status, HTTPException, Query
from fastapi.responses import JSONResponse

from typing import Annotated

from security.helpers import get_current_active_user

from models.request.posts import NewPost
from schemas.posts import Posts
from schemas.users import Users


router = APIRouter(
    prefix='/api/v1/posts',
    tags=['Posts']
)
current_date = datetime.now()

@router.post("")
async def create_post(request: NewPost, current_user: Annotated[Users, Security(get_current_active_user, scopes=["user"])]):
    
    creator = await Users.find_one(Users.id == PydanticObjectId(request.creator))
    
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator not found"
        )
        
    new_post = Posts(
        title=request.title,
        content=request.content,
        creator=request.creator,
        tags=[addiction for addiction in creator.addictions]
    )
    
    await new_post.save()
    
    # Add ID of new post to list of creator's posts
    await creator.update(Push({Users.posts: new_post.id}))
    await creator.save()
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "Post created successfully",
            "data": new_post.model_dump()
        }
    )