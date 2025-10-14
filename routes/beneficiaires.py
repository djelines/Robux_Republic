from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from routes.auth import get_uid
from app.models.models import User
from app.services.beneficiary import create_beneficiary_service
from app.settings.database import get_session
from app.schemas.schemas import Beneficiary  # Assure-toi que ton schéma est importé

router = APIRouter(prefix="/beneficiaires", tags=["Beneficiaires"])

@router.post("/")
def create_beneficiary_route(body: Beneficiary, uid: str = Depends(get_uid), session: Session = Depends(get_session)):
    return create_beneficiary_service(body, user_uid=uid, session=session)

