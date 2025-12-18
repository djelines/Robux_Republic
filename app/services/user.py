from fastapi import Depends, HTTPException
from app.models.models_create import Auth_create
from app.settings.database import get_session
from app.settings.schemas import Auth, User
from app.utils.utils import check_user_password


######################
#     CRUD
######################
message_user = "User not found"

def create_user(body: Auth_create, session=Depends(get_session)) -> User | None:
    """ Create a new user """
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

def get_first_name(uid: str, session=Depends(get_session)):
    """ Get the first name of a user """
    user = session.query(User).filter(User.uid == uid).first()
    if user:
        return user.first_name
    else:
        raise HTTPException(status_code=404, detail=message_user)

def get_last_name(uid: str, session=Depends(get_session)):
    """ Get the last name of a user """
    user = session.query(User).filter(User.uid == uid).first()
    if user:
        return user.last_name
    else:
        raise HTTPException(status_code=404, detail=message_user)

def get_address(uid: str, session=Depends(get_session)):
    """ Get the address of a user """
    user = session.query(User).filter(User.uid == uid).first()
    if user:
        return user.address
    else:
        raise HTTPException(status_code=404, detail=message_user)
    
def update_first_name(uid: str, password:str, new_first_name: str, session=Depends(get_session)):
    """ Update the first name of a user """
    user = session.query(User).filter(User.uid == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail=message_user)
    if not new_first_name or new_first_name.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid first name")
    
    check_user_password(uid, password, session)

    user.first_name = new_first_name
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.first_name

def update_last_name(uid: str, password:str, new_last_name: str, session=Depends(get_session)):
    """ Update the last name of a user """
    user = session.query(User).filter(User.uid == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail=message_user)
    if not new_last_name or new_last_name.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid last name")
    
    check_user_password(uid, password, session)

    user.last_name = new_last_name
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.last_name

def update_address(uid: str, password:str, new_address: str, session=Depends(get_session)):
    """ Update the address of a user """
    user = session.query(User).filter(User.uid == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail=message_user)
    if not new_address or new_address.strip() == "":
        raise HTTPException(status_code=400, detail="Invalid address")
    
    check_user_password(uid, password, session)

    user.address = new_address
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.address

