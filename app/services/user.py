from fastapi import Depends
from app.models.models_create import Auth_create
from app.settings.database import get_session
from app.settings.schemas import Auth, User


def create_user(body: Auth_create, session=Depends(get_session)) -> User | None:
    new_user = User(**body.model_dump())
    session.add(new_user)
    
    if new_user:
        return new_user
    return None

def get_all(uid: str, session=Depends(get_session)):
    """ Get all information about users """
    user = session.query(User).filter(User.uid == uid).first()
    print("Get all users", user)
    print("Get all users", uid)
    if user:
        return user

def get_first_name():
    pass

def get_last_name():
    pass

def get_address():
    pass

def update_first_name():
    pass

def update_last_name():
    pass

def update_address():
    pass

