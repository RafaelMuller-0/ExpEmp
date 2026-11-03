from pwdlib import PasswordHash
import jwt
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

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