from fastapi import Depends
from app.services import user
from app.settings.database import get_session
from app.models.models import Beneficiary
from fastapi import HTTPException as HTTPExpception
from app.services.bank_account import get_account
from sqlalchemy.orm import Session


def create_beneficiary(body: Beneficiary, user_uid: str, session: Session):
    """ Create a new beneficiary """

    # avant de crée un beneficiare il me faut le nom son iban et l'uid de l'user
    # Beneficiaire doit exister dans la base de donnee
    # virifier que l'iban existe et qu'il n'est pas le meme d'un des compte de celui de l'user
    # le beneficaire ne peut pas etre ajouter plus d'une fois par le meme user
    
    beneficiary_name = body.name
    beneficiary_iban = body.iban_to
    user_uid = body.user_uid
    get_account_to = get_account(body.iban_to, session)
    get_account_from = get_account(body.iban_from, session)
    existing_beneficiary = session.query(Beneficiary).filter(Beneficiary.iban_to == beneficiary_iban,Beneficiary.user_uid == user_uid).first()
    
    if not beneficiary_name or not beneficiary_iban:
        raise HTTPExpception(status_code=400, detail="Nom et IBAN du bénéficiaire sont requis")
    if not get_account_to:
        raise HTTPExpception(status_code=404, detail="Compte cible introuvable")
    if get_account_from and get_account_from.iban == beneficiary_iban:
        raise HTTPExpception(status_code=400, detail="Vous ne pouvez pas ajouter votre propre IBAN en tant que bénéficiaire")
    if existing_beneficiary:
        raise HTTPExpception(status_code=400, detail="Ce bénéficiaire existe déjà pour cet utilisateur")

    new_beneficiary = Beneficiary(
        name=beneficiary_name,
        iban_to=beneficiary_iban,
        user_uid=user_uid
    )

    session.add(new_beneficiary)
    session.commit()
    session.refresh(new_beneficiary)

    return new_beneficiary

def get_all_beneficiary(user_uid: str, session: Session = Depends(get_session)):
    """ Get all beneficiaries of a specific user """
    return session.query(Beneficiary).filter(Beneficiary.user_uid == user_uid).all()

def get_beneficiary():
    """ Get information about a specific beneficiary """
    pass

def get_iban_from():
    """ Get the IBAN of the user's account """
    pass

def get_iban_to():
    """ Get the IBAN of the beneficiary's account """

    pass

def delete_beneficiary():
    """ Delete a specific beneficiary """
    pass