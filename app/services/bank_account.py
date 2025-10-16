from app.models.models_create import Bank_Account_create
from app.services import user_bank_account
from app.services.user_bank_account import create_user_bank_account, get_all_accounts, get_uid, \
    get_all_bank_account_sql, get_bank_id
from app.settings.schemas import Bank_Account as Bank_Account_SQLModel
from app.models.models import Bank_Account as Bank_AccountModel, Bank_Account
from app.settings.schemas import User_Bank_Account
from app.settings.database import get_session
from fastapi import Depends, HTTPException

from app.utils.utils import generate_iban, get_user


def create_bank_account(body: Bank_Account_create, get_user: get_user, session=Depends(get_session)):
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

    user_bank_account = create_user_bank_account(User_Bank_Account(bank_account_id=bank_account.id, name=body.name, uid=body.uid , bank_id=get_bank_id(session)), session)

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

def get_account(iban: str , session:Depends(get_session)) -> Bank_Account:
    return session.query(Bank_Account_SQLModel).filter(Bank_Account_SQLModel.iban == iban).first()

def get_is_principal():
    """ Check if the bank account is a principal account """
    pass

def get_is_closed():
    """ Check if the bank account is closed """
    pass

def close_account(iban: str, get_user: get_user, session=Depends(get_session)):
    """ Close the bank account """

    # transférer l'argent sur le compte principale
    # change le boolean is_closed
    from app.services.transaction import get_all_transaction

    
    bank_account = get_account(iban , session)
    transactions = get_all_transaction(iban, get_user, session)
    all_account = get_all_bank_account_sql(get_uid(iban, session), get_user, session)

    principal_bank_account = {}

    for transaction in transactions:
        if transaction["status"] == "pending":
            raise HTTPException(status_code=400 , detail="Pending transaction")  
    if bank_account.is_principal:
        raise HTTPException(status_code=400 , detail="Account is principal")
    if bank_account.is_closed:
        raise HTTPException(status_code=400 , detail="Account is closed")

    if bank_account.balance >=0.0:
        for account in all_account:
            if account.is_principal:
                account.balance += bank_account.balance
                bank_account.balance = 0
                bank_account.is_closed = True
                principal_bank_account = account

                session.commit()
                session.refresh(bank_account)
                session.refresh(account)
        
    if bank_account.is_closed == False:
        raise HTTPException(status_code=400 , detail="No principal account found")

    return {
        "closed_bank_account": bank_account,
        "principal_bank_account": principal_bank_account

    }



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

def get_bank_account_id(iban : str, session=Depends(get_session)) -> int:
    return session.query(Bank_Account.id).filter(Bank_Account.iban == iban).first().scalar()