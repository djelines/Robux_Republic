from app.settings.database import get_session
from app.utils.utils import generate_uid
import jwt
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.models import User

secret_key = "give_me_robux_please_for_picture"
algorithm = "HS256"

bearer_scheme = HTTPBearer()

def generate_token(user: User) -> str:
    return jwt.encode(user.dict(), secret_key, algorithm=algorithm)

def get_uid():
    pass

def create_auth(body):
    """ Create authentication credentials for a user """
    pass

def get_password():
    """ Get the hashed password of a user """
    pass

def get_email(uid: str, session=Depends(get_session)) -> str:
    """ Get the email address of a user """
    user = session.query(User).filter(User.uid == uid).first()
    return user.email if user else ""

def update_password():
    """ Update the password of a user """
    pass

def update_email():
    """ Update the email address of a user """
    pass

def update_password():
    """ Update the password of a user """
    pass