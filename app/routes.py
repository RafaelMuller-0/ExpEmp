from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User
from app.security import hash_password, verify_password, create_access_token, get_current_user
from app.database import get_session
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, UserUpdate
from app.models.caregiver_profile import CaregiverProfile
from app.schemas.caregiver_profile import CaregiverProfileCreate, CaregiverProfileResponse, CaregiverProfileUpdate

router = APIRouter()

headers={"WWW-Authenticate": "Bearer"}

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
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    stmt = select(User).where(User.email == form_data.username)
    existing_user = db.scalar(stmt)
    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers=headers
        )
    password_valid = verify_password(
        form_data.password,
        existing_user.password_hash
    )
    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="E-mail ou senha incorretos",
            headers=headers
        )
    access_token = create_access_token(existing_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_current_user(user : User = Depends(get_current_user)):
    return user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    update_data = user_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado foi enviado para atualização"
        )
    if "email" in update_data:
        stmt = select(User).where(
            User.email == update_data["email"],
            User.id != user.id
        )
        existing_user = db.scalar(stmt)
        if existing_user:
            raise HTTPException(
                status_code=409,
                detail="E-mail já cadastrado"
            )
    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user

@router.post(
    "/caregiver-profile",
    response_model=CaregiverProfileResponse,
    status_code=201
)
def create_caregiver_profile(
    profile_data: CaregiverProfileCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    existing_profile = db.scalar(stmt)
    if existing_profile:
        raise HTTPException(
            status_code=409,
            detail="Usuário já possui um perfil de cuidador"
        )
    new_profile = CaregiverProfile(
        user_id=user.id,
        bio=profile_data.bio,
        experience_years=profile_data.experience_years,
        approval_status="pending"
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile

@router.get("/caregiver-profile/me", response_model=CaregiverProfileResponse)
def read_current_caregiver_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )
    return profile

@router.put(
    "/caregiver-profile/me",
    response_model=CaregiverProfileResponse
)
def update_caregiver_profile(
    profile_data: CaregiverProfileUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )

    update_data = profile_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado foi enviado para atualização"
        )
    for field, value in update_data.items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile