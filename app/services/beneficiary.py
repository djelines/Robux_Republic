from fastapi import Depends, HTTPException
from app.services import user
from app.services.user_bank_account import get_all_accounts
from app.settings.database import get_session
from app.settings.schemas import Beneficiary as Beneficiary_SQLModel
from fastapi import HTTPException as HTTPExpception
from app.services.bank_account import get_account
from sqlalchemy.orm import Session
from app.services.user import get_all
from app.utils.utils import get_user


######################
#     CRUD
######################
def create_beneficiary(body: Beneficiary_SQLModel, session: Session , get_user: get_user):
    """ Create a new beneficiary """
    
    beneficiary_name = body.name
    beneficiary_iban = body.iban_to
    user_uid = body.uid
    get_account_to = get_account(body.iban_to, get_user, session=session)
    
    all_bank_acounts = get_all_accounts(user_uid, "", get_user, session=session)
    
    existing_beneficiary = session.query(Beneficiary_SQLModel).filter(Beneficiary_SQLModel.iban_to == beneficiary_iban,Beneficiary_SQLModel.uid == user_uid).first()
    
    if not beneficiary_name or not beneficiary_iban:
        raise HTTPExpception(status_code=400, detail="Nom et IBAN du bénéficiaire sont requis")
    if not get_account_to:
        raise HTTPExpception(status_code=404, detail="Compte cible introuvable")
    if beneficiary_iban in all_bank_acounts:
        raise HTTPExpception(status_code=400, detail="Vous ne pouvez pas ajouter votre propre IBAN en tant que bénéficiaire")
    if not (get_all(user_uid, session)):
        raise HTTPExpception(status_code=404, detail="Utilisateur introuvable")
    for account in all_bank_acounts:
        if account.iban == beneficiary_iban:
            raise HTTPExpception(status_code=400, detail="You cant add your own IBAN")
    if existing_beneficiary:
        raise HTTPExpception(status_code=400, detail="Ce bénéficiaire existe déjà pour cet utilisateur")

    new_beneficiary = Beneficiary_SQLModel(
        name=beneficiary_name,
        iban_to=beneficiary_iban,
        uid= get_user.get("uid")
    )

    session.add(new_beneficiary)
    session.commit()
    session.refresh(new_beneficiary)

    return new_beneficiary

def get_all_beneficiary(get_user: get_user, session: Session = Depends(get_session)):
    """ Get all beneficiaries of a specific user """
    user_uid = get_user.get("uid")
    beneficiaries = session.query(Beneficiary_SQLModel).filter(Beneficiary_SQLModel.uid ==user_uid).all()
    if not beneficiaries:
        raise HTTPException(status_code=404, detail="No beneficiaries exists")

    return beneficiaries

def get_beneficiary(get_user: get_user, iban_to:str , session: Session = Depends(get_session)):
    """ Get information about a specific beneficiary """
    user_uid = get_user.get("uid")
    beneficiary = session.query(Beneficiary_SQLModel).filter(Beneficiary_SQLModel.iban_to == iban_to, Beneficiary_SQLModel.uid == user_uid).first()
    if not beneficiary:
        raise HTTPExpception(status_code=404, detail="Bénéficiaire introuvable pour cet utilisateur")
    return beneficiary


def get_iban_to(beneficiary_name: str, session: Session = Depends(get_session)):
    """ Get the IBAN of the beneficiary's account """
    iban_to = session.query(Beneficiary_SQLModel).filter(Beneficiary_SQLModel.name == beneficiary_name).first()
    if not iban_to:
       raise HTTPException(status_code=404, detail=f"Bénéficiaire '{beneficiary_name}' introuvable")
    return {"iban_to": iban_to.iban_to}

def delete_beneficiary(iban_to: str, get_user: get_user, session: Session = Depends(get_session)):
    """ Delete a specific beneficiary """
    user_uid = get_user.get("uid")
    beneficiary = session.query(Beneficiary_SQLModel).filter(Beneficiary_SQLModel.iban_to == iban_to, Beneficiary_SQLModel.uid == user_uid).first()
    if not beneficiary:
        raise HTTPExpception(status_code=404, detail="Bénéficiaire introuvable pour cet utilisateur")
    
    session.delete(beneficiary)
    session.commit()
    return {"detail":f"Bénéficiaire {iban_to} supprimé avec succès"}

