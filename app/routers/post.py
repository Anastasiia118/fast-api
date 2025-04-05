from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from ..database import get_db
from app import schemas, models, oauth2

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


# @router.get("/", response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
        db: Session = Depends(get_db),
        current_user: schemas.TokenData = Depends(oauth2.get_current_user),
        limit: int = 10,
        skip: int = 0,
        search: Optional[str] = ""
    ):
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).filter(
        models.Post.title.contains(search)).group_by(models.Post.id).limit(limit).offset(skip).all()
    
    return results

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
      post: schemas.PostCreate,
      db: Session = Depends(get_db),
      current_user: schemas.TokenData = Depends(oauth2.get_current_user)
    ):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
      id: int,
      db: Session = Depends(get_db),
      current_user: schemas.TokenData = Depends(oauth2.get_current_user)
    ):
    result = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).filter(
        models.Post.id == id).group_by(models.Post.id).first()
    
    if not result:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return result

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
      id: int,
      db: Session = Depends(get_db),
      current_user: schemas.TokenData = Depends(oauth2.get_current_user)
    ):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} was not found")
    if post.first().owner_id != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(
      id: int, post: schemas.PostCreate,
      db: Session = Depends(get_db),
      current_user: schemas.TokenData = Depends(oauth2.get_current_user),
    ):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if existing_post == None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} does not exist")
    
    if existing_post.owner_id != int(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

