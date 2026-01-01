import uuid
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from passlib.context import CryptContext
from starlette import status
from sqlmodel import Session

from app.settings.config import ALGORITHM, SECRET_KEY
from app.settings.schemas import Auth, Bank_Extern

secret_key = SECRET_KEY
algorithm = ALGORITHM

bearer_scheme = HTTPBearer()


pdw_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto") 


def generate_uid() -> str:
    """ Generate a unique identifier (UID) using UUID4."""
    return str(uuid.uuid4())

def generate_iban(session: Session) -> str:
    """ Generate a pseudo-random IBAN for demonstration purposes using the main bank's suffix."""
    # Get the main bank's IBAN to extract the suffix
    main_bank = session.query(Bank_Extern).filter(Bank_Extern.is_main == True).first()

    if main_bank and main_bank.iban:
        # Extract the suffix from the main bank's IBAN (everything after FR76 + 20 digits)
        suffix = main_bank.iban[24:]  # Skip "FR76" (4 chars) + 20 digits
    else:
        # Fallback to default suffix if no main bank found
        suffix = "REPUBLIC"

    return "FR76" + str(uuid.uuid4().int)[:20] + suffix  

def hash_password(password: str) -> str:
    """ Hash a plain password using Passlib's CryptContext."""
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

def get_user(authorization: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """ Decode the JWT token to get user information """
    try:
        return jwt.decode(authorization.credentials, secret_key, algorithms=[algorithm])
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")