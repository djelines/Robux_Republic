from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.models import User
from app.services.beneficiary import create_beneficiary as create_beneficiary_service, get_all_beneficiary
from app.settings.database import get_session
from app.models.models import Beneficiary  # Assure-toi que ton schéma est importé

router = APIRouter(prefix="/beneficiaires", tags=["Beneficiaires"])

@router.post("/")
def create_beneficiary_route(body: Beneficiary, session: Session = Depends(get_session)):
    return create_beneficiary_service(body, session=session)

@router.get("/{uid}")
def get_beneficiaries_route(uid:str, session: Session = Depends(get_session)):
    return get_all_beneficiary(uid, session=session)
