from fastapi import APIRouter, Depends

from app.models.models import Auth
from app.services.auth import create_user, get_uid, get_password, get_email, update_email, update_password, login, \
    get_user, get_all_information
from app.settings import schemas
from app.settings.database import get_session

router = APIRouter(prefix="/auth", tags=["Authentification"])

@router.post("/signup", response_model=schemas.Auth)
def sign_up(body:Auth, session = Depends(get_session)):
    return create_user(body, session)

@router.post("/login")
def log_in(email: str, password :str , session=Depends(get_session)):
    return login(email, password, session)


@router.get("/get_uid")
def recover_uid(email: str, session=Depends(get_session)):
    return get_uid(email, session)

@router.get("/me")
def me(user=Depends(get_user), session=Depends(get_session)):
    return get_all_information(user, session)


@router.get("/get_password")
def recover_password(uid: str, user = Depends(get_user), session=Depends(get_session)):
    return get_password(uid, session)

@router.get("/get_email")
def recover_email(uid: str, user = Depends(get_user), session=Depends(get_session)):
    return get_email(uid, session)

@router.put("/users/{uid}/email")
def update_user_email(uid: str, password: str, new_email: str, user = Depends(get_user), session=Depends(get_session)):
    return update_email(uid, password, new_email, session)

@router.put("/users/{uid}/password")
def update_user_password(uid: str, password: str, new_password: str, user = Depends(get_user), session=Depends(get_session)):
    return update_password(uid, password, new_password, session)
