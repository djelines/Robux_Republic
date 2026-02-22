from datetime import datetime, timedelta, timezone

from starlette import status
from sqlmodel import select

from app.models.models_create import Auth_create
from app.services.user import create_user
from app.settings import schemas
from app.settings.config import ALGORITHM, SECRET_KEY, IS_PROD
from app.settings.database import get_session
from app.utils.utils import (
    generate_uid, hash_password, verify_password, get_user, pdw_context,
    COOKIE_NAME, TOKEN_EXPIRE_DAYS
)
import jwt
import uuid
from fastapi import Depends, HTTPException, Response
from app.models.models import User, Auth
from app.settings.schemas import Auth, User


######################
#     Sign up
####################
def create_auth(body: Auth_create, session = Depends(get_session)) -> dict:
    """ Create authentication credentials for a user """
    
    existing_user = session.query(Auth).filter(Auth.email == body.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    user_uid = body.uid if body.uid else str(uuid.uuid4())
    
    new_user = User(
        uid=user_uid, 
        first_name=body.first_name, 
        last_name=body.last_name, 
        address=body.address
    )
    session.add(new_user)
    
    session.flush() 

    new_auth = Auth(
        uid=user_uid, 
        email=body.email, 
        password=hash_password(body.password)
    )
    session.add(new_auth)
    
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
def generate_token(auth: Auth) -> str:
    """ Generate a JWT token with expiry """
    exp = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {"uid": auth.uid, "email": auth.email, "exp": exp}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def login(email: str, password: str, session, response: Response):
    """ Login a user — sets httpOnly cookie """
    auth_user = session.query(Auth).filter(Auth.email == email).first()
    if not auth_user or not verify_password(password, auth_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )

    token = generate_token(auth_user)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="strict",
        secure=IS_PROD,
        max_age=TOKEN_EXPIRE_DAYS * 86400,
    )

    db_user = session.query(User).filter(User.uid == auth_user.uid).first()
    return {
        "uid": auth_user.uid,
        "email": auth_user.email,
        "first_name": db_user.first_name if db_user else None,
        "last_name": db_user.last_name if db_user else None,
        "address": db_user.address if db_user else None,
    }

def logout(response: Response):
    """ Clear the auth cookie """
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        samesite="strict",
        secure=IS_PROD,
    )
    return {"message": "Déconnecté"}


######################
#     CRUD
####################
def get_all_information(user=Depends(get_user), session=Depends(get_session)):
    """ Get all information about a user """
    uid = user.get("uid")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    

    # Join Auth and User tables to get all information
    db_auth = session.query(Auth).filter(Auth.uid == uid).first()
    if not db_auth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_user = session.query(User).filter(User.uid == uid).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    
    return {
        "uid": db_auth.uid,
        "email": db_auth.email,
        "first_name": db_user.first_name,
        "last_name": db_user.last_name,
        "address": db_user.address,
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

def update_user(uid: str, body: schemas.UserUpdate, session=Depends(get_session)) -> User:
    db_user = session.query(User).filter(User.uid == uid).first()
    db_auth = session.query(Auth).filter(Auth.uid == uid).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in body.dict(exclude_unset=True).items():
        
        if hasattr(db_user, key):
            setattr(db_user, key, value)
        
        if hasattr(db_auth, key):
            setattr(db_auth, key, value)

    session.commit()
    session.refresh(db_user)
    return db_user


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
