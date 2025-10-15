from sentry_sdk import session
from starlette import status
from sqlmodel import select
from app.services.user import create_user
from app.settings.config import ALGORITHM, SECRET_KEY
from app.settings.database import get_session
from app.utils.utils import *
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.models import User, Auth
from app.settings.schemas import Auth


######################
#     Sign up
####################
def create_auth(body:Auth, session = Depends(get_session))-> Auth:
    """ Create authentication credentials for a user """
    existing_user = session.query(Auth).filter(Auth.email == body.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    new_auth = Auth(uid=body.uid, email=body.email, password=body.password)
    new_auth.password = hash_password(new_auth.password)
    session.add(new_auth)
    session.flush()
    
    new_user = create_user(User(uid=new_auth.uid, first_name=body.first_name, last_name=body.last_name, address=body.address), session)
    
    session.commit()
    session.refresh(new_auth)
    session.refresh(new_user)
    return {
        "auth": new_auth,
        "user": new_user
    }


######################
#     Log in
####################
def generate_token(auth: Auth):
    """ Generate a JWT token """
    payload = {"uid": auth.uid, "email": auth.email}
    return jwt.encode(payload, secret_key, algorithm=algorithm)

def login(email: str, password: str, session):
    """ Login a user """
    auth_user = session.query(Auth).filter(Auth.email == email).first()
    if not auth_user or not verify_password(password, auth_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password incorrect")

    return {"token": generate_token(auth_user)}


######################
#     CRUD
####################
def get_all_information(user=Depends(get_user), session=Depends(get_session)):
    """ Get all information """
    uid = user.get("uid")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db_auth = session.query(Auth).filter(Auth.uid == uid).first()
    if not db_auth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {
        "uid": db_auth.uid,
        "email": db_auth.email
    }


def get_uid(email: str, session=Depends(get_session)) -> str:
    """ Get user uid """
    auth_user = session.query(Auth).filter(Auth.email == email).first()
    if auth_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uid not found")
    return auth_user.uid


def get_password(uid:str, session=Depends(get_session))->str:
    """ Get the hashed password of a user """
    auth_password = session.query(Auth).filter(Auth.uid == uid).first()
    ## password is hash
    if auth_password:
        return auth_password.password
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password not found")


def get_email(uid: str, session=Depends(get_session)) -> str:
    """ Get the email address of a user """
    auth_user = session.query(Auth).filter(Auth.uid == uid).first()
    if auth_user:
        return auth_user.email
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")


def update_email(uid:str , password:str, new_email:str , session=Depends(get_session)) -> str:
    """ Update the email address of a user """
    auth_user = session.query(Auth).filter(Auth.uid == uid).first()

    if not auth_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password, auth_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    if new_email == auth_user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    existing_user = session.query(Auth).filter(Auth.email == new_email).first()
    if existing_user and existing_user.uid != uid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    auth_user.email = new_email
    session.commit()
    session.refresh(auth_user)
    return auth_user.email

def update_password(uid:str , password:str, new_password:str , session=Depends(get_session))-> str:
    """ Update the password of a user """
    auth_user = session.query(Auth).filter(Auth.uid == uid).first()

    if not auth_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password, auth_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password")

    if pdw_context.verify(new_password, auth_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Same password")

    auth_user.password = hash_password(new_password)
    session.commit()
    session.refresh(auth_user)
    return auth_user.password
