from fastapi import APIRouter, Body, Depends, Request, Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.services.auth import (
    get_user, get_email, update_email, update_password, login, logout,
    get_all_information, update_user,
)
from app.settings import schemas
from app.settings.database import get_session

router = APIRouter(prefix="/auth", tags=["Authentification"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me")
def get_user_profile(user=Depends(get_user), session=Depends(get_session)):
    return get_all_information(user, session)


@router.get("/get_email")
def recover_email(uid: str, user=Depends(get_user), session=Depends(get_session)):
    return get_email(uid, session)


@router.post("/login")
@limiter.limit("10/minute")
def log_in(
    request: Request,
    response: Response,
    email: str = Body(),
    password: str = Body(),
    session=Depends(get_session),
):
    return login(email, password, session, response)


@router.post("/logout")
def log_out(response: Response):
    return logout(response)


@router.put("/users/{uid}/email")
def update_user_email(
    uid: str,
    password: str,
    new_email: str,
    user=Depends(get_user),
    session=Depends(get_session),
):
    return update_email(uid, password, new_email, session)


@router.put("/users/{uid}/password")
def update_user_password(
    uid: str,
    password: str,
    new_password: str,
    user=Depends(get_user),
    session=Depends(get_session),
):
    return update_password(uid, password, new_password, session)


@router.put("/users/{uid}/profile")
def update_user_profile(
    uid: str,
    body: schemas.UserUpdate,
    user=Depends(get_user),
    session=Depends(get_session),
):
    return update_user(uid, body, session)
