import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request
from passlib.context import CryptContext
from starlette import status
from sqlmodel import Session
import jwt

from app.settings.config import ALGORITHM, SECRET_KEY, IS_PROD
from app.settings.schemas import Auth, Bank_Extern

secret_key = SECRET_KEY
algorithm = ALGORITHM

COOKIE_NAME = "access_token"
TOKEN_EXPIRE_DAYS = 7

pdw_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


def generate_uid() -> str:
    """ Generate a unique identifier (UID) using UUID4."""
    return str(uuid.uuid4())

def generate_iban(session: Session) -> str:
    """ Generate a pseudo-random IBAN for demonstration purposes using the main bank's suffix."""
    main_bank = session.query(Bank_Extern).filter(Bank_Extern.is_main == True).first()

    if main_bank and main_bank.iban:
        suffix = main_bank.iban[24:]
    else:
        suffix = "REPUBLIC"

    return "FR76" + str(uuid.uuid4().int)[:20] + suffix

def hash_password(password: str) -> str:
    """ Hash a plain password using bcrypt (12 rounds)."""
    return pdw_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Verify a plain password against a hashed password."""
    return pdw_context.verify(plain_password, hashed_password)

def check_user_password(uid: str, plain_password: str, session):
    """ Check if the provided password matches the stored password for the user with the given UID """
    auth = session.query(Auth).filter(Auth.uid == uid).first()
    if not auth:
        raise HTTPException(status_code=404, detail="Authentication record not found")

    if not verify_password(plain_password, auth.password):
        raise HTTPException(status_code=403, detail="Incorrect password")

    return True

def get_user(request: Request):
    """ Decode the JWT token from the httpOnly cookie to get user information """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié",
        )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expirée",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide",
        )
