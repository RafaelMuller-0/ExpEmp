from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.security import hash_password
from app.database import get_session
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Hello World"}

@router.post("/user", response_model=UserResponse, status_code= 201)
def create_user(user: UserCreate, db: Session = Depends(get_session)):
    stmt = select(User).where(User.email == user.email)
    existing_user = db.scalar(stmt)
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="E-mail já cadastrado"
        )
    hashed_password = hash_password(user.password)
    new_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user