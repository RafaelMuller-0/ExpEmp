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
from app.models.availability import Availability
from app.schemas.availability import AvailabilityCreate, AvailabilityResponse, AvailabilityUpdate
from app.models.care_recipient import CareRecipient
from app.schemas.care_recipient import CareRecipientCreate, CareRecipientResponse, CareRecipientUpdate
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingResponse, BookingStatusUpdate

router = APIRouter()

headers={"WWW-Authenticate": "Bearer"}

async def root():
    return {"message": "Hello World"}

"""User routes"""
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
def update_current_user(user_data: UserUpdate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
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

"""caregiver_profile routes"""
@router.post("/caregiver-profile",response_model=CaregiverProfileResponse,status_code=201)
def create_caregiver_profile(profile_data: CaregiverProfileCreate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
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
def read_current_caregiver_profile(user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )
    return profile

@router.put("/caregiver-profile/me",response_model=CaregiverProfileResponse)
def update_caregiver_profile(profile_data: CaregiverProfileUpdate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
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

"""availability routes"""
@router.post("/availability",response_model=AvailabilityResponse,status_code=201)
def create_availability(availability_data: AvailabilityCreate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )
    if availability_data.end_at <= availability_data.start_at:
        raise HTTPException(
            status_code=400,
            detail="O horário de término deve ser posterior ao início"
        )
    new_availability = Availability(
        caregiver_profile_id=profile.id,
        start_at=availability_data.start_at,
        end_at=availability_data.end_at
    )
    db.add(new_availability)
    db.commit()
    db.refresh(new_availability)
    return new_availability

@router.get("/availability/me",response_model=list[AvailabilityResponse])
def read_my_availabilities(user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )
    stmt = select(Availability).where(Availability.caregiver_profile_id == profile.id)
    availabilities = db.scalars(stmt).all()
    return availabilities

@router.delete("/availability/{availability_id}", status_code=204)
def delete_availability(availability_id: int,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CaregiverProfile).where(
        CaregiverProfile.user_id == user.id
    )
    profile = db.scalar(stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )
    stmt = select(Availability).where(Availability.id == availability_id,Availability.caregiver_profile_id == profile.id)
    availability = db.scalar(stmt)
    if availability is None:
        raise HTTPException(
            status_code=404,
            detail="Disponibilidade não encontrada"
        )
    db.delete(availability)
    db.commit()

@router.put("/availability/{availability_id}",response_model=AvailabilityResponse)
def update_availability(availability_id: int,availability_data: AvailabilityUpdate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )
    stmt = select(Availability).where(Availability.id == availability_id,Availability.caregiver_profile_id == profile.id)
    availability = db.scalar(stmt)
    if availability is None:
        raise HTTPException(
            status_code=404,
            detail="Disponibilidade não encontrada"
        )
    update_data = availability_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado foi enviado para atualização"
        )
    new_start = update_data.get("start_at", availability.start_at)
    new_end = update_data.get("end_at", availability.end_at)
    if new_start is None or new_end is None or new_end <= new_start:
        raise HTTPException(
            status_code=400,
            detail="O horário de término deve ser posterior ao início"
        )
    for field, value in update_data.items():
        setattr(availability, field, value)
    db.commit()
    db.refresh(availability)
    return availability

"""Care_recipient routes"""
@router.post("/care-recipients",response_model=CareRecipientResponse,status_code=201)
def create_care_recipient(recipient_data: CareRecipientCreate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    new_recipient = CareRecipient(
        created_by_user_id=user.id,
        name=recipient_data.name,
        care_notes=recipient_data.care_notes
    )
    db.add(new_recipient)
    db.commit()
    db.refresh(new_recipient)
    return new_recipient

@router.get("/care-recipients",response_model=list[CareRecipientResponse])
def read_my_care_recipients(user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CareRecipient).where(CareRecipient.created_by_user_id == user.id)
    recipients = db.scalars(stmt).all()
    return recipients

@router.put("/care-recipients/{recipient_id}",response_model=CareRecipientResponse)
def update_care_recipient(recipient_id: int,recipient_data: CareRecipientUpdate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CareRecipient).where(CareRecipient.id == recipient_id,CareRecipient.created_by_user_id == user.id)
    recipient = db.scalar(stmt)
    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Assistido não encontrado"
        )

    update_data = recipient_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Nenhum dado foi enviado para atualização"
        )

    for field, value in update_data.items():
        setattr(recipient, field, value)

    db.commit()
    db.refresh(recipient)
    return recipient

@router.delete("/care-recipients/{recipient_id}",status_code=204)
def delete_care_recipient(recipient_id: int,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(CareRecipient).where(CareRecipient.id == recipient_id,CareRecipient.created_by_user_id == user.id    )
    recipient = db.scalar(stmt)
    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Assistido não encontrado"
        )

    db.delete(recipient)
    db.commit()

""" Booking routes"""
@router.post("/bookings",response_model=BookingResponse,status_code=201)
def create_booking(booking_data: BookingCreate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    recipient_stmt = select(CareRecipient).where(CareRecipient.id == booking_data.care_recipient_id,CareRecipient.created_by_user_id == user.id    )
    recipient = db.scalar(recipient_stmt)
    if recipient is None:
        raise HTTPException(
            status_code=404,
            detail="Assistido não encontrado"
        )

    caregiver_stmt = select(CaregiverProfile).where(CaregiverProfile.id == booking_data.caregiver_profile_id,CaregiverProfile.approval_status == "approved")
    caregiver = db.scalar(caregiver_stmt)
    if caregiver is None:
        raise HTTPException(
            status_code=404,
            detail="Cuidador não encontrado ou não aprovado"
        )
    if booking_data.end_at <= booking_data.start_at:
        raise HTTPException(
            status_code=400,
            detail="O horário de término deve ser posterior ao início"
        )
    availability_stmt = select(Availability).where(Availability.caregiver_profile_id == caregiver.id,Availability.start_at <= booking_data.start_at,Availability.end_at >= booking_data.end_at)
    availability = db.scalar(availability_stmt)
    if availability is None:
        raise HTTPException(
            status_code=409,
            detail="Cuidador não possui disponibilidade para esse horário"
        )

    conflict_stmt = select(Booking).where(Booking.caregiver_profile_id == caregiver.id,Booking.status.in_(["pending", "accepted"]),Booking.start_at < booking_data.end_at,Booking.end_at > booking_data.start_at)
    conflict = db.scalar(conflict_stmt)
    if conflict is not None:
        raise HTTPException(
            status_code=409,
            detail="Cuidador já possui um agendamento nesse horário"
        )

    new_booking = Booking(
        requester_user_id=user.id,
        care_recipient_id=recipient.id,
        caregiver_profile_id=caregiver.id,
        start_at=booking_data.start_at,
        end_at=booking_data.end_at,
        address=booking_data.address,
        status="pending"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking

@router.get("/bookings/me",response_model=list[BookingResponse])
def read_my_bookings(user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(Booking).where(Booking.requester_user_id == user.id    )
    bookings = db.scalars(stmt).all()
    return bookings

@router.get("/bookings/caregiver/me",response_model=list[BookingResponse])
def read_caregiver_bookings(user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    profile_stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(profile_stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )

    stmt = select(Booking).where(Booking.caregiver_profile_id == profile.id)
    bookings = db.scalars(stmt).all()
    return bookings

@router.put("/bookings/{booking_id}/status",response_model=BookingResponse)
def update_booking_status(booking_id: int,status_data: BookingStatusUpdate,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    profile_stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(profile_stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )

    stmt = select(Booking).where(Booking.id == booking_id,Booking.caregiver_profile_id == profile.id    )
    booking = db.scalar(stmt)
    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    if status_data.status not in ["accepted", "rejected"]:
        raise HTTPException(
            status_code=400,
            detail="Status deve ser accepted ou rejected"
        )
    if booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Este agendamento não está mais pendente"
        )

    booking.status = status_data.status

    db.commit()
    db.refresh(booking)

    return booking

@router.put("/bookings/{booking_id}/cancel",response_model=BookingResponse)
def cancel_booking(booking_id: int,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    stmt = select(Booking).where(Booking.id == booking_id,Booking.requester_user_id == user.id    )
    booking = db.scalar(stmt)

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )
    if booking.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Somente agendamentos pendentes podem ser cancelados"
        )

    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking

@router.put("/bookings/{booking_id}/complete",response_model=BookingResponse)
def complete_booking(booking_id: int,user: User = Depends(get_current_user),db: Session = Depends(get_session)):
    profile_stmt = select(CaregiverProfile).where(CaregiverProfile.user_id == user.id)
    profile = db.scalar(profile_stmt)
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Perfil de cuidador não encontrado"
        )

    stmt = select(Booking).where(Booking.id == booking_id,Booking.caregiver_profile_id == profile.id    )
    booking = db.scalar(stmt)

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Agendamento não encontrado"
        )

    if booking.status != "accepted":
        raise HTTPException(
            status_code=400,
            detail="Somente agendamentos aceitos podem ser finalizados"
        )

    booking.status = "completed"

    db.commit()
    db.refresh(booking)

    return booking

