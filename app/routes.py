from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.security import hash_password, verify_password, create_access_token
from app.database import get_session
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token

router = APIRouter()

headers={"WWW-Authenticate": "Bearer"}

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

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_session)):
    stmt = select(User).where(User.email == user.email)
    existing_user = db.scalar(stmt)
    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers = headers
        )
    password_valid = verify_password(user.password, existing_user.password_hash)
    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers=headers
        )
    access_token = create_access_token(existing_user.id)
    return {"access_token": access_token,"token_type": "bearer"
    }