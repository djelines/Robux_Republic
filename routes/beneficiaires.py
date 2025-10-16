from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.models import User
from app.services.beneficiary import create_beneficiary as create_beneficiary_service, delete_beneficiary, get_all_beneficiary, get_beneficiary, get_iban_to
from app.settings.database import get_session
from app.models.models import Beneficiary
from app.utils.utils import get_user  # Assure-toi que ton schéma est importé

router = APIRouter(prefix="/beneficiaires", tags=["Beneficiaires"])



@router.get("/all-beneficiaries")
def get_beneficiaries_route(session: Session = Depends(get_session),get_user: dict = Depends(get_user),):
    return get_all_beneficiary(get_user, session)

@router.get("/beneficiary/{iban_to}")
def get_one_beneficiary_route(iban_to: str, session: Session = Depends(get_session), get_user: dict = Depends(get_user)):
    return get_beneficiary(get_user, iban_to, session=session)

@router.get("/{beneficiary_name}")
def get_iban_to_route(beneficiary_name: str, session: Session = Depends(get_session), get_user: dict = Depends(get_user)):
    return get_iban_to(beneficiary_name, session=session)

@router.post("/")
def create_beneficiary_route(body: Beneficiary, session: Session = Depends(get_session), get_user: dict = Depends(get_user)):
    return create_beneficiary_service(body, session=session, get_user=get_user)

@router.delete("/{iban}")
def delete_beneficiary_route(iban: str, session: Session = Depends(get_session), get_user: dict = Depends(get_user)):
    return delete_beneficiary(iban, session=session, get_user=get_user)