from pwdlib import PasswordHash
import jwt
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_session
from app.models.user import User

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
password_hash = PasswordHash.recommended()

def hash_password(password : str):
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(user_id : int):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload = {"sub": str(user_id), "exp": expiration}
    key = getenv("JWT_SECRET_KEY")
    if not key:
        raise RuntimeError("JWT_SECRET_KEY não configurada")
    encoded_jwt = jwt.encode(payload, key, algorithm="HS256")
    return encoded_jwt

def decode_access_token(access_token : str):
    key = getenv("JWT_SECRET_KEY")
    if not key:
        raise RuntimeError("JWT_SECRET_KEY não configurada")
    try:
        jwt_token = jwt.decode(access_token, key, algorithms=["HS256"])
        jwt_token_sub = jwt_token.get("sub")
        if jwt_token_sub is None:
            raise InvalidTokenError("Token sem identificação de usuário")
        return int(jwt_token_sub)
    except (InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    decoded_token = decode_access_token(token)
    stmt = select(User).where(User.id == decoded_token)
    existing_user = db.scalar(stmt)
    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return existing_user