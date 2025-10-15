from typing import List

from fastapi import Depends
from sqlmodel import Session

from app.models.models import User_Bank_Account as User_Bank_Account_Models, Bank_Account_Info
from app.settings.database import get_session
from app.settings.schemas import User_Bank_Account, Bank_Account
from app.utils.utils import get_user


def create_user_bank_account(body: User_Bank_Account_Models, session = Depends(get_session)) -> User_Bank_Account:
    user_bank_account = User_Bank_Account(**body.model_dump())
    session.add(user_bank_account)

    return user_bank_account


def get_account():
    """ Get information about a specific user bank account """
    
    pass

def get_all_accounts(uid: str,get_user : get_user, session = Depends(get_session)) -> List[Bank_Account_Info]:
    """ Get all information about user bank accounts """
    resultArray = []

    user_bank_accounts = session.query(User_Bank_Account).filter(User_Bank_Account.uid == uid).order_by(User_Bank_Account.creation_date.asc()).all()

    for user_bank_account in user_bank_accounts:
        bank_account = session.query(Bank_Account).filter(Bank_Account.id == user_bank_account.bank_account_id and 
                                                          Bank_Account.is_closed == False).first()
        resultArray.append(Bank_Account_Info(
            id=user_bank_account.id,
            name=user_bank_account.name,
            is_principal=bank_account.is_principal,
            is_closed=bank_account.is_closed,
            creation_date=user_bank_account.creation_date,
            balance=bank_account.balance,
            iban=bank_account.iban,
        ))

    return resultArray

def get_account_id():
    pass

def get_uid(iban : str, session : Session = Depends(get_session)):
    
    account_id = session.query(Bank_Account).filter(Bank_Account.iban == iban).id
    uid = session.query(User_Bank_Account).filter(User_Bank_Account.bank_account_id == account_id).uid
    return uid

def get_name():
    pass


