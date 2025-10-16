from fastapi import APIRouter, Depends

from app.services.user import get_address, get_all, get_first_name, get_last_name, update_address, update_first_name, update_last_name
from app.settings.database import get_session
from app.utils.utils import get_user


router = APIRouter(prefix="/user", tags=["User Management"])

@router.get("/{uid}/all")
def read_all(uid: str, user=Depends(get_user), session=Depends(get_session)):
    return get_all(uid, session)

@router.get("/{uid}/first_name")
def read_first_name(uid: str, user=Depends(get_user), session=Depends(get_session)):
    return get_first_name(uid, session)

@router.get("/{uid}/last_name")
def read_last_name(uid: str, user=Depends(get_user), session=Depends(get_session)):
    return get_last_name(uid, session)

@router.get("/{uid}/address")
def read_address(uid: str, user=Depends(get_user), session=Depends(get_session)):
    return get_address(uid, session)

@router.put("/{uid}/first_name")
def new_first_name(uid: str, password:str, new_first_name: str, user=Depends(get_user), session=Depends(get_session)):
    return update_first_name(uid, password, new_first_name, session)

@router.put("/{uid}/last_name")
def new_last_name(uid: str, password:str, new_last_name: str, user=Depends(get_user), session=Depends(get_session)):
    return update_last_name(uid, password, new_last_name, session)

@router.put("/{uid}/address")
def new_address(uid: str, password:str, new_address: str, user=Depends(get_user), session=Depends(get_session)):
    return update_address(uid, password, new_address, session)

