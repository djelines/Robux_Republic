from app.models.models_create import Bank_Account_create
from app.services.user_bank_account import create_user_bank_account
from app.settings.schemas import Bank_Account as Bank_Account_SQLModel
from app.models.models import Bank_Account as Bank_AccountModel, Bank_Account
from app.settings.schemas import User_Bank_Account
from app.settings.database import get_session
from fastapi import Depends

from app.utils.utils import generate_iban


def create_bank_account(body: Bank_Account_create = None, session = Depends(get_session)):
    """ Create a new bank account """


    if body is None or body.uid is None or body.name is None:
        return {
            "error": "Valeurs manquantes incomplet"
        }

    body.bank_account_id = None
    body.iban = generate_iban()

    bank_account = Bank_Account_SQLModel(**body.model_dump())
    session.add(bank_account)
    session.flush()

    user_bank_account = create_user_bank_account(User_Bank_Account(bank_account_id=bank_account.id, name=body.name, uid=body.uid), session)

    session.commit()
    session.refresh(bank_account)
    session.refresh(user_bank_account)

    return {
        "bank_account": bank_account,
        "user_bank_account": user_bank_account
    }

def get_all():
    """ Get all information about bank accounts """
    pass

def get_account(iban: str , session=Depends(get_session)) -> Bank_Account:
    return session.query(Bank_Account_SQLModel).filter(Bank_Account_SQLModel.iban == iban).first()

def get_is_principal():
    """ Check if the bank account is a principal account """
    pass

def get_is_closed():
    """ Check if the bank account is closed """
    pass

def get_iban():
    """ Get the IBAN of the bank account """
    pass

def get_balance():
    """ Get the solde of the bank account """
    pass

def update_is_closed():
    """ Update the closed status of the bank account and related user bank accounts """
    pass

def update_balance():
    """ Update the balance of the bank account """
    pass