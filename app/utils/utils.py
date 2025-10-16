import uuid
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from passlib.context import CryptContext
from starlette import status

from app.settings.config import ALGORITHM, SECRET_KEY
from app.settings.schemas import Auth

secret_key = SECRET_KEY
algorithm = ALGORITHM

bearer_scheme = HTTPBearer()


pdw_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto") 


def generate_uid() -> str:
    """ Generate a unique identifier (UID) using UUID4."""
    return str(uuid.uuid4())

def generate_iban() -> str:
    """ Generate a pseudo-random IBAN for demonstration purposes."""
    return "FR76" + str(uuid.uuid4().int)[:20] + "RobuxCommunity"  

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